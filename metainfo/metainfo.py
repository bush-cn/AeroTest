from typing import List

from metainfo.c_metainfo_builder import CMetaInfoBuilder
from utils.data_processor import load_json
import config
from utils.logger import logger


class MetaInfo:
    """
    暂时没有维护之前的Java和Python适配了，只保留处理C的部分代码，后面如需合并可简单修改即可。
    """
    udt_metainfo_path = config.UDT_METAINFO_PATH
    function_metainfo_path = config.FUNCTION_METAINFO_PATH
    testcase_metainfo_path = config.TESTCASE_METAINFO_PATH
    global_variable_metainfo = config.GLOBAL_VARIABLE_METAINFO_PATH
    language_mode = config.LANGUAGE_MODE

    def __init__(self) -> None:
        self.testcase_metainfo = load_json(self.testcase_metainfo_path)
        self.udt_metainfo = load_json(self.udt_metainfo_path)
        self.function_metainfo = load_json(self.function_metainfo_path)
        self.global_variable_metainfo = load_json(self.global_variable_metainfo)

    def get_function(self, name, file):
        """
        name: 函数名
        file: 所需要检索的代码所在文件
        返回值：函数的元信息
        根据函数名和文件名获取函数的元信息。只有static声明的函数才会重名，此时在本文件中查找。
        若未找到，返回None。
        """
        result = self.function_metainfo.get(name)
        if result is None or len(result) == 0:
            logger.warning(f"Function {name} not found.")
            return None
        elif len(result) == 1:
            return result[0]
        else:
            logger.warning(f"Function {name} has more than one definition.")
            for item in result:
                if item['file'] == file:
                    logger.info(f"Found the function {name} in file {file}.")
                    return item
            return None

    def get_udt(self, name) -> List:
        """
        name: 类型名
        返回值：类型的元信息

        只有UDT是一对一不存在重名。若查找到typedef，递归查找其真实类型。
        且查找过程中的define链也需要保存，最终将全部的源字符串提供给LLM。
        """
        results = []
        result = self.udt_metainfo.get(name)
        if result is None:
            results.append(result)
        while result is not None and result['typedef'] and result['typedef'] in self.udt_metainfo:
            result = self.udt_metainfo.get(result['typedef'])
            results.append(result)
        return results


    def get_global_variable(self, name, file):
        """
        name: 全局变量名
        file: 所需要检索的代码所在文件
        返回值：全局变量的元信息
        """
        result = self.global_variable_metainfo.get(name)
        if result is None or len(result) == 0:
            logger.warning(f"Global variable {name} not found.")
            return None
        elif len(result) == 1:
            return result[0]
        else:
            logger.warning(f"Global variable {name} has more than one definition.")
            for item in result:
                if item['file'] == file:
                    logger.info(f"Found the global variable {name} in file {file}.")
                    return item
            return None


    def get_testcase(self, name, file):
        return self.get_function(name, file)


def run_build_metainfo(builder: CMetaInfoBuilder):
    logger.info('run_build_metainfo start.')
    builder.build_metainfo()
    builder.save()
    logger.info('run_build_metainfo Done!')

