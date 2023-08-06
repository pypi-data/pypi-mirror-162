from abc import abstractmethod

from abc import ABC, abstractmethod
from typing import Any
import openai
from transformers import AutoTokenizer, AutoModelForCausalLM


class CodeGenerator(object):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate(self, *args: Any, **kwargs: Any) -> list[Any]:
        """Generate code"""
        pass


class OpenAICodeGenerator(CodeGenerator):
    def __init__(
        self, name: str, engine: str = "codex-davinci-001", temperature: int = 0
    ):
        super().__init__(name)
        self.engine = engine
        self.temperature = temperature

    def generate(
        self,
        prompt: str,
        max_tokens: int = 200,
        best_of: int = 1,
        frequency_penalty: int = 0,
        n: int = 10,
        suffix: str = None,
        presence_penalty: int = 0,
    ) -> list[Any]:
        engine = self.engine
        prompt = prompt
        if suffix is not None:
            engine = "code-davinci-002"
            # prompt = prompt + "[insert]"
        # print(f"\n**************\nGenerating code for prompt:\n {repr(prompt)}")
        # print(f"\n**************\nUsing suffix:\n {repr(suffix)}")
        response: list[Any] = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=max_tokens,
            # top_p=1,
            # logprobs=1,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            suffix=suffix,
            n=n,
        )
        return response


class HFCodeGenerator(CodeGenerator):
    def __init__(self, name: str, model: str = "Salesforce/codegen-350M-multi"):
        super().__init__(name)
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(model)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 200,
        best_of: int = 1,
        frequency_penalty: int = 0,
        n: int = 10,
        suffix: str = None,
        presence_penalty: int = 0,
        temperature: float = 0.2,
    ):
        prompt_tokens = self.tokenizer(prompt, return_tensors="pt")
        generations = self.model.generate(
            prompt_tokens.input_ids,
            max_length=max_tokens,
            do_sample=True,
            temperature=temperature,
            num_return_sequences=n,
            attention_mask=prompt_tokens.attention_mask,
        )
        completions = [
            self.tokenizer.decode(
                generation, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            for generation in generations
        ]
        return completions
