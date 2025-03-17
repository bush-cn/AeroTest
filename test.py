from functools import partial
import llm.deepseek_llm
from common.enum import LANGUAGE_TO_SUFFIX, LanguageEnum
from parser.source_parse import run_source_parse
from config import REPO_PATH, ALL_METAINFO_PATH
from source_parser.parsers.cpp_parser import CppParser
from parser.c_parser import CParser
from metainfo.c_metainfo_builder import CMetaInfoBuilder

# running_config = {
#     "class_analyzer": {
#         "analyzer": partial(JavaClassAnalyzer, llm=llm)
#     },
#     "testcase_analyzer": {
#         "analyzer": partial(JavaTestcaseAnalyzer, llm=llm)
#     },
#     "property_analyzer": {
#         "analyzer": partial(JavaPropertyAnalyzer, llm=llm)
#     },
#     "node_coordinator": {
#         "coordinator": partial(JavaNodeCoordinator, llm=llm)
#     },
#     "testcase_generator": {
#         "generator": partial(JavaTestcaseGenerator, llm=llm)
#     }
# }

if __name__ == "__main__":
    run_source_parse(REPO_PATH, LanguageEnum.C, CParser())

    builder = CMetaInfoBuilder()
    builder.build_metainfo()
    builder.save()
