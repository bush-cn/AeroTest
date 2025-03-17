from config import FILE_PATH
from prompt.utgen import Prompt
from llm.deepseek_llm import DeepSeekLLM

def load_cpp_file(file_path):
    """读取 C++ 文件并返回其内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        cpp_code = file.read()
    return cpp_code

def generate_unit_test(cpp_code):
    """生成单元测试代码"""
    # 创建 DeepSeekLLM 实例
    llm = DeepSeekLLM()

    # 拼接完整的提示词
    prompt = Prompt + cpp_code

    # 调用 LLM 生成单元测试
    response = llm.chat(
        system_prompt="You are a helpful assistant",
        user_input=prompt
    )
    return response

def save_unit_test(result):
    """将生成的单元测试代码保存到文件"""
    output_path = "result/UnitTest.cpp"
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(result)

def main():
    # 1. 加载 C++ 文件内容
    cpp_code = load_cpp_file(FILE_PATH)

    # 2. 调用 LLM 生成单元测试代码
    unit_test_code = generate_unit_test(cpp_code)

    # 3. 保存生成的单元测试代码
    save_unit_test(unit_test_code)
    print("Unit test code has been saved to result/UnitTest.cpp")

if __name__ == "__main__":
    main()
