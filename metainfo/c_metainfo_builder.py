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
from metainfo.model import Function, UDT, CTestcase, GlobalVariable


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
            UDT_METAINFO_PATH: self.data_to_dict(self.udts),
            GLOBAL_VARIABLE_METAINFO_PATH: self.data_to_dict(self.global_variables)
        }

        for path, data in path_to_data.items():
            save_json(path, data)

        logger.info("save metainfo success!")

    @staticmethod
    def data_to_dict(data: List[Function | UDT | CTestcase | GlobalVariable]) -> Dict:
        # 为了提高查询速度，将列表形式的metainfo转换为字典形式，以uri为key
        _dict = {}
        for item in data:
            _dict[item.uris] = item.to_json()
        return _dict

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
                    uris=udt['name'],   # UDT name is unique among all files
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
                    type=global_var['type'],
                    file=file_path,
                    docstring=global_var['docstring'],
                    original_string=global_var['original_string'],
                )
                self.global_variables.append(_global_var)

            if self.is_testcase(file):
                for function in file['methods']:
                    _testcase = CTestcase(
                        uris=file_path + '.' + function['name'],
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
                        uris=file_path + '.' + function['name'],
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

