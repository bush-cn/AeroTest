from typing import List, Tuple
from source_parser.parsers.language_parser import (
    LanguageParser,
    has_correct_syntax,
    children_of_type,
    traverse_type,
    previous_sibling,
)
from source_parser.parsers.commentutils import strip_c_style_comment_delimiters


class CParser(LanguageParser):
    """
    C 语言解析器，将源码解析为结构化数据，包括函数定义和结构体信息。
    其中将结构体（struct）当作类处理，函数当作方法。
    """
    _function_types = ("function_definition",)
    _user_defined_types = (
        "struct_specifier",
        "enum_specifier",
        "union_specifier",
        "type_definition",
    )
    _import_types = (
        "preproc_include",
        "preproc_def",
    )
    _docstring_types = ("comment",)
    _include_patterns = "*.h", "*.c"

    def update(self, file_contents):
        """更新待解析的源码内容"""
        self.file_bytes = file_contents.encode("utf-8")
        self.tree = self.parser.parse(self.file_bytes)

    @classmethod
    def get_lang(cls):
        return "c"

    @property
    def file_docstring(self):
        """返回文件中第一个注释"""
        file_docstring = ""
        if not self.tree.root_node.children:
            return file_docstring
        for child in self.tree.root_node.children:
            if child.type != "comment":
                break
            file_docstring += self.span_select(child) + "\n"
        return strip_c_style_comment_delimiters(file_docstring).strip()

    @property
    def file_context(self) -> List[str]:
        """返回文件级预处理指令信息"""
        file_context_nodes = children_of_type(self.tree.root_node, self._import_types)
        return [self.span_select(node).strip() for node in file_context_nodes]

    @property
    def class_nodes(self):
        """
        返回所有用户定义类型（UDTs）节点
        匿名struct、union、enum不计入，且inner_types字段处理在对应的typedef中
        而具名的struct、union、enum则计入，与typedef独立为两个节点
        """
        nodes = []
        try:
            all_nodes = []
            traverse_type(self.tree.root_node, all_nodes, self._user_defined_types)
            # 过滤掉没有 body 的标识符节点，以及没有 name
            nodes = [node for node in all_nodes
                     if node.type == "type_definition" or (
                             node.child_by_field_name("body") is not None and node.child_by_field_name("name") is not None)]
        except RecursionError:
            pass
        return nodes

    @property
    def method_nodes(self):
        """
        返回所有函数定义节点。
        同样采用 traverse_type 遍历整个 AST 来获取所有 function_definition 节点。
        """
        nodes = []
        try:
            traverse_type(self.tree.root_node, nodes, self._function_types)
        except RecursionError:
            pass
        return nodes

    def _get_docstring_before(self, node, parent_node=None):
        """返回紧邻 node 之前的注释节点"""
        if parent_node is None:
            parent_node = self.tree.root_node
        prev_sib = previous_sibling(node, parent_node)
        if prev_sib is None:
            return None
        if prev_sib.type in self._docstring_types:
            return prev_sib
        return None

    def _get_signature(self, function_node):
        """返回函数签名字符串（不包含函数体）"""
        nodes = []
        for child in function_node.children:
            if child.type == "compound_statement":
                return self.span_select(*nodes, indent=False) if nodes else ""
            nodes.append(child)
        return self.span_select(*nodes, indent=False) if nodes else ""

    def _parse_function_node(self, function_node):
        """解析函数定义节点，返回函数的结构化信息"""
        result = {
            "original_string": self.span_select(function_node, indent=False),
            # "byte_span": (function_node.start_byte, function_node.end_byte),
            # "start_point": (
            #     self.starting_point + function_node.start_point[0],
            #     function_node.start_point[1]
            # ),
            # "end_point": (
            #     self.starting_point + function_node.end_point[0],
            #     function_node.end_point[1]
            # ),
            "signature": self._get_signature(function_node),
            "attributes": {
                "annotations": []
            }
        }
        comment_node = self._get_docstring_before(function_node)
        result["docstring"] = (
            strip_c_style_comment_delimiters(self.span_select(comment_node, indent=False)).strip()
            if comment_node else ""
        )
        body_node = function_node.child_by_field_name("body")
        result["body"] = self.span_select(body_node, indent=False) if body_node else ""
        declarator_node = function_node.child_by_field_name("declarator")
        type_node = function_node.child_by_field_name("type")
        base_type = (self.span_select(type_node, indent=False) if type_node else "") + " "
        #   处理指针函数的情况，即int *foo返回值应为int *
        while declarator_node.type == "pointer_declarator":
            base_type += "*"
            declarator_node = declarator_node.child_by_field_name("declarator")

        name_node = declarator_node.child_by_field_name("declarator") if declarator_node else None
        result["name"] = self.span_select(name_node, indent=False) if name_node else ""
        result["attributes"]["return_type"] = base_type.strip()
        # 解析 static、inline 以及 const 等修饰符
        for child in function_node.children:
            if child.type in ["storage_class_specifier", "inline"]:
                result["attributes"]["annotations"].append(self.span_select(child, indent=False))
            elif child.type == "function_declarator":
                if child.children and child.children[-1].type == "type_qualifier":
                    result["attributes"]["annotations"].append(self.span_select(child.children[-1], indent=False))
                break

        # 解析参数列表：
        params = []
        if declarator_node:
            parameters_node = declarator_node.child_by_field_name("parameters")
            if parameters_node:
                # 遍历参数列表节点下的每个 parameter_declaration 节点
                for param in parameters_node.children:
                    if param.type != "parameter_declaration":
                        continue
                    # 使用全文本作为参数原始字符串
                    param_text = self.span_select(param, indent=False)
                    # 由于存在int *a, char c[]这种情况，这里的处理方法是将标识符去掉即得到参数类型
                    # 递归查找 identifier 节点
                    declarator = param.child_by_field_name("declarator")
                    while declarator and declarator.type != "identifier":
                        declarator = declarator.child_by_field_name("declarator")
                    param_name = self.span_select(declarator, indent=False)
                    # # 计算相对于父节点字符串的偏移量
                    # offset_start = declarator.start_byte - param.start_byte
                    # offset_end = declarator.end_byte - param.start_byte
                    # param_type = param_text[:offset_start] + param_text[offset_end:]
                    # 或者直接将字符串末尾的标识符去掉？
                    param_type = param_text[:param_text.rfind(param_name)].strip()
                    params.append({
                        "original_string": param_text,
                        "type": param_type,
                        "name": param_name
                    })
        result["parameters"] = params
        # try:
        #     result["syntax_pass"] = has_correct_syntax(function_node)
        # except RecursionError:
        #     result["syntax_pass"] = False
        return result

    def _parse_udt_node(self, udt_node):
        """
        解析用户定义类型（UDT）节点，返回结构化信息。
        name字段是后续检索的键，如 struct s, union u, typedef_t（TODO: 加速检索？）
        若为 typedef，新增typedef字段，指向所定义的类型源字符串，如struct s, int
        """
        result = {
            "original_string": self.span_select(udt_node, indent=False),
            # "byte_span": (udt_node.start_byte, udt_node.end_byte),
            # "start_point": (
            #     self.starting_point + udt_node.start_point[0],
            #     udt_node.start_point[1]
            # ),
            # "end_point": (
            #     self.starting_point + udt_node.end_point[0],
            #     udt_node.end_point[1]
            # ),
            # "attributes": {
            #     "annotations": [],
            #     "fields": []
            # }
        }
        comment_node = self._get_docstring_before(udt_node)
        result["docstring"] = (
            strip_c_style_comment_delimiters(self.span_select(comment_node, indent=False)).strip()
            if comment_node else ""
        )
        # 处理typedef
        if udt_node.type == "type_definition":
            typedef_name_node = udt_node.child_by_field_name("declarator")
            result['name'] = self.span_select(typedef_name_node, indent=False) if typedef_name_node else ""
            typedef_original_type_node = udt_node.child_by_field_name("type")
            result['typedef'] = self.span_select(typedef_original_type_node, indent=False) \
                if typedef_original_type_node else ""
            # 若为具名UDT，则直接返回，因为具名UDT会被再解析一遍
            if typedef_original_type_node.child_by_field_name("name") is not None:
                return result
            # 若为匿名UDT，匿名UDT不解析，与此typedef合并
            else:
                udt_node = typedef_original_type_node

        name_node = udt_node.child_by_field_name("name")
        if name_node is not None:
            udt_name = self.span_select(name_node, indent=False)
            if udt_node.type == "struct_specifier":
                udt_name = "struct " + udt_name
            elif udt_node.type == "enum_specifier":
                udt_name = "enum " + udt_name
            elif udt_node.type == "union_specifier":
                udt_name = "union " + udt_name
            result["name"] = udt_name.strip()
        # 否则是匿名UDT，上面已将name字符置为typedef值

        body_node = udt_node.child_by_field_name("body")
        fields = []
        if body_node and body_node.children:
            for field in body_node.children:
                if field.type != "field_declaration":
                    continue
                # field_dict = {
                #                 "original_string": self.span_select(field, indent=False),
                #                 "annotations": []
                # }
                # comment_node = self._get_docstring_before(field, body_node)
                # field_dict["docstring"] = (
                #     strip_c_style_comment_delimiters(self.span_select(comment_node, indent=False)).strip()
                #     if comment_node else ""
                # )
                type_node = field.child_by_field_name("type")
                type_name = self.span_select(type_node, indent=False) if type_node else ""
                fields.append(type_name)
                # field_dict["type"] = self.span_select(type_node, indent=False) if type_node else ""

        #         if field.children and field.children[0].type == "storage_class_specifier":
        #             field_dict["annotations"].append(self.span_select(field.children[0], indent=False))
        #         try:
        #             field_dict["syntax_pass"] = has_correct_syntax(field)
        #         except RecursionError:
        #             field_dict["syntax_pass"] = False
        #         fields.append(field_dict)
        #     result["attributes"]["fields"] = fields
        # try:
        #     result["syntax_pass"] = has_correct_syntax(udt_node)
        # except RecursionError:
        #     result["syntax_pass"] = False
        # # 解析嵌套的结构体（如果有）
        # nested_structs = []
        # if body_node:
        #     for child in body_node.children:
        #         if child.type in self._struct_types:
        #             nested_structs.append(self._parse_struct_node(child))
        # result["structs"] = nested_structs
        result["inner_types"] = fields
        return result

    # --- 实现抽象方法和属性 ---
    @property
    def class_types(self):
        """将结构体当作类来处理，返回对应的节点类型"""
        return self._user_defined_types

    @property
    def method_types(self):
        return self._function_types

    @property
    def import_types(self):
        return self._import_types

    @property
    def include_patterns(self):
        return self._include_patterns

    def _parse_class_node(self, node, parent_node=None):
        return self._parse_udt_node(node)

    def _parse_method_node(self, node, parent_node=None):
        return self._parse_function_node(node)

    # 以下辅助函数保持一致

    def _find_variable_declarations(self, node, variable_types):
        if node.type == 'declaration':
            type_node = node.child_by_field_name('type')
            declarator_node = node.child_by_field_name('declarator')
            if type_node and declarator_node:
                type_name = self.span_select(type_node)
                variable_name = self.span_select(declarator_node.child_by_field_name('declarator'))
                variable_types[variable_name] = type_name
        for child in node.children:
            self._find_variable_declarations(child, variable_types)

    def _find_function_calls(self, node, function_calls, variable_types):
        if node.type == 'call_expression':
            function_node = node.child_by_field_name('function')
            function_name = self.span_select(function_node)
            if function_node.type == 'field_expression':
                object_node = function_node.child_by_field_name('object')
                if object_node and object_node.type == 'identifier':
                    object_name = self.span_select(object_node)
                    if object_name in variable_types:
                        function_name = variable_types[object_name] + '::' + function_name
            function_calls.add(function_name)
        for child in node.children:
            self._find_function_calls(child, function_calls, variable_types)

    def find_function_calls_in_code(self, code):
        self.update(code)
        function_calls = set()
        variable_types = {}
        self._find_variable_declarations(self.tree.root_node, variable_types)
        self._find_function_calls(self.tree.root_node, function_calls, variable_types)
        return function_calls

    def _find_function_definitions(self, node, function_definitions):
        if node.type == 'function_definition':
            function_name_node = node.child_by_field_name('declarator').child_by_field_name('declarator')
            function_name = self.span_select(function_name_node)
            function_definitions.add(function_name)
        for child in node.children:
            self._find_function_definitions(child, function_definitions)

    def find_function_definitions_in_code(self, code):
        self.update(code)
        function_definitions = set()
        self._find_function_definitions(self.tree.root_node, function_definitions)
        return function_definitions
