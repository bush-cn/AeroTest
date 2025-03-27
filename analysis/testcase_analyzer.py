from llm.llm import LLM
from utils.decorators import log_llm_interaction
from analysis.analyzer import Analyzer
from config import TESTCASE_ANALYSIS_RESULT_PATH, TESTCASE_METAINFO_PATH
from utils.data_processor import load_json, save_json
from utils.logger import logger
from prompt.testcase_analyzer import Prompt_C


class TestCaseAnalyzer(Analyzer):
    def __init__(self,
                 llm: LLM = None,
                 system_prompt: str = Prompt_C,
                 testcase_analysis_result_path: str = TESTCASE_ANALYSIS_RESULT_PATH,
                 ):
        Analyzer.__init__(self, llm=llm)
        self.llm = llm
        self.system_prompt = system_prompt
        self.testcase_metainfo = load_json(TESTCASE_METAINFO_PATH)
        self.testcase_analysis_result_path = testcase_analysis_result_path

    @log_llm_interaction("TestCaseAnalyzer")
    def call_llm(self, system_prompt, user_input) -> str:
        full_response = self.llm.chat(system_prompt, user_input)
        return full_response

    def execute(self):
        results = {}
        for uris, testcase in self.testcase_metainfo.items():
            resp_dict = self._analyze_testcase(testcase)
            results.update({uris: resp_dict})
        logger.info(f"Analyze all testcases finished")
        save_json(file_path=self.testcase_analysis_result_path, data=results)
        return results

    @staticmethod
    def get_testcase_analysis(testcase_analysis_result, function_name, file):
        return testcase_analysis_result.get(file + '.' + function_name)

    def analyze_testcase(self, testcase_name, file):
        return self._analyze_testcase(self.get_testcase(file+'.'+testcase_name))

    def _analyze_testcase(self, testcase):
        try:
            testcase_name = testcase['name']
            original_string = testcase['original_string']
            if testcase['docstring']:
                original_string = "/* " + testcase['docstring'] + " */\n" + original_string
            full_response = self.call_llm(system_prompt=self.system_prompt, user_input=original_string)
            resp_dict = self.extract(full_response)

            logger.info(f"Analyze testcase {testcase_name} finished")
            return resp_dict
        except Exception as e:
            logger.exception(f'Analyze testcase {testcase_name} failed: {e}')

