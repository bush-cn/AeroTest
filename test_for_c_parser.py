import os
import json
from tree_sitter import Language, Parser

def get_field(node):
    """通过遍历父节点的 children 获取当前节点对应的 field_name。"""
    if not node.parent:
        return None
    for i, child in enumerate(node.parent.children):
        if child == node:
            return node.parent.field_name_for_child(i)
    return None

def node_to_dict(node):
    """递归地将 tree-sitter 节点转换为字典，用于 JSON 输出。"""
    result = {
        'type': node.type,
        # 'start_point': node.start_point,
        # 'end_point': node.end_point,
        'children': [node_to_dict(child) for child in node.children] if node.children else []
    }
    field = get_field(node)
    if field:
        result['field'] = field
    return result


def node_to_string(node, indent=0):
    """递归地将 tree-sitter 节点转换为缩进格式的字符串，直观显示树状结构。"""
    indent_str = '  ' * indent
    result = f"{indent_str}{node.type} [{node.start_point} - {node.end_point}]\n"
    for child in node.children:
        result += node_to_string(child, indent + 1)
    return result


def output_json_tree(tree, output_filename):
    tree_dict = node_to_dict(tree.root_node)
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(tree_dict, f, indent=4)
    print(f"JSON 格式的语法树已输出到文件 {output_filename}")


def output_text_tree(tree, output_filename):
    tree_text = node_to_string(tree.root_node)
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(tree_text)
    print(f"缩进文本格式的语法树已输出到文件 {output_filename}")


def main():
    # 定义生成的语言库文件路径
    LIB_PATH = 'build/my-languages.so'

    # 如果语言库不存在，则构建语言库
    if not os.path.exists(LIB_PATH):
        os.makedirs('build', exist_ok=True)
        # 检查 tree-sitter-c 目录是否存在
        if not os.path.exists('tree-sitter-c'):
            print("错误：未找到 'tree-sitter-c' 目录，请先使用 git 克隆该仓库：")
            print("git clone https://github.com/tree-sitter/tree-sitter-c.git")
            return
        print("构建语言库...")
        Language.build_library(
            # 输出的共享库文件路径
            LIB_PATH,
            # 指定需要包含的语言语法目录（这里是 C 语言）
            ['tree-sitter-c']
        )

    # 加载 C 语言
    C_LANGUAGE = Language(LIB_PATH, 'c')

    # 创建解析器并设置语言
    parser = Parser()
    parser.set_language(C_LANGUAGE)

    # 读取当前目录下的 test.c 文件
    try:
        with open('test_c_file.c', 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print("错误：未找到 test.c 文件。")
        return

    # 解析源代码
    tree = parser.parse(source_code.encode('utf8'))

    # # 1. 输出为 s-expression 格式文件
    # with open('test_output_sexp', 'w', encoding='utf-8') as f:
    #     f.write(tree.root_node.sexp())
    # print("s-expression 格式的语法树已输出到文件 test_output_sexp")

    # 2. 输出为 JSON 格式文件
    output_json_tree(tree, 'test_output_json.json')

    # # 3. 输出为自定义缩进文本格式文件
    # output_text_tree(tree, 'test_output_text')


if __name__ == '__main__':
    main()
