import json
from typing import Dict, List
from utils.data_processor import load_json, save_json
from utils.java import get_java_standard_method_name
from utils.logger import logger
from config import (
    ALL_METAINFO_PATH,
    RESOLVED_METAINFO_PATH,
    FUNCTION_METAINFO_PATH,
    STRUCT_METAINFO_PATH,
    TESTCASE_METAINFO_PATH,
    CUSTOMIZED_TESTCODE_PATH
)
from metainfo.model import Function, Struct, CTestcase, File, FunctionSignature


class CMetaInfoBuilder():
    """
    for C, method denotes function and class denotes struct,
    so I didn't use the super class MetaInfoBuilder
    """

    def __init__(self, metainfo_json_path: str = ALL_METAINFO_PATH,
                 resolved_metainfo_path: str = RESOLVED_METAINFO_PATH):
        self.metainfo_json_path = metainfo_json_path
        self.metainfo = self.load_metainfo()
        self.resolved_metainfo_path = resolved_metainfo_path
        self.functions: List[Function] = []
        self.structs: List[Struct] = []
        self.testcases: List[CTestcase] = []
        self.files: List[File] = []

    def load_metainfo(self):
        with open(self.metainfo_json_path) as f:
            metainfo = json.load(f)

        return metainfo

    def save_metainfo(self, path_to_data: Dict[str, List[Dict]]):
        def save_data(file_path, data):
            save_json(file_path, [item.to_json() for item in data])

        for path, data in path_to_data.items():
            save_data(path, data)

        logger.info("save metainfo success!")

    def save(self):
        path_to_data = {
            FUNCTION_METAINFO_PATH: self.functions,
            TESTCASE_METAINFO_PATH: self.testcases,
            STRUCT_METAINFO_PATH: self.structs,
        }
        self.save_metainfo(path_to_data)

    # def resolve_file_imports(self, file_imports_path=FILE_IMPORTS_PATH):
    #     file_imports = {}
    #     for file in self.metainfo:
    #         file_imports[file['relative_path']] = file['contexts']
    #
    #     save_json(file_imports_path, file_imports)
    #     logger.info(f"Saved file imports to {file_imports_path}")

    def get_standard_function_name(self, function: Function):
        return f'[{function.return_type}]' + function.name + \
            '(' + ','.join([param['type'] for param in function.params]) + ')'

    @staticmethod
    def is_testcase(file):
        """
        Check if a file is a testcase file
        """
        for path in CUSTOMIZED_TESTCODE_PATH:
            if path in file['relative_path']:
                return True

        c_unit_test_frameworks = [
            'unity.h',
            'CUnit/CUnit.h',
            'CUnit/Basic.h',
            # 'check.h',
        ]
        for context in file['contexts']:
            if any([framework in context for framework in c_unit_test_frameworks]):
                return True

    def build_metainfo(self):
        for file in self.metainfo:
            file_path = file['relative_path']
            #   for C, 'classes' denotes 'structs'
            for struct in file['classes']:
                _struct = Struct(
                    uris=file_path + '.' + struct['name'],
                    name=struct['name'],
                    file_path=file_path,
                    fields=struct['attributes']['fields'],
                    struct_docstring=struct['docstring'],
                    original_string=struct['original_string'],
                )
                self.structs.append(_struct)

            if self.is_testcase(file):
                for function in file['methods']:
                    _testcase = CTestcase(
                        uris=FunctionSignature(
                            file_path=file_path,
                            function_name=function['name'],
                            params=function['parameters'],
                            return_type=function['attributes']['return_type'],
                        ).unique_name(),
                        name=function['name'],
                        arg_nums=len(function['parameters']),
                        params=function['parameters'],
                        signature=get_java_standard_method_name(
                            function['name'],
                            function['parameters'],
                            function['attributes']['return_type']
                        ),
                        original_string=function['original_string'],
                        default_arguments=None, # C has no default arguments
                        file=file_path,
                        attributes=function['attributes'],
                        docstring=function['docstring'],
                        return_type=function['attributes']['return_type'],
                    )
                    self.testcases.append(_testcase)
            else:
                for function in file['methods']:
                    _function = Function(
                        uris=FunctionSignature(
                            file_path=file_path,
                            function_name=function['name'],
                            params=function['parameters'],
                            return_type=function['attributes']['return_type'],
                        ).unique_name(),
                        name=function['name'],
                        arg_nums=len(function['parameters']),
                        params=function['parameters'],
                        signature=get_java_standard_method_name(
                            function['name'],
                            function['parameters'],
                            function['attributes']['return_type']
                        ),
                        original_string=function['original_string'],
                        default_arguments=None, # C has no default arguments
                        file=file_path,
                        attributes=function['attributes'],
                        docstring=function['docstring'],
                        return_type=function['attributes']['return_type'],
                    )
                    self.functions.append(_function)


