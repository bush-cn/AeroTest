import re
import os
from analysis.analyzer import Analyzer
from analysis.context_analyzer import ContextAnalyzer
from analysis.testcase_analyzer import TestCaseAnalyzer
from analysis.repo_analyzer import RepoAnalyzer
from llm.llm import LLM
from config import (
    TESTCASE_ANALYSIS_RESULT_PATH,
    CONTEXT_ANALYSIS_RESULT_PATH,
    FUNCTION_SIMILARITY_PATH,
    FUNCTION_METAINFO_PATH,
    STRUCT_METAINFO_PATH,
    TESTCASE_METAINFO_PATH,
    ALL_METAINFO_PATH,
    GENERATION_RESULT_PATH
)
from utils.decorators import log_llm_interaction
from utils.logger import logger
from utils.data_processor import load_json
from prompt.generator import Prompt_has_ref


class CTestcaseGenerator(Analyzer):
    """
    生成指定函数的测试用例。
    1. 使用 LLM 捕获函数中使用到的结构体和函数名。
    2. 从metainfo中获取对应的结构体和函数信息作为上下文context。
    3. 查找该函数最相似的函数，获取其测试用例。
    4. 从metainfo中获取对应的相似函数及测试用例信息作为参考生成。
    5. 将全部信息输入LLM，生成测试用例。
    """

    def __init__(self,
                 llm: LLM,
                 system_prompt: str = Prompt_has_ref,
                 ):
        Analyzer.__init__(self, llm=llm)
        self.llm = llm
        self.system_prompt = system_prompt
        self.all_metainfo = load_json(ALL_METAINFO_PATH)
        self.function_metainfo = load_json(FUNCTION_METAINFO_PATH)
        self.struct_metainfo = load_json(STRUCT_METAINFO_PATH)
        self.testcase_metainfo = load_json(TESTCASE_METAINFO_PATH)

    @log_llm_interaction("TestcaseGenerator")
    def call_llm(self, system_prompt, user_input) -> str:
        full_response = self.llm.chat(system_prompt, user_input)
        return full_response

    def execute(self):
        similar = load_json(FUNCTION_SIMILARITY_PATH)
        context_analysis = load_json(CONTEXT_ANALYSIS_RESULT_PATH)
        testcase_analysis = load_json(TESTCASE_ANALYSIS_RESULT_PATH)
        for function in self.function_metainfo:
            self.run_generate_testcase(function, similar, context_analysis, testcase_analysis)

    def generate_testcase(self, function_uri, batch=True):
        function = self.get_function(function_uri)
        if batch:
            similar = load_json(FUNCTION_SIMILARITY_PATH)
            context_analysis = load_json(CONTEXT_ANALYSIS_RESULT_PATH)
            testcase_analysis = load_json(TESTCASE_ANALYSIS_RESULT_PATH)
        else:
            similar = RepoAnalyzer().analyze_function_similarity(function_uri)
            context_analysis = ContextAnalyzer().analyze_function_context(function_uri)
            testcase_analysis = TestCaseAnalyzer().analyze_testcase(function_uri)
        self.run_generate_testcase(function, similar, context_analysis, testcase_analysis)

    def run_generate_testcase(self, function, similar, context_analysis, testcase_analysis):
        similar = similar[function['name']]
        other_function = None
        for f in self.function_metainfo:
            if f['name'] == similar['other_function']:
                other_function = f
                break

        context = None
        for _context in context_analysis:
            if _context['function_name'] == function['name']:
                context = _context
                break

        testcases = []
        for _testcase in testcase_analysis:
            if 'functions' in _testcase:
                for _f in _testcase['functions']:
                    if (similar['other_function'] ==
                            re.search(r"](.*?)\(", _f['signature']).group(1)):
                        testcases.append(_testcase)
                        break

        if not testcases:
            # TODO: 没有可参考的测试用例，需要重新设计生成策略
            logger.warning(f"No testcases found for most similar function of {function['name']}.")
        elif len(testcases) > 1:
            # TODO: 多个测试用例，需要重新设计生成策略
            logger.warning(f"Multiple testcases found for most similar function of {function['name']}.")

        testcase = None
        for t in self.testcase_metainfo:
            if t['name'] == testcases[0]['testcase_name']:
                testcase = t
                break
        file = None
        for f in self.all_metainfo:
            for m in f['methods']:
                if m['name'] == testcase['name']:
                    file = f
                    break

        # TODO: 添加注释到original_string
        user_input = "\"Code A\":\n" + function['original_string'] + "\n\n" + \
                     f"context:\n- description of this function: {context['description']}\n" + \
                     f"- related functions: {context['related_functions']}\n" + \
                     f"- related structs: {context['related_structs']}\n\n" + \
                     "\"Code B\":\n" + f"{other_function['original_string']}" + "\n\n" + \
                     f"similarity: {similar['ts_score']}\n\n" + \
                     "\"Testcase B\":\n" + f"{testcase['original_string']}\n\n" + \
                     f"macros of \"Testcase B\":\n" + f"{file['contexts']}\n"
        response = self.call_llm(system_prompt=self.system_prompt, user_input=user_input)

        result = self.extract_code(response)
        os.makedirs(GENERATION_RESULT_PATH, exist_ok=True)
        with open(GENERATION_RESULT_PATH + f"test_{function['name']}.c", 'w', encoding='utf-8') as f:
            f.write(result)
        logger.info(f"Generated testcase for {function['name']}.")
