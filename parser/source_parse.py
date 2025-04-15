import os
from source_parser.parsers.language_parser import LanguageParser
from parser.tree_sitter_query_parser import extract_global_variables
from common.enum import LANGUAGE_TO_SUFFIX, LanguageEnum
from source_parser.utils import static_hash
from utils.data_processor import save_json
from config import global_config
from utils.logger import logger


class Processor:
    def __init__(self,
                 repo_dir: str,
                 language: LanguageEnum,
                 parser: LanguageParser):
        self.repo_dir = repo_dir
        self.language = language
        self.parser = parser

    def process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            file_contents = f.read()
        self.parser.update(file_contents)
        return self.parser.schema

    def batch_process(self, directory):
        # directory是绝对路径
        results = []
        parser = self.parser
        file_suffix = LANGUAGE_TO_SUFFIX[self.language]

        exclude_paths = set(os.path.abspath(p) for p in global_config['EXCEPTE_PATH'])
        for root, dirs, files in os.walk(directory):
            root_abs = os.path.abspath(root)

            # 跳过.开头的目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            # 跳过用户配置文件中指定的目录
            new_dirs = []
            for d in dirs:
                abs_dir = os.path.join(root_abs, d)
                if os.path.abspath(abs_dir) not in exclude_paths:
                    new_dirs.append(d)
            dirs[:] = new_dirs

            for file in files:
                if not file.endswith(file_suffix):
                    continue  # 跳过

                file_path = os.path.join(root, file)
                abs_file_path = os.path.abspath(file_path)
                if abs_file_path in exclude_paths:
                    continue  # 跳过配置中排除的文件
                relative_path = os.path.relpath(file_path, directory)

                # 新增文件编码检测
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents = f.read()
                except UnicodeDecodeError as e:
                    logger.exception(f"\n\tFile {file_path} raised {type(e)}: {e}\n")
                    continue

                try:
                    processed_contents = parser.preprocess_file(file_contents)
                    parser.update(processed_contents)
                    if not processed_contents:
                        continue

                except Exception as e_err:
                    logger.exception(f"\n\tFile {file_path} raised {type(e_err)}: {e_err}\n")
                    continue

                schema = parser.schema

                if not any(schema.values()):
                    continue  # 跳过没有特征的文件

                file_results = {
                    "relative_path": relative_path,
                    "original_string": processed_contents,
                    "file_hash": static_hash(file_contents),  # REQUIRED!
                }
                file_results.update(schema)
                # 新增查询文件中的全局变量
                global_vars = extract_global_variables(processed_contents)
                file_results["global_variables"] = global_vars

                results.append(file_results)

        logger.info(f"{len(results)} files processed")
        return results


def run_source_parse(repo_path: str, language: LanguageEnum, parser: LanguageParser):
    logger.info("start repo parsing...")

    processor = Processor(repo_dir=repo_path, language=language, parser=parser)
    results = processor.batch_process(repo_path)
    # 将结果转为以文件名为key的字典
    results_dict = {file['relative_path']: file for file in results}

    save_json(global_config['ALL_METAINFO_PATH'], results_dict)
    logger.info("repo parsed successfully!")
