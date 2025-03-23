import json
from typing import Dict, List
from utils.data_processor import load_json, save_json
from utils.java import get_java_standard_method_name
from utils.logger import logger
from config import (
    ALL_METAINFO_PATH,
    RESOLVED_METAINFO_PATH,
    FUNCTION_METAINFO_PATH,
    UDT_METAINFO_PATH,
    TESTCASE_METAINFO_PATH,
    GLOBAL_VARIABLE_METAINFO_PATH,
    CUSTOMIZED_TESTCODE_PATH,
)
from metainfo.model import Function, UDT, CTestcase, FunctionSignature, GlobalVariable


class CMetaInfoBuilder:

    def __init__(self, metainfo_json_path: str = ALL_METAINFO_PATH,
                 resolved_metainfo_path: str = RESOLVED_METAINFO_PATH):
        self.metainfo_json_path = metainfo_json_path
        self.metainfo = load_json(self.metainfo_json_path)
        self.resolved_metainfo_path = resolved_metainfo_path
        self.functions: List[Function] = []
        self.udts: List[UDT] = []
        self.testcases: List[CTestcase] = []
        self.global_variables: List[GlobalVariable] = []


    def save(self):
        path_to_data = {
            FUNCTION_METAINFO_PATH: self.data_to_dict(self.functions),
            TESTCASE_METAINFO_PATH: self.data_to_dict(self.testcases),
            UDT_METAINFO_PATH: self.data_to_dict(self.udts, duplicate=False),
            GLOBAL_VARIABLE_METAINFO_PATH: self.data_to_dict(self.global_variables)
        }

        for path, data in path_to_data.items():
            save_json(path, data)

        logger.info("save metainfo success!")

    @staticmethod
    def data_to_dict(data: List[Function | UDT | CTestcase | GlobalVariable], duplicate=True) -> Dict:
        # 为了提高查询速度，将列表形式的metainfo转换为字典形式
        # 因为有可能用static关键字修饰的函数、全局变量可以重名，所以用列表存储（UDT不会重名）
        if not duplicate:
            return {item.name: item.to_json() for item in data}

        _dict = {}
        for item in data:
            name = item.name
            if name in _dict:
                _dict[name].append(item.to_json())  # 如果已存在，追加到列表中
            else:
                _dict[name] = [item.to_json()]  # 如果不存在，创建新列表
        return _dict

    # def resolve_file_imports(self, file_imports_path=FILE_IMPORTS_PATH):
    #     file_imports = {}
    #     for file in self.metainfo:
    #         file_imports[file['relative_path']] = file['contexts']
    #
    #     save_json(file_imports_path, file_imports)
    #     logger.info(f"Saved file imports to {file_imports_path}")

    # def get_standard_function_name(self, function: Function):
    #     return f'[{function.return_type}]' + function.name + \
    #         '(' + ','.join([param['type'] for param in function.params]) + ')'

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
        for file_path, file in self.metainfo.items():
            #   for C, 'classes' denotes 'structs'
            for udt in file['classes']:
                _udt = UDT(
                    uris=file_path + '.' + udt['name'],
                    name=udt['name'],
                    file=file_path,
                    # fields=struct['attributes']['fields'],
                    udt_docstring=udt['docstring'],
                    original_string=udt['original_string'],
                    typedef=udt['typedef'] if 'typedef' in udt else None,
                )
                self.udts.append(_udt)

            for global_var in file['global_variables']:
                _global_var = GlobalVariable(
                    uris=file_path + '.' + global_var['name'],
                    name=global_var['name'],
                    file=file_path,
                    docstring=global_var['docstring'],
                    original_string=global_var['original_string'],
                )
                self.global_variables.append(_global_var)

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

