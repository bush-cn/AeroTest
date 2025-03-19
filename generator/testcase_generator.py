from analysis.analyzer import Analyzer
from llm.llm import LLM
from config import (
    TESTCASE_ANALYSIS_RESULT_PATH,
    FUNCTION_SIMILARITY_PATH,
    FUNCTION_METAINFO_PATH,
    STRUCT_METAINFO_PATH,
    TESTCASE_METAINFO_PATH,
)
from utils.decorators import log_llm_interaction
from utils.logger import logger
from utils.data_processor import load_json


class CTestcaseGenerator(Analyzer):
    def __init__(self,
                 llm: LLM):
        Analyzer.__init__(self, llm=llm)
        self.function_metainfo = load_json(FUNCTION_METAINFO_PATH)
        self.struct_metainfo = load_json(STRUCT_METAINFO_PATH)
        self.testcase_metainfo = load_json(TESTCASE_METAINFO_PATH)
        self.function_similarity = load_json(FUNCTION_SIMILARITY_PATH)
        self.testcase_analysis_result = load_json(TESTCASE_ANALYSIS_RESULT_PATH)

    def execute(self):
        pass

    @log_llm_interaction("TestcaseGenerator")
    def call_llm(self, system_prompt, user_input) -> str:
        full_response = self.llm.chat(system_prompt, user_input)
        return full_response

    def generate_testcase(self, function_uri: str):
        """
        生成指定函数的测试用例。
        1. 使用 LLM 捕获函数中使用到的结构体和函数名。
        2. 从metainfo中获取对应的结构体和函数信息作为上下文context。
        3. 查找该函数最相似的函数，获取其测试用例。
        4. 从metainfo中获取对应的相似函数及测试用例信息作为参考生成。
        5. 将全部信息输入LLM，生成测试用例。
        """
