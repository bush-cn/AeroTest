import llm.deepseek_llm
from common.enum import LANGUAGE_TO_SUFFIX, LanguageEnum
from parser.source_parse import run_source_parse
from config import REPO_PATH, ALL_METAINFO_PATH
from parser.c_parser import CParser
from metainfo.c_metainfo_builder import CMetaInfoBuilder
from analysis.repo_analyzer import RepoAnalyzer
from analysis.testcase_analyzer import TestCaseAnalyzer

if __name__ == "__main__":
    run_source_parse(REPO_PATH, LanguageEnum.C, CParser())

    builder = CMetaInfoBuilder()
    builder.build_metainfo()
    builder.save()

    # repo_analyzer = RepoAnalyzer()
    # repo_analyzer.execute()
    llm = llm.deepseek_llm.DeepSeekLLM()
    testcase_analyzer = TestCaseAnalyzer(llm=llm)
