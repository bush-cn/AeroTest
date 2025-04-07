import sys
import io
import argparse
import llm.deepseek_llm
from common.enum import LANGUAGE_TO_SUFFIX, LanguageEnum
from parser.source_parse import run_source_parse
from config import global_config
from parser.c_parser import CParser
from metainfo.c_metainfo_builder import CMetaInfoBuilder
from analysis.repo_analyzer import RepoAnalyzer
from analysis.testcase_analyzer import TestCaseAnalyzer
from analysis.context_analyzer import ContextAnalyzer
from generator.generator import CTestcaseGenerator


def run(function_name, file_name, reference=False):
    run_source_parse(global_config['REPO_PATH'], LanguageEnum.C, CParser())

    builder = CMetaInfoBuilder()
    builder.build_metainfo()
    builder.save()

    _llm = llm.deepseek_llm.DeepSeekLLM()
    # TODO：batch analyze
    # repo_analyzer = RepoAnalyzer()
    # repo_analyzer.execute()
    # testcase_analyzer = TestCaseAnalyzer(llm=_llm)
    # testcase_analyzer.execute()

    # context_analyzer = ContextAnalyzer(llm=_llm)
    # context_analyzer.execute()

    generator = CTestcaseGenerator(llm=_llm)
    generator.generate_testcase(function_name, file_name, analyze_similarity=reference, pre_analyzed=False)


# backend
def run_with_output(function_name, file_name, reference=False):
    buffer = io.StringIO()
    sys_stdout = sys.stdout
    sys.stderr = sys.stdout = buffer  # 捕获 stderr 也可选

    try:
        run(function_name, file_name, reference)
    finally:
        sys.stdout = sys_stdout
        sys.stderr = sys_stdout

    return buffer.getvalue()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="AeroTest CLI")
    # parser.add_argument("function_name", type=str, help="Function name to generate test case for")
    # parser.add_argument("file_name", type=str, help="File name containing the function")
    # parser.add_argument(
    #     "-r", "--reference",
    #     action="store_true",
    #     help="Whether to use reference test cases for generation",
    # )
    # args = parser.parse_args()
    # run(args.function_name, args.file_name, args.reference)
    run("cg_quit", "commands.c", reference=False)
