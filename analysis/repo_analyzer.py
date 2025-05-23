from collections import defaultdict
from typing import Dict, List, Tuple

import analysis.TSED as TSED
from llm.llm import LLM
from analysis.analyzer import Analyzer
from utils.data_processor import save_json, load_json
from utils.logger import logger
from config import global_config
from apted import APTED, PerEditOperationConfig

class RepoAnalyzer(Analyzer):
    def __init__(self,
                 llm: LLM = None,
                 function_similarity_path: str = global_config['FUNCTION_SIMILARITY_PATH'],
                 function_metainfo_path: str = global_config['FUNCTION_METAINFO_PATH']
                 ):
        Analyzer.__init__(self, llm=llm)
        self.function_similarity_path = function_similarity_path
        self.function_metainfo = load_json(function_metainfo_path)

    def execute(self):
        self.calculate_all_function_similarity()

    def parse_ast(self, code: str):
        # 预解析 AST，避免重复解析
        from tree_sitter_languages import get_language, get_parser
        language = get_language("c")
        parser = get_parser("c")
        tree = parser.parse(bytes(code, encoding='UTF-8'))
        tree_str = tree.root_node.sexp()
        tree_ast = TSED.parse_tree_string(tree_str)
        tree_length = tree_str.count(")")
        return tree_ast, tree_length

    def calculate_ast_similarity(self, treeA, treeB, lenA, lenB, d=1.0, i=0.8, r=1.0):
        # 使用预解析的 AST 计算编辑距离
        max_len = max(lenA, lenB)
        apted = APTED(treeA, treeB, PerEditOperationConfig(d, i, r))
        res = apted.compute_edit_distance()
        if max_len > 0:
            return (max_len - res) / max_len if res <= max_len else 0.0
        else:
            return 1.0

    # TODO: 全部计算太慢了，或许可以优化？
    #  如果只生成一个函数的测试用例，只需要计算这个函数和其他函数的相似度
    #  但是如果要生成多个函数的测试用例，还是统一计算总用时最短（而且不会消耗LLM资源）
    def calculate_all_function_similarity(self, save: bool = True):
        n = len(self.function_metainfo)
        print(f"Calculating similarity for {n} functions")

        # 初始化每个函数的最佳匹配记录
        best_sim = {}
        for uris, func in self.function_metainfo.items():
            best_sim[uris] = {'ts_score': -1.0, 'similar_function': None}

        # 预先缓存每个函数的 AST 和树长度
        ast_cache = {}
        for uris, func in self.function_metainfo.items():
            ast_cache[uris] = self.parse_ast(func['original_string'])

        all_functions = [function for function in self.function_metainfo.values()]
        # 只比较每对函数一次（i < j），同时更新两个函数的最佳匹配信息
        for idx_a in range(n):
            functionA = all_functions[idx_a]
            treeA, lenA = ast_cache[functionA['uris']]
            for idx_b in range(idx_a + 1, n):
                functionB = all_functions[idx_b]
                treeB, lenB = ast_cache[functionB['uris']]
                ts_score = self.calculate_ast_similarity(treeA, treeB, lenA, lenB)
                # 更新 functionA 的最佳匹配
                if ts_score > best_sim[functionA['uris']]['ts_score']:
                    best_sim[functionA['uris']]['ts_score'] = ts_score
                    best_sim[functionA['uris']]['similar_function'] = functionB['uris']
                # 更新 functionB 的最佳匹配
                if ts_score > best_sim[functionB['uris']]['ts_score']:
                    best_sim[functionB['uris']]['ts_score'] = ts_score
                    best_sim[functionB['uris']]['similar_function'] = functionA['uris']
                print(f"Function {idx_a} vs. {idx_b} ts_score: {ts_score}")
        if save:
            save_json(
                file_path=self.function_similarity_path,
                data=best_sim)
            logger.info(f"{n} functions' similarity analyzed")

    def analyze_function_similarity(self, function_name, file):
        logger.info(f"Analyzing similarity for {file}.{function_name}")
        best_sim = {'ts_score': -1.0, 'similar_function': None}
        function = self.get_function(file+'.'+function_name)
        tree_1, len_1 = self.parse_ast(function['original_string'])
        for uris, func in self.function_metainfo.items():
            if uris == function['uris']:
                continue
            tree_2, len_2 = self.parse_ast(func['original_string'])
            ts_score = self.calculate_ast_similarity(tree_1, tree_2, len_1, len_2)
            if ts_score > best_sim['ts_score']:
                best_sim['ts_score'] = ts_score
                best_sim['similar_function'] = uris

        save_json(
            file_path=self.function_similarity_path,
            data={function['uris']: best_sim})
        logger.info(f"Similarity analyzed: {best_sim['similar_function']} ({best_sim['ts_score']})")
        return best_sim
