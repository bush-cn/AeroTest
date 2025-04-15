import re
import os
from analysis.analyzer import Analyzer
from analysis.context_analyzer import ContextAnalyzer
from analysis.testcase_analyzer import TestCaseAnalyzer
from analysis.repo_analyzer import RepoAnalyzer
from llm.llm import LLM
from config import global_config
from utils.decorators import log_llm_interaction
from utils.logger import logger
from utils.data_processor import load_json
from prompt.generator import Prompt


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
                 system_prompt: str = Prompt,
                 pre_analyzed: bool = False,
                 ):
        Analyzer.__init__(self, llm=llm)
        self.llm = llm
        self.system_prompt = system_prompt
        self.all_metainfo = load_json(global_config['ALL_METAINFO_PATH'])
        self.function_metainfo = load_json(global_config['FUNCTION_METAINFO_PATH'])
        self.udt_metainfo = load_json(global_config['UDT_METAINFO_PATH'])
        self.global_variable_metainfo = load_json(global_config['GLOBAL_VARIABLE_METAINFO_PATH'])
        self.testcase_metainfo = load_json(global_config['TESTCASE_METAINFO_PATH'])

        self.context_analysis = load_json(global_config['CONTEXT_ANALYSIS_RESULT_PATH']) if pre_analyzed else None
        self.testcase_analysis = load_json(global_config['TESTCASE_ANALYSIS_RESULT_PATH']) if pre_analyzed else None
        self.similar_analysis = load_json(global_config['FUNCTION_SIMILARITY_PATH']) if pre_analyzed else None

    @log_llm_interaction("TestcaseGenerator")
    def call_llm(self, system_prompt, user_input) -> str:
        full_response = self.llm.chat(system_prompt, user_input)
        return full_response

    def execute(self):
        assert self.context_analysis is not None, "execute() must be used after pre-analyzed."
        for uris, function in self.function_metainfo.items():
            self._generate_testcase(function,
                                    self.similar_analysis.get(uris),
                                    self.context_analysis.get(uris),
                                    self.testcase_analysis)

    def generate_testcase(self, function_name, file, analyze_similarity=False, pre_analyzed=False):
        function = self.get_function(file + '.' + function_name)
        similar = None
        testcase_analysis = None
        if pre_analyzed:
            context_analysis = load_json(global_config['CONTEXT_ANALYSIS_RESULT_PATH'])
            if analyze_similarity:
                similar = load_json(global_config['FUNCTION_SIMILARITY_PATH'])
                testcase_analysis = load_json(global_config['TESTCASE_ANALYSIS_RESULT_PATH'])
        else:
            context_analysis = ContextAnalyzer(llm=self.llm).analyze_function_context(function_name, file)
            if analyze_similarity:
                similar = RepoAnalyzer(llm=self.llm).analyze_function_similarity(function_name, file)
                testcase_analysis = TestCaseAnalyzer(llm=self.llm).execute()
        self._generate_testcase(function, context_analysis, similar=similar, testcase_analysis=testcase_analysis)

    def _generate_testcase(self, function, context, similar=None, testcase_analysis=None):
        """
        similar, context_analysis都是以函数uri对应的解析结果
        而testcase_analysis是以全部testcase的结果
        """
        logger.info(f"Generating testcase for {function['name']}...")
        # 全局变量的UDT也需要加入到context_udts中
        global_variable_udts_string = ""
        for global_variable_name in context['global_variables']:
            global_variable = self.get_global_variable(global_variable_name, function['file'])
            if global_variable is not None:
                global_variable_udts_string += self._get_udt_string(global_variable['type'])


        llm_input = LLMInput(
            focal_function=function['original_string'],
            includes='\n'.join(self.all_metainfo.get(function['file'])['contexts']),
            context_functions='\n'.join([result for f in context['functions']
                                         if (result := self._get_function_string(f, function['file'])) is not None]),
            context_udts='\n'.join([self._get_udt_string(u) for u in context['udts']])
                         + '\n' + global_variable_udts_string,
            context_global_variables='\n'.join([result for g in context['global_variables']
                                                if (result := self._get_global_variable_string(g, function[
                    'file'])) is not None]),
            context_marcos='\n'.join([result for m in context['macros']
                                      if (result := self._get_marco_string(m, function['file'])) is not None]),
            reference=self._get_reference_string(similar, testcase_analysis)
        )

        response = self.call_llm(system_prompt=self.system_prompt, user_input=str(llm_input))
        result = self.extract_code(response)
        path = os.path.dirname(function['file'])
        file_name = os.path.basename(function['file']).removesuffix('.c')
        with open(os.path.join(global_config['REPO_PATH'], path, f"test_{file_name}_{function['name']}.c"), 'w', encoding='utf-8') as f:
            f.write(result)
        logger.info(f"Generated testcase for {function['name']} successfully.")

    def _get_function_string(self, function_name, file):
        function = self.get_function(function_name, file)
        if function is None:
            return None

        original_string = function['original_string']
        if function['docstring']:
            original_string = "/* " + function['docstring'] + " */\n" + original_string
        return original_string

    def _get_udt_string(self, udt_name):
        return '\n'.join([(("/* " + udt['docstring'] + " */\n") if udt['docstring'] else "")
                          + udt['original_string'] for udt in self.get_udt(udt_name)])

    def _get_global_variable_string(self, global_variable_name, file):
        global_variable = self.get_global_variable(global_variable_name, file)
        if global_variable is None:
            return None

        original_string = global_variable['original_string']
        if global_variable['docstring']:
            original_string = "/* " + global_variable['docstring'] + " */\n" + original_string
        return original_string

    def _get_marco_string(self, marco_name, file):
        contexts = self.all_metainfo[file]['contexts']
        includes = []
        for context in contexts:
            if context.startswith("#define ") and marco_name in context:
                return context
            elif context.startswith("#include "):
                includes.append(context)

        # 如果没有找到，则前往引入的头文件中查找
        for include in includes:
            include_file = include.split()[1]
            if include_file.startswith('"') and include_file.endswith('"'):
                include_file = include_file.strip('"')
                path = os.path.dirname(file)
                include_file = os.path.join(path, include_file)
                return self._get_marco_string(marco_name, include_file)

        return None

    def _get_reference_string(self, similar, testcase_analysis):
        if similar is None or testcase_analysis is None:
            return None

        if similar['ts_score'] < global_config['REFERENCE_THRESHOLD']:
            return None

        result = "The most similar function:\n"
        similar_function = self.get_function(similar['similar_function'])
        result += (("\* " + similar_function['docstring'] + " */\n") if similar_function['docstring'] else "") + \
                  similar_function['original_string']
        result += "\n\nIts testcases from source:\n"
        for uris, _testcase in testcase_analysis.items():
            if 'functions' in _testcase:
                for _f in _testcase['functions']:
                    if _f in similar['similar_function']:
                        result += (("\* " + _testcase['docstring'] + " */\n") if _testcase['docstring'] else "") + \
                                  _testcase['original_string']

        return result


class LLMInput:
    def __init__(self,
                 focal_function: str,
                 includes: str,
                 context_functions: str,
                 context_udts: str,
                 context_global_variables: str,
                 context_marcos: str,
                 reference: str = None,
                 ):
        self.focal_function = focal_function
        self.includes = includes
        self.context_functions = context_functions
        self.context_udts = context_udts
        self.context_global_variables = context_global_variables
        self.context_marcos = context_marcos
        self.reference = reference

    def __str__(self) -> str:
        str = f"""Target Function to be tested: \n{self.focal_function}
Its header files and macro definitions you must all include in test file: \n{self.includes}
---
Context Information you may need:
1. Source code of involved function: \n{self.context_functions}
2. User-defined types: \n{self.context_udts}
3. Global variables: \n{self.context_global_variables}
4. Macro definitions: \n{self.context_marcos}"""
        if self.reference:
            str += (f"---"
                    f"Reference test case from source: {self.reference}")
        return str
