from analysis.analyzer import Analyzer
from llm.llm import LLM
from utils.data_processor import load_json, save_json
from utils.decorators import log_llm_interaction
from utils.logger import logger
from config import global_config
from prompt.context_analyzer import Prompt


class ContextAnalyzer(Analyzer):
    """
    分析需要生成测试用例的函数上下文，包括调用的函数、UDT、全局变量、宏信息。
    """
    def __init__(self,
                 llm: LLM = None,
                 system_prompt: str = Prompt,
                 context_analysis_result_path: str = global_config['CONTEXT_ANALYSIS_RESULT_PATH'],
                 ):
        Analyzer.__init__(self, llm=llm)
        self.llm = llm
        self.system_prompt = system_prompt
        self.function_metainfo = load_json(global_config['FUNCTION_METAINFO_PATH'])
        self.context_analysis_result = None
        self.context_analysis_result_path = context_analysis_result_path

    @log_llm_interaction("TestCaseAnalyzer")
    def call_llm(self, system_prompt, user_input) -> str:
        full_response = self.llm.chat(system_prompt, user_input)
        return full_response

    def execute(self):
        results = {}
        for uris, function in self.function_metainfo.items():
            resp_dict = self._analyze_function_context(function)
            results.update({uris: resp_dict})
        logger.info(f"Analyze all testcases finished")
        self.context_analysis_result = results
        save_json(file_path=self.context_analysis_result_path, data=results)

    @staticmethod
    def get_context_analysis(context_analysis_result, function_name, file):
        return context_analysis_result.get(file + '.' + function_name)

    def analyze_function_context(self, function_name, file_path):
        return self._analyze_function_context(self.get_function(file_path+'.'+function_name))

    def _analyze_function_context(self, function):
        try:
            function_name = function['name']
            original_string = function['original_string']
            full_response = self.call_llm(system_prompt=self.system_prompt, user_input=original_string)
            resp_dict = self.extract(full_response)

            save_json(file_path=self.context_analysis_result_path, data={function['uris']: resp_dict})

            logger.info(f"Analyze function {function_name} finished")
            return resp_dict
        except Exception as e:
            logger.exception(f'Analyze function {function_name} failed: {e}')
