from abc import ABC, abstractmethod
import tiktoken

class LLM(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def chat(self, system_prompt, user_input, model=None, max_tokens=4096, temperature=0, stream=True):
        pass

    def calculate_tokens(self, messages, model):
        tokenizer = tiktoken.get_encoding("cl100k_base")  # This is an example; replace with the actual encoding used by your model
        total_tokens = 0
        for message in messages:
            content = message["content"]
            tokens = tokenizer.encode(content)
            total_tokens += len(tokens)
        return total_tokens