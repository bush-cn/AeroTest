import warnings
from tree_sitter_languages import get_language, get_parser  # noqa: E402
from source_parser.parsers.language_parser import previous_sibling
from source_parser.parsers.commentutils import strip_c_style_comment_delimiters

warnings.filterwarnings("ignore", category=FutureWarning)


def _get_docstring_before(node, root_node, parent_node=None):
    """返回紧邻 node 之前的注释节点"""
    if parent_node is None:
        parent_node = root_node
    prev_sib = previous_sibling(node, parent_node)
    if prev_sib is None:
        return None
    if prev_sib.type == 'comment':
        return prev_sib
    return None


def extract_global_variables(source_code):
    language = get_language("c")
    parser = get_parser("c")
    source_bytes = bytes(source_code, 'utf8')
    tree = parser.parse(source_bytes)
    root = tree.root_node

    global_vars = []

    # 函数声明匹配查询
    func_query = language.query("""
    (declaration
        declarator: (function_declarator) @func
    ) @func_decl
    """)

    # 变量声明匹配查询
    var_query = language.query("""
    (declaration
        declarator: (_) @declarator
    ) @var_decl
    """)

    # 遍历语法树
    for node in root.children:
        if node.type != 'declaration':
            continue

        # 过滤函数声明
        if func_query.captures(node):
            continue

        # 获取完整声明语句
        decl_text = source_bytes[node.start_byte:node.end_byte].decode('utf8').strip()

        # 注释
        comment_node = _get_docstring_before(node, root_node=root)
        doc_string = source_bytes[comment_node.start_byte:comment_node.end_byte].decode(
            'utf8').strip() if comment_node else ""
        doc_string = (
            strip_c_style_comment_delimiters(doc_string).strip()
            if comment_node else ""
        )

        type_node = node.child_by_field_name('type')
        type_text = source_bytes[type_node.start_byte:type_node.end_byte].decode('utf8') if type_node else ""

        # 提取变量名
        var_matches = var_query.captures(node)
        for v_node, v_name in var_matches:
            if v_name == 'declarator':
                if name := extract_identifier(v_node):
                    global_vars.append({
                        'name': name,
                        'type': type_text,
                        'original_string': decl_text,
                        'docstring': doc_string
                    })

    return global_vars


def extract_identifier(node):
    """递归提取标识符名称"""
    if node.type == 'identifier':
        return node.text.decode('utf8')
    for child in node.children:
        if res := extract_identifier(child):
            return res
    return None
