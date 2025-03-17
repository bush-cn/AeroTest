def get_method_canonical_uri(relative_path, class_name=None, method_name=None):
    path = relative_path.strip('.py').replace('/', '.')
    if class_name:
        return f'{path}.{class_name}.{method_name}'
    return f'{path}.{method_name}'

def resolve_relative_import(current_module, relative_import):
    current_module_path = current_module.strip('.py').replace('/', '.')
    relative_parts = relative_import.split('.')
    depth = len([part for part in relative_parts if part == ''])
    
    # 计算绝对路径
    base_module = '.'.join(current_module_path.split('.')[:-depth])
    resolved_path = f'{base_module}.' + '.'.join([part for part in relative_parts if part != ''])
    
    return resolved_path

def get_method_alias_uris(relative_path, class_name=None, method_name=None, import_path=None):
    path = relative_path.strip('.py').replace('/', '.')
    aliases = []
    
    if import_path:
        # 如果方法通过__init__.py或其他模块导入
        import_module = import_path.strip('.py').replace('/', '.')
        if class_name:
            aliases.append(f'{import_module}.{class_name}.{method_name}')
        else:
            aliases.append(f'{import_module}.{method_name}')
    
    # 处理 __init__.py 特例
    if path.endswith('.__init__'):
        package_path = path.rstrip('.__init__')
        if class_name:
            aliases.append(f'{package_path}.{class_name}.{method_name}')
        else:
            aliases.append(f'{package_path}.{method_name}')
    
    return aliases


def get_method_uris(relative_path, class_name=None, method_name=None, import_path=None, current_module=None, relative_import=None):
    """
    生成给定方法或函数的 URI，包括 Canonical URI 和 Alias URIs。

    参数：
    ----------
    
    relative_path : str
        方法或函数所在文件的相对路径（相对于仓库根目录）。用于生成 Canonical URI 的模块路径部分。
    
    class_name : str, 可选
        如果方法属于某个类，则为类的名称。
    
    method_name : str, 可选
        方法或函数的名称。用于生成 URI 的方法或函数名部分。
    
    import_path : str, 可选
        导入路径，表示该方法或函数可能被导入到的其他模块路径。用于生成 Alias URI。
    
    current_module : str, 可选
        当前模块的相对路径（相对于仓库根目录），用于解析相对引用。
    
    relative_import : str, 可选
        相对导入路径，通常以 `.` 或 `..` 开头。用于解析并生成绝对导入路径的 Alias URI。
    
    返回值：
    ----------
    tuple
        包含 Canonical URI 和 Alias URIs 的元组。
        - Canonical URI (str): 方法或函数的标准 URI。
        - Alias URIs (list): 方法或函数可能的其他 URI 别名列表。
    
    示例：
    ----------
    >>> get_method_uris(
            is_in_class=False, 
            relative_path='source_parser/some_module.py', 
            method_name='load_zip_json',
            import_path='source_parser/__init__.py'
        )
    ('source_parser.some_module.load_zip_json', 
     ['source_parser.load_zip_json'])
    
    逻辑：
    ----------
    1. Canonical URI:
       使用 `relative_path`、`class_name` 和 `method_name` 生成唯一的 Canonical URI。
    
    2. Alias URIs:
       使用 `import_path` 生成导入路径对应的 Alias URI。
    
    3. 相对引用解析:
       如果提供了 `relative_import` 和 `current_module`，解析相对导入路径，并添加解析后的路径作为 Alias URI。
    """
    
    # 生成Canonical URI
    canonical_uri = get_method_canonical_uri(relative_path, class_name, method_name)
    
    # 生成Alias URIs
    alias_uris = get_method_alias_uris(relative_path, class_name, method_name, import_path)
    
    # 解析相对引用
    if relative_import and current_module:
        resolved_import = resolve_relative_import(current_module, relative_import)
        alias_uris.append(f'{resolved_import}.{method_name}')
    
    return [canonical_uri] + alias_uris
    # return canonical_uri, alias_uris

def get_class_canonical_uri(relative_path, class_name):
    path = relative_path.strip('.py').replace('/', '.')
    return f'{path}.{class_name}'

def get_class_uris(relative_path, class_name, import_path=None, current_module=None, relative_import=None):
    """
    生成给定类的 URI，包括 Canonical URI 和 Alias URIs。

    参数：
    ----------
    relative_path : str
        类所在文件的相对路径（相对于仓库根目录）。用于生成 Canonical URI 的模块路径部分。

    class_name : str
        类的名称。

    import_path : str, 可选
        导入路径，表示该类可能被导入到的其他模块路径。用于生成 Alias URI。

    current_module : str, 可选
        当前模块的相对路径（相对于仓库根目录），用于解析相对引用。

    relative_import : str, 可选
        相对导入路径，通常以 `.` 或 `..` 开头。用于解析并生成绝对导入路径的 Alias URI。

    返回值：
    ----------
    tuple
        包含 Canonical URI 和 Alias URIs 的元组。
        - Canonical URI (str): 类的标准 URI。
        - Alias URIs (list): 类可能的其他 URI 别名列表。

    示例：
    ----------
    >>> get_class_uris(
            relative_path='source_parser/some_module.py',
            class_name='DataProcessor',
            import_path='source_parser/__init__.py'
        )
    ('source_parser.some_module#DataProcessor', 
     ['source_parser#DataProcessor'])
    """
    
    # 生成Canonical URI
    canonical_uri = get_class_canonical_uri(relative_path, class_name)

    # 生成Alias URIs
    alias_uris = []
    if import_path:
        import_module = import_path.strip('.py').replace('/', '.')
        alias_uris.append(f'{import_module}.{class_name}')
    
    # 处理 __init__.py 特例
    if relative_path.endswith('__init__.py'):
        package_path = relative_path.rstrip('.__init__.py').replace('/', '.')
        alias_uris.append(f'{package_path}.{class_name}')
    
    # 解析相对引用
    if relative_import and current_module:
        resolved_import = resolve_relative_import(current_module, relative_import)
        alias_uris.append(f'{resolved_import}.{class_name}')

    return [canonical_uri] + alias_uris


if __name__ == '__main__':
    # # 定义在 __init__.py 中的函数：
    # uris = get_method_uris(
    #     relative_path='source_parser/__init__.py',
    #     method_name='load_zip_json'
    # )

    # # 从其他模块导入的函数：
    # canonical_uri, alias_uris = get_method_uris(
    #     is_in_class=False,
    #     relative_path='source_parser/some_module.py',
    #     method_name='load_zip_json',
    #     import_path='source_parser/__init__.py'
    # )

    # # 处理相对引用：
    # canonical_uri, alias_uris = get_method_uris(
    #     is_in_class=False,
    #     relative_path='utils/helper.py',
    #     method_name='calculate_checksum',
    #     current_module='utils/helper.py',
    #     relative_import='.submodule'
    # )
    
    uris = get_class_uris(
        relative_path='source_parser/some_module.py',
        class_name='DataProcessor',
        import_path='source_parser/__init__.py',
        current_module='source_parser/some_module.py',
        relative_import='..helpers'
    )

    print(uris)