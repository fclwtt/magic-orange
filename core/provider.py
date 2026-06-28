"""LLMProvider — OpenAI SDK 封装"""

from __future__ import annotations
import json, logging, time, openai
from typing import Any
from openai import OpenAI
from interfaces.iprovider import ILLMProvider
from interfaces.iconfig import IConfigStore

logger = logging.getLogger(__name__)

class OpenAIProvider(ILLMProvider):
    def __init__(self, config: IConfigStore):
        self._config = config
        self._model = config.get("model", "gpt-4")
        api_key = config.get("api_key", "") or ""
        base_url = config.get("base_url", "https://api.openai.com/v1")
        kw: dict = {}
        if api_key: kw["api_key"] = api_key
        if base_url: kw["base_url"] = base_url
        self._client = OpenAI(**kw)

    @property
    def model(self) -> str: return self._model

    def chat_completion(self, messages: list[dict], tools: list[dict] | None = None, **kw) -> dict[str, Any]:
        params = {"model": self._model, "messages": messages}
        if tools: params["tools"] = tools
        params.update(kw)

        for attempt in range(3):
            try:
                resp = self._client.chat.completions.create(**params)
                choice = resp.choices[0]
                msg = choice.message
                result = {"role": "assistant", "content": msg.content or ""}
                if msg.tool_calls:
                    result["tool_calls"] = [
                        {"id": tc.id, "type": "function",
                         "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in msg.tool_calls]
                return result
            except openai.RateLimitError:
                time.sleep(2 ** attempt)
            except (openai.APIError, openai.APITimeoutError, openai.APIConnectionError) as e:
                if attempt < 2: time.sleep(1.0)
                else: raise
        raise RuntimeError("LLM call failed")
