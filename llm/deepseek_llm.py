from openai import OpenAI
from dotenv import load_dotenv
import os

from llm.llm import LLM

# Load environment variables from .env file
load_dotenv()

# DEEPSEEK_MODEL = "deepseek-v3-241226"
# DEEPSEEK_MODEL = "deepseek-r1"
DEEPSEEK_MODEL = "deepseek-v3"

class DeepSeekLLM(LLM):
    def __init__(self, api_key=None,
                 api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"):  # https://ark.cn-beijing.volces.com/api/v3
        super().__init__()
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base,
        )
        self.history = []

    def __str__(self) -> str:
        return "DeepSeek"

    def chat(self, system_prompt, user_input, model=DEEPSEEK_MODEL, max_tokens=4096, temperature=0, stream=True):
        history_openai_format = [{"role": "system", "content": system_prompt},
                                 {"role": "user", "content": user_input}]

        response_stream = self.client.chat.completions.create(
            model=model,
            messages=history_openai_format,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
        )

        return self._process_stream(response_stream)

    def chat_with_history(self, user_input, system_prompt=None, model=DEEPSEEK_MODEL, max_tokens=4096, temperature=0,
                          stream=True):
        if system_prompt is None:
            assert self.history, "system_prompt must be provided for the first message"
        else:
            self.clear_history()
            self.history.append({"role": "system", "content": system_prompt})

        self.history.append({"role": "user", "content": user_input})

        response_stream = self.client.chat.completions.create(
            model=model,
            messages=self.history,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
        )

        full_response = self._process_stream(response_stream)
        self.history.append({"role": "system", "content": full_response})
        return full_response

    def clear_history(self):
        self.history = []

    @staticmethod
    def _process_stream(stream):
        full_response = ""
        is_answering = False
        for chunk in stream:
            # content = chunk.choices[0].delta.content or ""
            # print(content, end="", flush=True)
            # full_response += content
            if not chunk.choices:
                print("\nUsage:")
                print(chunk.usage)
            else:
                delta = chunk.choices[0].delta
                # 打印思考过程
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                    print(delta.reasoning_content, end='', flush=True)
                    # reasoning_content += delta.reasoning_content
                else:
                    # 开始回复
                    if delta.content != "" and is_answering is False:
                        print("\n" + "=" * 20 + "Response" + "=" * 20 + "\n")
                        is_answering = True
                    # 打印回复过程
                    print(delta.content, end='', flush=True)
                    full_response += delta.content
        print("\n")
        return full_response


if __name__ == "__main__":
    # Example usage
    deepseek_llm = DeepSeekLLM()
    response = deepseek_llm.chat(
        system_prompt="You are a helpful assistant",
        user_input="Hello"
    )
    print("Final Response:", response)
