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
    packages_metainfo_path = config.PACKAGES_METAINFO_PATH
    file_imports_metainfo_path = config.FILE_IMPORTS_PATH
    language_mode = config.LANGUAGE_MODE

    def __init__(self) -> None:
        self.testcase_metainfo = load_testcase_metainfo(self.testcase_metainfo_path)
        self.file_imports_metainfo = load_file_imports_metainfo(self.file_imports_metainfo_path)
        self.testcase_metainfo = load_testcase_metainfo(self.testcase_metainfo_path)
        self.file_imports_metainfo = load_file_imports_metainfo(self.file_imports_metainfo_path)

        self.struct_metainfo = load_class_metainfo(self.struct_metainfo_path)
        self.function_metainfo = load_method_metainfo(self.function_metainfo_path)

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

    def get_type_or_none(self, type_name, package_name, metadata):
        """
        根据类型名称和包名称查找相应的元信息。
        如果找到多个匹配项，则选择与指定包名称匹配的那个。
        如果没有匹配项，则返回 None。
        """
        res = []
        for item in metadata:
            if item['name'] == type_name:
                res.append(item)

        if len(res) > 1:
            logger.warning(f"Found {len(res)} items with the same name {type_name} in package {package_name}")
            for item in res:
                package = item['file_path'].split('.java')[0].split('src/main/java/')[-1].replace('/', '.')
                if package == package_name:
                    logger.info(f"Found the item {item['name']} in package {package}")
                    return item

        return res[0] if len(res) > 0 else None

    def get_struct_or_none(self, struct_name, package_name):
        return self.get_type_or_none(struct_name, package_name, self.struct_metainfo)

    # TODO: 这个函数没看懂，classname如何迁移？
    def process_method_and_field_invocations(self, original_string, class_name, file_path, _class):
        """
        Extracts and processes method and field invocations based on the provided parameters.
        """
        methods_invoked, field_invoked = extract_identifiers(original_string=original_string, invoker_name=class_name)
        methods_invoked = [method.strip('.').split('(')[0] for method in methods_invoked]
        # logger.info(f"Methods invoked: {methods_invoked}")

        methods = []
        fields = []

        if methods_invoked:
            for method in self.method_metainfo:
                if file_path == method['file'] and method['name'] in methods_invoked:
                    logger.info(f"Find method {method['name']} in class {class_name}.")
                    methods.append(method['original_string'])

        if field_invoked:
            for field in _class['fields']:
                if field['name'].split('=')[0] in field_invoked:
                    logger.info(f"Find field {field['name']} in class {class_name}.")
                    fields.append(field['attribute_expression'])

        return methods, fields

    def fuzzy_get_method(self, file_path, class_name, method_name):
        for method in self.method_metainfo:
            if method['file'] == file_path and method['class_name'] == class_name and method['name'] == method_name:
                return method

    def fuzzy_get_testcase(self, file_path, class_name, testcase_name):
        for testcase in self.testcase_metainfo:
            if testcase['file'] == file_path and testcase['class_name'] == class_name and testcase[
                    'name'] == testcase_name:
                return testcase

    def fuzzy_get_class(self, class_name):
        for cls in self.class_metainfo:
            if class_name == cls['name']:
                return cls

    def fuzzy_get_testclass(self, testclass_name):
        for testclass in self.testclass_metainfo:
            if testclass_name == testclass['name']:
                return testclass

    def fuzzy_get_record(self, record_name):
        for record in self.record_metainfo:
            if record_name == record['name']:
                return record

    def fuzzy_get_interface(self, interface_name):
        for interface in self.interface_metainfo:
            if interface_name == interface['name']:
                return interface

    def fuzzy_get_abstractclass(self, abstractclass_name):
        for abstractclass in self.abstractclass_metainfo:
            if abstractclass_name == abstractclass['name']:
                return abstractclass

    def get_common_methods(self, child):
        child_class = self.fuzzy_get_class(class_name=child)
        if child_class is None:
            return None

        parent_class_name = child_class['superclasses']
        parent_class = self.fuzzy_get_class(class_name=parent_class_name)
        if parent_class is None:
            parent_class = self.fuzzy_get_abstractclass(abstractclass_name=parent_class_name)
        if parent_class is None:
            return None

        # methods = set(child_class['methods']) & set(parent_class['methods'])
        methods = set(parent_class['methods'])
        return methods

    def pack_testcases_original_string(self, testcases: List[str]) -> str:
        original_string = ""
        for testcase in testcases:
            testcase = self.get_testcase(testcase)
            if testcase is not None:
                original_string += testcase["original_string"]
                original_string += "\n\n"
        return original_string

    def pack_testclass_and_imports_for_testcases(self, testcase_uris: List[str]) -> str:
        res = ""
        class_uri_set = set()
        for testcase_uri in testcase_uris:
            testcase = self.get_testcase(testcase_uri)
            class_uri = testcase['class_uri']

            # This is a hack to avoid duplicate class provided
            if class_uri in class_uri_set:
                continue

            class_uri_set.add(class_uri)
            file_path = testcase['file']
            imports = self.get_imports(file_path)
            if imports is not None:
                res += "\n" + '\n'.join(imports)

            _class = self.get_testclass(class_uri)
            if _class is not None:
                res += "\n" + _class['original_string']
                logger.info(f"Packing testclass {_class['name']} for testcase: {testcase_uri}")

        return res

    def pack_class_montage_description(self, class_montage):
        return (
                "<class_name>" + class_montage['class_name'] + "</class_name>" +
                "<methods_signature>" + '\n'.join(class_montage['methods_signature']) + "</methods_signature>" +
                "<fields>" + '\n'.join(class_montage['fields']) + "</fields>"
        )

    def pack_interface_montage_description(self, interface_montage):
        return (
                "<interface_name>" + interface_montage['interface_name'] + "</interface_name>" +
                "<methods_signature>" + '\n'.join(interface_montage['methods_signature']) + "</methods_signature>"
        )

    def pack_abstractclass_montage_description(self, abstractclass_montage):
        return (
                "<abstract_class_name>" + abstractclass_montage['abstract_class_name'] + "</abstract_class_name>" +
                "<methods_signature>" + '\n'.join(abstractclass_montage['methods_signature']) + "</methods_signature>"
        )

    def pack_package_class_montages_description(self, package_class_montages):
        if not package_class_montages:
            return ""

        description = "\nAnd We provide you with the montage information of the package to help you."
        for package_class_montage in package_class_montages:
            description += self.pack_class_montage_description(package_class_montage)
        return description

    def pack_package_refs_description(self, package_refs):
        if not package_refs:
            return ""

        content = "\nAnd we provide you with the package references to help you."
        description = ""
        for package_ref in package_refs:
            methods_str = '\n'.join(package_ref['methods']) if package_ref['methods'] else ""
            fields_str = '\n'.join(package_ref['fields']) if package_ref['fields'] else ""
            description += (
                    "<ref>\n" + "name:\n" + package_ref['name'] + '\n' + methods_str + '\n' + fields_str + "\n</ref>\n"
            )
        return content + description

    def pack_repo_refs_use_dot_description(self, repo_refs):
        if not repo_refs:
            return ""
        content = "\nAnd we provide you with the repo references of target method to help you."
        description = ""
        for repo_refs in repo_refs:
            methods_str = '\n'.join(repo_refs['methods']) if repo_refs['methods'] else ""
            fields_str = '\n'.join(repo_refs['fields']) if repo_refs['fields'] else ""
            description += (
                    "<ref>\n" + "name:\n" + repo_refs['name'] + '\n' + methods_str + '\n' + fields_str + "\n</ref>\n"
            )
        return content + description

    # def get_methods_original_string(self, class_methods_dict: Dict[str, List[str]]):
    #     original_string = ""
    #     for _class, methods in class_methods_dict.items():
    #         for method in self.method_metainfo:
    #             if method['class_name'] != _class:
    #                 continue
    #             if method['name'] + "#" + str(method['arg_nums']) in methods:
    #                 original_string += method['original_string']
    #     return original_string


def run_build_metainfo(builder: CMetaInfoBuilder):
    logger.info('run_build_metainfo start.')
    builder.build_metainfo()
    builder.save()

    #   TODO: 这里代码没看懂，C应该不需要package、brother、interface？

    logger.info('resolve file imports(includes) for C start...')
    builder.resolve_file_imports(file_imports_path=config.FILE_IMPORTS_PATH)
    logger.info('resolve file imports(includes) for C start...')

    logger.info('run_build_metainfo Done!')


if __name__ == '__main__':
    metainfo_json_path = r'/home/zhangzhe/APT/repo_parse/python_files_results.json'
    resolved_metainfo_path = r'/home/zhangzhe/APT/repo_parse/'
    # builder = PythonMetaInfoBuilder(
    #     metainfo_json_path=metainfo_json_path,
    #     resolved_metainfo_path=resolved_metainfo_path
    # )

    builder = JavaMetaInfoBuilder()

    # builder.build_metainfo()
    # builder.save()
    builder.resolve_file_imports()

    # builder.resolve_file_imports(file_imports_path=r'/home/zhangzhe/APT/repo_parse/file_imports.json')

    # builder.resolve_package_level_info(
    #     packages_metainfo_path=r'/home/zhangzhe/APT/repo_parse/packages_metainfo.json')
