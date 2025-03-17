

from abc import ABC, abstractmethod

from typing import Dict, List, Set, Tuple
from metainfo.model import Class, Method, TestCase
from utils.data_processor import load_json
from utils.logger import logger


class FileLevelContextType:
    """我们定义这个类，为了区分Java和Python
    对于Java来说，一般情况下一个文件中只有一个类，
    We define this Class to distinguish between Java and Python.
    For Java, generally, one file only contains one class, context searching is in the same class.
    But for python, we searching in the same file."""

class FileLevel(FileLevelContextType):
    pass

class ClassLevel(FileLevelContextType):
    pass


class Finds:
    """
    用于存储查找结果的类。
    
    Attributes:
        field_finds (list): 存储在类字段中的查找结果。
        method_finds (list): 存储在类方法中的查找结果。
        all_finds (list): 所有查找结果的汇总。
    """
    def __init__(self):
        self.find_in_fileds = []
        self.find_in_methods = []
        self.class_finds = []
        self.record_finds = []
        self.interface_finds = []


class StaticContextRetrieval(ABC):
    def __init__(self, std_lib_path, keywords_and_builtin_path):
        self.std_lib_path = std_lib_path
        self.keywords_and_builtin_path = keywords_and_builtin_path
        self.std_lib = self.load_std_lib()
        self.keywords_and_builtin = self.load_keywords_and_builtin()
        self.class_map = {cls['name']: cls for cls in self.class_metainfo}

    def load_std_lib(self) -> List[str]:
        pass

    def load_keywords_and_builtin(self):
        pass
    
    def pack_package_info(self, unresolved_refs, file_path, original_string):
        pass
    
    def pack_repo_info(self, unresolved_refs, imports):
        pass
    
    def pack_package_info_use_dot(self, unresolved_refs, file_path, original_string):
        pass
    
    @abstractmethod
    def pack_method_class_info(self, method: Dict, is_montage=False) -> str:
        pass
    
    def prune_class(self, _class, method_names=None, save_constructors=True):
        pass
    
    def pack_pruned_class_description(self, pruned_class):
        pass
    
    def pack_repo_info_use_dot(self, unresolved_refs, original_string, imports):
        pass
    
    @abstractmethod
    def pack_method_file_level_context(self, method: Method):
        pass
    
    @abstractmethod
    def pack_testcase_file_level_context(self, testcase: TestCase):
        pass
    
    @abstractmethod
    def find_file_level_context(self, code_block, where, language='python') -> Tuple[Finds, Set]:
        pass
    
    @abstractmethod
    def get_inherited_methods(self, cls_name) -> Dict[str, List[str]]:
        pass
    
    @abstractmethod
    def get_methods_original_string(self, class_methods_dict: Dict[str, List[str]]):
        pass
    
    @abstractmethod
    def pack_inherited_method_info(self, _class, inherited_method_info):
        pass
    
    def get_inherited_method_info(self, _class: Class) -> str:
        # 或者直接在original_string中添加上父类的方法？
        inherit_methods = self.get_inherited_methods(cls_name=_class['name'])
        
        if inherit_methods:
            inherit_methods_original_string = self.get_methods_original_string(class_methods_dict=inherit_methods)
            logger.info(f"Get inherited methods from super class: {_class['name']}")
            return inherit_methods_original_string
        return ''



