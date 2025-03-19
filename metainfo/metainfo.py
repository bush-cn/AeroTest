from typing import List

from metainfo.c_metainfo_builder import CMetaInfoBuilder
from metainfo.metainfo_builder import MetaInfoBuilder
from parser.tree_sitter_query_parser import extract_identifiers
from utils.data_processor import load_class_metainfo, load_file_imports_metainfo, load_json, load_method_metainfo, \
    load_packages_metainfo, load_testcase_metainfo
import config
from utils.logger import logger


class MetaInfo:
    """
    暂时没有维护之前的Java和Python适配了，只保留处理C的部分代码，后面如需合并可简单修改即可。
    """
    struct_metainfo_path = config.STRUCT_METAINFO_PATH
    function_metainfo_path = config.FUNCTION_METAINFO_PATH
    testcase_metainfo_path = config.TESTCASE_METAINFO_PATH
    language_mode = config.LANGUAGE_MODE

    def __init__(self) -> None:
        self.testcase_metainfo = load_json(self.testcase_metainfo_path)
        self.struct_metainfo = load_json(self.struct_metainfo_path)
        self.function_metainfo = load_json(self.function_metainfo_path)

    def get_function(self, uri):
        for function in self.function_metainfo:
            if uri == function["uris"]:
                return function

    def get_struct(self, uri):
        for struct in self.struct_metainfo:
            if uri == struct["uris"]:
                return struct

    def get_includes(self, file_path) -> List[str]:
        return self.file_imports_metainfo.get(file_path)

    def get_testcase(self, uri):
        for testcase in self.testcase_metainfo:
            if testcase["uris"] == uri:
                return testcase

    def get_struct_montage(self, _struct, use_doc=False):
        """Now we only pack the fields and method signature"""
        # logger.info(f"Get montage of {_class['name']}.")
        # TODO: attribute_expression是？我这里用的是original_string代替
        if not use_doc:
            return {
                "struct_name": _struct['name'],
                "fields": [field['original_string'] for field in _struct['fields']]
            }
        else:
            return {
                "struct_name": _struct['name'],
                "struct_doc": _struct['struct_docstring'],
                "fields": [field['original_string'] + " # " + field["docstring"] for field in _struct['fields']]
            }  # 这里加了一个#，用于分隔字段和字段注解

    def get_metainfo_or_none(self, name, file_name, metadata):
        res = []
        for item in metadata:
            if item['name'] == name:
                res.append(item)

        if len(res) > 1:
            logger.warning(f"Found {len(res)} items with the same name {name}.")
            for item in res:
                if item['file'] == file_name:
                    logger.info(f"Found the item {item['name']} in file {file_name}")
                    return item

        return res[0] if len(res) > 0 else None

    def get_struct_or_none(self, struct_name, file_name):
        return self.get_metainfo_or_none(struct_name, file_name, self.struct_metainfo)

    def get_function_or_none(self, function_name, file_name):
        return self.get_metainfo_or_none(function_name, file_name, self.function_metainfo)


def run_build_metainfo(builder: CMetaInfoBuilder):
    logger.info('run_build_metainfo start.')
    builder.build_metainfo()
    builder.save()

    #   TODO: 这里代码没看懂，C应该不需要package、brother、interface？

    logger.info('resolve file imports(includes) for C start...')
    builder.resolve_file_imports(file_imports_path=config.FILE_IMPORTS_PATH)
    logger.info('resolve file imports(includes) for C start...')

    logger.info('run_build_metainfo Done!')

