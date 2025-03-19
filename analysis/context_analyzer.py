from analysis.analyzer import Analyzer
from llm.llm import LLM


class ContextAnalyzer(Analyzer):
    """
    分析需要生成测试用例的函数上下文，包括调用的函数、结构体等信息。
    """
    def __init__(self,
                 llm: LLM = None):
        Analyzer.__init__(self)

    def execute(self):
        pass
