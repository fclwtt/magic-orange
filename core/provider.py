"""LLMProvider — OpenAI SDK 封装 (Hermes-style: proxy-aware, classified errors, jittered retry)"""

from __future__ import annotations
import json, logging, os, random, time, openai
from typing import Any
from openai import OpenAI
from interfaces.iprovider import ILLMProvider
from interfaces.iconfig import IConfigStore

logger = logging.getLogger(__name__)


def _get_proxy_from_env() -> str | None:
    """Read proxy from environment (Hermes-style multi-var probing)."""
    for key in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY",
                "https_proxy", "http_proxy", "all_proxy"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return None


def _jittered_backoff(attempt: int, base: float = 2.0, max_delay: float = 60.0) -> float:
    """Exponential backoff with decorrelated jitter (Hermes pattern)."""
    delay = min(base * (2 ** max(0, attempt - 1)), max_delay)
    jitter = random.uniform(0, delay * 0.5)
    return delay + jitter


class OpenAIProvider(ILLMProvider):
    def __init__(self, config: IConfigStore):
        self._config = config
        self._model = config.get("model", "gpt-4")
        api_key = config.get("api_key", "") or ""
        base_url = config.get("base_url", "https://api.openai.com/v1")
        kw: dict = {}
        if api_key:
            kw["api_key"] = api_key
        if base_url:
            kw["base_url"] = base_url

        # ── Inject proxy into httpx client (Hermes pattern) ──
        proxy_url = _get_proxy_from_env()
        if proxy_url:
            import httpx
            kw["http_client"] = httpx.Client(proxy=proxy_url, timeout=60.0)
            logger.info("Using proxy: %s", proxy_url.split("@")[-1] if "@" in proxy_url else proxy_url)
        else:
            logger.debug("No proxy configured — direct connection")

        self._client = OpenAI(**kw)
        self._max_retries = config.get("max_retries", 3)

    @property
    def model(self) -> str:
        return self._model

    def chat_completion(self, messages: list[dict], tools: list[dict] | None = None, **kw) -> dict[str, Any]:
        params = {"model": self._model, "messages": messages}
        if tools:
            params["tools"] = tools
        params.update(kw)

        last_error = None
        for attempt in range(self._max_retries):
            try:
                resp = self._client.chat.completions.create(**params)
                choice = resp.choices[0]
                msg = choice.message
                result = {"role": "assistant", "content": msg.content or ""}
                if msg.tool_calls:
                    result["tool_calls"] = [
                        {"id": tc.id, "type": "function",
                         "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in msg.tool_calls
                    ]
                return result

            except json.JSONDecodeError as e:
                last_error = e
                logger.warning("API returned non-JSON response (attempt %d/%d): %s",
                               attempt + 1, self._max_retries, e)
                if attempt < self._max_retries - 1:
                    time.sleep(_jittered_backoff(attempt))

            except openai.RateLimitError as e:
                last_error = e
                delay = _jittered_backoff(attempt, base=5.0, max_delay=120.0)
                logger.warning("Rate limited (attempt %d/%d), waiting %.1fs",
                               attempt + 1, self._max_retries, delay)
                time.sleep(delay)

            except openai.APITimeoutError as e:
                last_error = e
                logger.warning("API timeout (attempt %d/%d)", attempt + 1, self._max_retries)
                if attempt < self._max_retries - 1:
                    time.sleep(_jittered_backoff(attempt))

            except openai.APIConnectionError as e:
                last_error = e
                logger.warning("API connection error (attempt %d/%d): %s",
                               attempt + 1, self._max_retries, e)
                if attempt < self._max_retries - 1:
                    time.sleep(_jittered_backoff(attempt, base=3.0))

            except openai.AuthenticationError as e:
                last_error = e
                msg = str(e).lower()
                if "invalid api key" in msg or "incorrect api key" in msg:
                    logger.error("Invalid API key — check your DEEPSEEK_API_KEY")
                elif "insufficient_quota" in msg or "billing" in msg:
                    logger.error("Account quota exceeded or billing issue")
                else:
                    logger.error("Authentication failed: %s", e)
                raise  # Never retry auth errors

            except openai.BadRequestError as e:
                last_error = e
                logger.error("Bad request (non-retryable): %s", e)
                raise

            except openai.APIError as e:
                last_error = e
                status = getattr(e, "status_code", None)
                if status and 500 <= status < 600:
                    logger.warning("Server error %d (attempt %d/%d)", status, attempt + 1, self._max_retries)
                    if attempt < self._max_retries - 1:
                        time.sleep(_jittered_backoff(attempt))
                else:
                    logger.error("API error: status=%s, message=%s", status, e)
                    if attempt >= self._max_retries - 1:
                        raise

            except Exception as e:
                last_error = e
                logger.error("Unexpected error (attempt %d/%d): %s", attempt + 1, self._max_retries, e)
                if attempt >= self._max_retries - 1:
                    raise

        err_msg = f"LLM call failed after {self._max_retries} attempts"
        if last_error:
            err_msg += f": {type(last_error).__name__}: {last_error}"
        raise RuntimeError(err_msg)

    def chat_completion_stream(self, messages: list[dict], tools: list[dict] | None = None, **kw):
        """Streaming API call — yields dicts: {type: "delta"|"tool_call"|"done", ...}"""
        params = {"model": self._model, "messages": messages, "stream": True}
        if tools:
            params["tools"] = tools
        params.update(kw)

        resp = self._client.chat.completions.create(**params)
        content_chunks: list[str] = []
        tool_call_buf: dict[int, dict] = {}  # index -> {id, name, arguments}

        for chunk in resp:
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue

            # Text delta
            if delta.content:
                content_chunks.append(delta.content)
                yield {"type": "delta", "text": delta.content}

            # Tool call delta (streaming tool calls come in fragments)
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_call_buf:
                        tool_call_buf[idx] = {"id": tc.id or "", "name": "", "arguments": ""}
                    entry = tool_call_buf[idx]
                    if tc.id:
                        entry["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            entry["name"] += tc.function.name
                            yield {"type": "tool.start", "tool_name": entry["name"].strip()}
                        if tc.function.arguments:
                            entry["arguments"] += tc.function.arguments

        # Yield tool calls
        for entry in tool_call_buf.values():
            if entry["name"]:
                yield {
                    "type": "tool.complete",
                    "tool_name": entry["name"],
                    "arguments": entry["arguments"],
                    "tool_call_id": entry["id"],
                }

        final_content = "".join(content_chunks)
        yield {"type": "done", "content": final_content}
