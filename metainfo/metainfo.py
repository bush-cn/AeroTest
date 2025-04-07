from typing import List

from metainfo.c_metainfo_builder import CMetaInfoBuilder
from utils.data_processor import load_json
from config import global_config
from utils.logger import logger


class MetaInfo:
    """
    暂时没有维护之前的Java和Python适配了，只保留处理C的部分代码，后面如需合并可简单修改即可。
    """
    udt_metainfo_path = global_config['UDT_METAINFO_PATH']
    function_metainfo_path = global_config['FUNCTION_METAINFO_PATH']
    testcase_metainfo_path = global_config['TESTCASE_METAINFO_PATH']
    global_variable_metainfo = global_config['GLOBAL_VARIABLE_METAINFO_PATH']
    language_mode = global_config['LANGUAGE_MODE']

    def __init__(self) -> None:
        self.testcase_metainfo = load_json(self.testcase_metainfo_path)
        self.udt_metainfo = load_json(self.udt_metainfo_path)
        self.function_metainfo = load_json(self.function_metainfo_path)
        self.global_variable_metainfo = load_json(self.global_variable_metainfo)

    def get_function(self, *args):
        """
        当参数为1个时，使用uris查找
        当参数为2个时，使用函数名+文件名查找，首选函数名匹配，若有多个则使用文件名区分
        """
        if len(args) == 1:  # 使用uris查找
            return self.function_metainfo.get(args[0])
        elif len(args) == 2:  # 使用文件名和函数名查找，首选第一个参数函数名，次选文件名
            results = []
            for k, v in self.function_metainfo.items():
                if v['name'] == args[0]:
                    results.append(v)
            if len(results) == 1:
                return results[0]
            elif len(results) > 1:
                logger.warn(f'find {len(results)} functions with name {args[0]}')
                for r in results:
                    if r['file'] == args[1]:
                        return r
        return None

    def get_udt(self, name) -> List:
        """
        name: 类型名
        返回值：类型的元信息

        只有UDT是一对一不存在重名。若查找到typedef，递归查找其真实类型。
        查找过程中的define链以及内部类型也需要保存，最终将全部的源字符串提供给LLM。
        若查找不到返回空列表。
        """
        results = []
        result = self.udt_metainfo.get(name)
        if result is not None:
            results.append(result)
        while result is not None and result['typedef'] and result['typedef'] in self.udt_metainfo:
            result = self.udt_metainfo.get(result['typedef'])
            results.append(result)
        # 最后当前result是真实类型，递归查找其内部类型
        if result is not None and result['inner_types']:
            for inner_type in result['inner_types']:
                results.extend(self.get_udt(inner_type))
        return results

    def get_global_variable(self, *args):
        """
        当参数为1个时，使用uris查找
        当参数为2个时，使用函数名+文件名查找，首选函数名匹配，若有多个则使用文件名区分
        """
        if len(args) == 1:  # 使用uris查找
            return self.global_variable_metainfo.get(args[0])
        elif len(args) == 2:  # 使用文件名和函数名查找，首选第一个参数函数名，次选文件名
            results = []
            for k, v in self.global_variable_metainfo.items():
                if v['name'] == args[0]:
                    results.append(v)
            if len(results) == 1:
                return results[0]
            elif len(results) > 1:
                logger.warn(f'find {len(results)} functions with name {args[0]}')
                for r in results:
                    if r['file'] == args[1]:
                        return r
        return None

    def get_testcase(self, *args):
        return self.get_function(args)


def run_build_metainfo(builder: CMetaInfoBuilder):
    logger.info('run_build_metainfo start.')
    builder.build_metainfo()
    builder.save()
    logger.info('run_build_metainfo Done!')
