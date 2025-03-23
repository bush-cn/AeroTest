import json
import os
from typing import List

from utils.logger import logger


def add_json_item(file_path: str, item: dict, key: str = None):
    """
    将一个新的数据项添加到 JSON 文件中。

    :param file_path: JSON 文件的路径
    :param item: 要添加的数据项
    :param key: 如果提供，则将数据项添加到指定键的列表中；否则，将数据项添加到根列表中
    """
    try:
        # 加载现有的 JSON 数据
        data = load_json(file_path)

        if key:
            # 如果指定了键，则将数据项添加到指定键的列表中
            if key not in data:
                data[key] = []
            data[key].append(item)
        else:
            # 如果没有指定键，则将数据项添加到根列表中
            if not isinstance(data, list):
                data = []
            data.append(item)

        # 保存更新后的 JSON 数据
        save_json(file_path, data)
    except Exception as e:
        logger.exception(f"Error adding item to json file: {e}")


def save_json(file_path: str, data: dict | list):
    try:
        # 获取文件所在的目录路径
        dir_path = os.path.dirname(file_path)

        # 如果目录不存在，则创建目录
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        logger.exception(f"Error saving json file: {e}")


def load_json(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.exception(f"Error loading json file: {e}")


def load_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.exception(f"Error loading file: {e}")


def load_testcase_metainfo(testcase_metainfo_path):
    testcases = load_json(testcase_metainfo_path)
    return testcases


def load_class_metainfo(class_metainfo_path):
    class_metainfo = load_json(class_metainfo_path)
    return class_metainfo


def load_method_metainfo(method_metainfo_path):
    method_metainfo = load_json(method_metainfo_path)
    return method_metainfo


def load_packages_metainfo(packages_metainfo_path=r"/home/zhangzhe/APT/repo_parse/packages_metainfo.json"):
    return load_json(packages_metainfo_path)


def load_file_imports_metainfo(file_imports_metainfo_path=r"/home/zhangzhe/APT/repo_parse/file_imports.json"):
    return load_json(file_imports_metainfo_path)


def load_all_metainfo(
        class_metainfo_path: str = None,
        method_metainfo_path: str = None,
        testcase_metainfo_path: str = None,
) -> List[list]:
    paths = [testcase_metainfo_path, class_metainfo_path, method_metainfo_path]
    keys = ['testcases', 'classes', 'methods']
    res = []

    for i, path in enumerate(paths):
        data = load_json(path)
        res.append(data[keys[i]])

    return res


def get_single_value_in_dict(dictionary):
    for _, value in dictionary.items():
        return value


def get_singe_key_in_dict(dictionary):
    return next(iter(dictionary))


def extract_code_from_json(json_file_path, output_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            code = data[0]['code']
        with open(output_file_path, 'w') as out_file:
            out_file.write(code)
        logger.info(f"Code extracted successfully from JSON and saved to {output_file_path}")
    except Exception as e:
        logger.exception(f"Error extracting code from JSON: json_file_path: {json_file_path}, err: {e}")
