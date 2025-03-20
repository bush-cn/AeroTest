from analysis.analyzer import Analyzer
from llm.llm import LLM
from utils.data_processor import load_json, save_json
from utils.decorators import log_llm_interaction
from utils.logger import logger
from config import FUNCTION_METAINFO_PATH, STRUCT_METAINFO_PATH, CONTEXT_ANALYSIS_RESULT_PATH
from prompt.context_analyzer import Prompt_C


class ContextAnalyzer(Analyzer):
    """
    分析需要生成测试用例的函数上下文，包括调用的函数、结构体等信息。
    """
    def __init__(self,
                 llm: LLM = None,
                 system_prompt: str = Prompt_C,
                 context_analysis_result_path: str = CONTEXT_ANALYSIS_RESULT_PATH,
                 ):
        Analyzer.__init__(self, llm=llm)
        self.llm = llm
        self.system_prompt = system_prompt
        self.function_metainfo = load_json(FUNCTION_METAINFO_PATH)
        self.struct_metainfo = load_json(STRUCT_METAINFO_PATH)
        self.context_analysis_result_path = context_analysis_result_path
        self.all_functions = [function['signature'] for function in self.function_metainfo]
        self.all_structs = []
        self.get_all_structs()

    # TODO: parser解析typedef
    def get_all_structs(self):
        for struct in self.struct_metainfo:
            if struct['name']:
                self.all_structs.append('struct ' + struct['name'])
            if 'typedefs' in struct:
                for typedef in struct['typedefs']:
                    self.all_structs.append(typedef)

    @log_llm_interaction("TestCaseAnalyzer")
    def call_llm(self, system_prompt, user_input) -> str:
        full_response = self.llm.chat(system_prompt, user_input)
        return full_response

    def execute(self):
        results = []
        for function in self.function_metainfo:
            resp_dict = self.run_analyze_function_context(function)
            function_analyze_info = {
                'function_name': function['name'],
            }
            results.append({**function_analyze_info, **resp_dict})
        logger.info(f"Analyze all testcases finished")
        save_json(file_path=self.context_analysis_result_path, data=results)

    def analyze_function_context(self, function_uri: str):
        return self.run_analyze_function_context(self.get_function(function_uri))

    def run_analyze_function_context(self, function):
        try:
            function_name = function['name']

            user_input = f"Here are all functions: {self.all_functions}.\n" + \
                            f"Here are all structs: {self.all_structs}.\n" + \
                            "This is the testcase: \n"
            original_string = function['original_string']
            if function['docstring']:
                original_string = "/* " + function['docstring'] + " */\n" + original_string
            full_response = self.call_llm(system_prompt=self.system_prompt, user_input=user_input + original_string)
            resp_dict = self.extract(full_response)

            logger.info(f"Analyze function {function_name} finished")
            return resp_dict
        except Exception as e:
            logger.exception(f'Analyze function {function_name} failed: {e}')
