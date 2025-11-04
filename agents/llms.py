import openai
import os
from markdown import markdown
from enum import Enum
from dotenv import load_dotenv
from logging import info, error

from openai.types.chat import ChatCompletionMessageParam

_ = load_dotenv()

open_router_api_key = os.getenv("OPEN_ROUTER_API_KEY")
ollama_api_key = os.getenv("OLLAMA_API_KEY")

# ollama_client = openai.OpenAI(api_key=ollama_api_key, base_url="http://localhost:11434/v1/")
ollama_client = openai.OpenAI(api_key="ollama", base_url="http://localhost:11434/v1/")
# ollama_client = openai.OpenAI(api_key=ollama_api_key, base_url="http://ollama.com")
open_router_client = openai.OpenAI(
    api_key=open_router_api_key, base_url="https://openrouter.ai/api/v1"
)

if open_router_api_key:
    print(f"Open Router API Key available, starting with {open_router_api_key[:8]}")

if ollama_api_key:
    print(f"Ollama API Key available, starting with {ollama_api_key[:8]}")


class LLM_Model(Enum):
    GPT_41_MINI = "gpt-4.1-mini"
    GPT_OSS_OLLAMA = "gpt-oss:20b-cloud"
    GPT_OSS_OPEN = "openai/gpt-oss-20b"
    DEEPSEEK_V3 = "deepseek/deepseek-chat-v3-0324"
    DEEPSEEK_V3_OLLAMA = "deepseek-v3.1:671b-cloud"


class Text_Generator:
    def __init__(self, model: LLM_Model, llm_client: openai.OpenAI = ollama_client):
        self.llm_client: openai.OpenAI = llm_client

        # Adjust model for client compatibility: map GPT_OSS_OPEN to GPT_OSS_OLLAMA for Ollama,
        # and vice versa for Open Router
        if llm_client is ollama_client:
            if model is LLM_Model.GPT_OSS_OPEN:
                model = LLM_Model.GPT_OSS_OLLAMA
        elif llm_client is open_router_client:
            if model is LLM_Model.GPT_OSS_OLLAMA:
                model = LLM_Model.GPT_OSS_OPEN

        self.model: LLM_Model = model

        info(f"[Text Generator] Ollama client set up with model {self.model}")
        info(f"[Text Generator] Open Router client set up with model {self.model}")

    def generate_text(
        self,
        messages: list[ChatCompletionMessageParam],
        temperature: float = 0.8,
        max_tokens: int = 200,
    ) -> str | None:
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model.value,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            error(f"Something went wrong while generating text: {e}")
            return ""

    def generate_streaming_text(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.8,
        max_tokens: int = 200,
    ) -> str | None:
        stream = self.llm_client.chat.completions.create(
            model=self.model.value,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        response = ""
        for chunk in stream:
            response += chunk.choices[0].delta.content
        return response

    def generate_text_with_system_prompt(
        self, prompt: str, system_prompt: str, role: str = "user"
    ) -> str | None:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": role, "content": prompt},
        ]
        return self.generate_text(messages)

    def generate_streaming_text_with_system_prompt(
        self, prompt: str, system_prompt: str, role: str = "user"
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": role, "content": prompt},
        ]
        return self.generate_streaming_text(messages)

    def format_with_markdown(self, text: str) -> str:
        return markdown(text)
