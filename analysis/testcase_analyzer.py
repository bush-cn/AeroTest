import concurrent.futures

from llm.deepseek_llm import DeepSeekLLM
from llm.llm import LLM

from utils.decorators import log_llm_interaction
from analysis.analyzer import Analyzer
from config import TESTCASE_ANALYSIS_RESULT_PATH, TESTFILE_METAINFO_PATH, FUNCTION_METAINFO_PATH
from utils.data_processor import load_json, save_json
from utils.logger import logger
from prompt.testcase_analyzer import Prompt_C


class TestCaseAnalyzer(Analyzer):
    def __init__(self,
                 llm: LLM,
                 system_prompt: str = Prompt_C
                 ):
        Analyzer.__init__(self, llm=llm)
        self.llm = llm
        self.testcase_metainfo = load_json(TESTFILE_METAINFO_PATH)
        self.testcase_analysis_result_path = TESTCASE_ANALYSIS_RESULT_PATH
        self.function_metainfo = load_json(FUNCTION_METAINFO_PATH)
        self.all_functions = [function['signature'] for function in self.function_metainfo]
        self.system_prompt = system_prompt

    @log_llm_interaction("TestCaseAnalyzer")
    def call_llm(self, system_prompt, user_input) -> str:
        full_response = self.llm.chat(system_prompt, user_input)
        return full_response

    def batch_high_level_analyze(self):
        raise NotImplementedError

    def high_level_analyze(self):
        """
        If one test function is in a test class, we analyze the test class;

        # The following cases is for Python and Go.
        else if one test function is in a file, we analyze the file;
            if file is too long,
        """
        raise NotImplementedError

    def execute(self):
        results = []
        for testcase in self.testcase_metainfo:
            try:
                testcase_name = testcase['name']
                file = testcase['file']

                user_input = f'Here are all functions: {self.all_functions}.\n' + 'This is the testcase: \n'
                original_string = testcase['original_string']
                if testcase['docstring']:
                    original_string = "/* " + testcase['docstring'] + " */\n" + original_string

                full_response = self.call_llm(system_prompt=self.system_prompt, user_input=user_input + original_string)
                resp_dict = self.extract(full_response)

                testcase_analyze_info = {
                    'file': file,
                }
                results.append({**testcase_analyze_info, **resp_dict})

                logger.info(f"Analyze testcase {testcase_name} finished")
            except Exception as e:
                logger.exception(f'Analyze testcase {testcase_name} failed: {e}')

        save_json(file_path=self.testcase_analysis_result_path, data=results)


def run_testcase_analyzer(analyzer: TestCaseAnalyzer):
    logger.info("Starting testcase analyzer...")
    analyzer.execute()
    logger.info("Testcase analyzer finished!")
