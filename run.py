import llm.deepseek_llm
from common.enum import LANGUAGE_TO_SUFFIX, LanguageEnum
from parser.source_parse import run_source_parse
from config import REPO_PATH, ALL_METAINFO_PATH
from parser.c_parser import CParser
from metainfo.c_metainfo_builder import CMetaInfoBuilder
from analysis.repo_analyzer import RepoAnalyzer
from analysis.testcase_analyzer import TestCaseAnalyzer
from analysis.context_analyzer import ContextAnalyzer
from generator.generator import CTestcaseGenerator

if __name__ == "__main__":
    run_source_parse(REPO_PATH, LanguageEnum.C, CParser())

    builder = CMetaInfoBuilder()
    builder.build_metainfo()
    builder.save()

    llm = llm.deepseek_llm.DeepSeekLLM()
    # repo_analyzer = RepoAnalyzer()
    # repo_analyzer.execute()
    # testcase_analyzer = TestCaseAnalyzer(llm=llm)
    # testcase_analyzer.execute()

    # context_analyzer = ContextAnalyzer(llm=llm)
    # context_analyzer.execute()

    generator = CTestcaseGenerator(llm=llm)
    generator.generate_testcase("img_init", "image.c",analyze_similarity=False, pre_analyzed=False)
