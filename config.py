LANGUAGE_MODE = "cpp"

LOG_DIR = r"D:\Code\UnitTestGen\logs"
LLM_LOG_DIR = LOG_DIR + r"\llm_logs"

REPO_PATH = r"D:\Code\UnitTestGen\mahm3lib"
CUSTOMIZED_TESTCODE_PATH = [
    r"test"
]   # relative path
EXCEPTE_PATH = [
    r"D:\Code\UnitTestGen\mahm3lib\src\unity"
]
RESOLVED_METAINFO_PATH = "D:\\Code\\UnitTestGen\\data\\"
ALL_METAINFO_PATH = r"D:\Code\UnitTestGen\data\all_metainfo.json"

TESTCASE_METAINFO_PATH = RESOLVED_METAINFO_PATH + "testcase_metainfo.json"
# 新增
FUNCTION_METAINFO_PATH = RESOLVED_METAINFO_PATH + "function_metainfo.json"
STRUCT_METAINFO_PATH = RESOLVED_METAINFO_PATH + "struct_metainfo.json"

FUNCTION_SIMILARITY_PATH = RESOLVED_METAINFO_PATH + "function_similarity.json"

CLASS_PROPERTY_PATH = RESOLVED_METAINFO_PATH + "class_property.json"
CLASS_PROPERTY_DIR = RESOLVED_METAINFO_PATH + "class_property/"
CLASS_SIMILARITY_PATH = RESOLVED_METAINFO_PATH + "class_similarity.json"
TESTCASE_ANALYSIS_RESULT_PATH = RESOLVED_METAINFO_PATH + "testcase_analysis_result.json"
TESTCLASS_ANALYSIS_RESULT_PATH = RESOLVED_METAINFO_PATH + "testclass_analysis_result.json"
TESTCLASS_ANALYSIS_RESULT_DIR = RESOLVED_METAINFO_PATH + "testclass_analysis_result/"
INHERIT_TREE_PATH = RESOLVED_METAINFO_PATH + "inherit_tree.json"
FUNC_RELATION_PATH = RESOLVED_METAINFO_PATH + "func_relation.json"
METHOD_PROPERTY_DIR = RESOLVED_METAINFO_PATH + "method_property/"
BROTHER_RELATIONS_PATH = RESOLVED_METAINFO_PATH + "brother_relations.json"
BROTHER_ENHANCEMENTS_PATH = RESOLVED_METAINFO_PATH + "brother_enhancements.json"
PARENT_ENHANCEMENTS_PATH = RESOLVED_METAINFO_PATH + "parent_enhancements.json"
CHILD_ENHANCEMENTS_PATH = RESOLVED_METAINFO_PATH + "child_enhancements.json"
POTENTIAL_BROTHER_RELATIONS_PATH = RESOLVED_METAINFO_PATH + "potential_brother_relations.json"
INTERFACE_BROTHER_RELATIONS_PATH = RESOLVED_METAINFO_PATH + "interface_brother_relations.json"
INTERFACE_BROTHER_ENHANCEMENTS_PATH = RESOLVED_METAINFO_PATH + "interface_brother_enhancements.json"
NODE_TO_TESTCASE_PATH = RESOLVED_METAINFO_PATH + "node_to_testcase.json"
NODE_COORDINATOR_RESULT_PATH = RESOLVED_METAINFO_PATH + "node_coordinator_result.json"
# UNMAPPED_NODES_PATH = RESOLVED_METAINFO_PATH + "unmapped_nodes.json"
PART_UNMAPPED_NODES_PATH = RESOLVED_METAINFO_PATH + "part_unmapped_nodes.json"
FULL_UNMAPPED_NODES_PATH = RESOLVED_METAINFO_PATH + "full_unmapped_nodes.json"
EXISTING_ENHANCEMENTS_PATH = RESOLVED_METAINFO_PATH + "existing_enhancements.json"
METHOD_TO_PRIMARY_TESTCASE_PATH = RESOLVED_METAINFO_PATH + "method_to_primary_testcase.json"
METHOD_TO_RELEVANT_TESTCASE_PATH = RESOLVED_METAINFO_PATH + "method_to_relevant_testcase.json"
CLASS_TO_PRIMARY_TESTCASE_PATH = RESOLVED_METAINFO_PATH + "class_to_primary_testcase.json"
CLASS_TO_RELEVANT_TESTCASE_PATH = RESOLVED_METAINFO_PATH + "class_to_relevant_testcase.json"
HISTORY_TESTCASE_PATHS_PATH = RESOLVED_METAINFO_PATH + "history_testcase_paths.json"
FILE_PATHS_WITH_TWO_DOTS = RESOLVED_METAINFO_PATH + "file_paths_with_two_dots.txt"
PROPERTY_GRAPH_PATH = RESOLVED_METAINFO_PATH + "property_graph.json"
METHOD_COVERAGE_RESULT_PATH = RESOLVED_METAINFO_PATH + "method_coverage_result.json"

GENERATED_TESTCASES_PATH = RESOLVED_METAINFO_PATH + "generated_testcases.json"
GENERATED_TESTCASES_DIR = RESOLVED_METAINFO_PATH + "generated_testcases/"
COMPLETED_TESTCASES_DIR = RESOLVED_METAINFO_PATH + "completed_testcases/"
RUNNING_STATUS_DIR = RESOLVED_METAINFO_PATH + "running_status/"
FAILED_TESTFILES_PATH = RESOLVED_METAINFO_PATH + "failed_testfiles.json"
GENERATED_TESTFILE_RUNNING_STATUS_PATH = RESOLVED_METAINFO_PATH + "generated_testfile_running_status.json"
GENERATED_TESTCASES_RESULT_PATH = RESOLVED_METAINFO_PATH + "generated_testcases_result.json"
TESTFILES_PATH = RESOLVED_METAINFO_PATH + "testfiles.txt"
TARGET_METHODS_PATH = RESOLVED_METAINFO_PATH + "target_methods.txt"
CLASS_ALREADY_HAVED_TESTCASE_PATH = RESOLVED_METAINFO_PATH + "class_already_haved_testcase.txt"
EXPERIMENT_RESULT_PATH = RESOLVED_METAINFO_PATH + "experiment_result.json"
TRY_GENERATED_TESTCASES_PATH = RESOLVED_METAINFO_PATH + "try_generated_testcases.json"
FINAL_RESULT_PATH = RESOLVED_METAINFO_PATH + "final_result.json"
STATUS_DISTRIBUTION_PATH = RESOLVED_METAINFO_PATH + "status_distribution.txt"
METHOD_BEING_TESTED_PATH = RESOLVED_METAINFO_PATH + "method_being_tested.txt"
MAX_RETRY_NUMBER = 2