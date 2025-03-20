LANGUAGE_MODE = "cpp"

LOG_DIR = r"D:\Code\UnitTestGen\logs"
LLM_LOG_DIR = LOG_DIR + r"\llm_logs"

REPO_PATH = r"D:\Code\UnitTestGen\test_repo"
# REPO_PATH = r"D:\Code\UnitTestGen\mahm3lib"
# REPO_PATH = r"D:\Code\UnitTestGen\fzy"
CUSTOMIZED_TESTCODE_PATH = [
    r"test"
]  # relative path
EXCEPTE_PATH = [
    r"D:\Code\UnitTestGen\mahm3lib\src\unity"
]
# EXCEPTE_PATH = [
#     r"D:\Code\UnitTestGen\fzy\deps"
# ]
RESOLVED_METAINFO_PATH = "D:\\Code\\UnitTestGen\\data\\"
ALL_METAINFO_PATH = r"D:\Code\UnitTestGen\data\all_metainfo.json"

TESTCASE_METAINFO_PATH = RESOLVED_METAINFO_PATH + "testcase_metainfo.json"
# 新增
FUNCTION_METAINFO_PATH = RESOLVED_METAINFO_PATH + "function_metainfo.json"
STRUCT_METAINFO_PATH = RESOLVED_METAINFO_PATH + "struct_metainfo.json"

FUNCTION_SIMILARITY_PATH = RESOLVED_METAINFO_PATH + "function_similarity.json"
TESTCASE_ANALYSIS_RESULT_PATH = RESOLVED_METAINFO_PATH + "testcase_analysis_result.json"
CONTEXT_ANALYSIS_RESULT_PATH = RESOLVED_METAINFO_PATH + "context_analysis_result.json"

GENERATION_RESULT_PATH = "D:\\Code\\UnitTestGen\\results\\"
