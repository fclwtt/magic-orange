from __future__ import annotations
from typing import Any, Protocol

class ILLMProvider(Protocol):
    @property
    def model(self) -> str: ...
    def chat_completion(self, messages: list[dict], tools: list[dict] | None = None, **kw) -> dict[str, Any]: ...
