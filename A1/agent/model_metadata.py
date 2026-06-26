"""Model metadata - compatibility layer"""
from typing import Optional

def get_model_info(model: str) -> dict:
    return {"name": model, "context_window": 128000}

def fetch_model_metadata(model: str) -> dict:
    return {"name": model, "context_window": 128000}

def estimate_tokens_rough(text: str) -> int:
    return len(text) // 4

def estimate_messages_tokens_rough(messages: list) -> int:
    return sum(estimate_tokens_rough(m.get("content", "")) for m in messages)

def estimate_request_tokens_rough(messages: list) -> int:
    return estimate_messages_tokens_rough(messages)

def get_next_probe_tier(current_tier: int) -> int:
    return current_tier + 1

def parse_context_limit_from_error(error: str) -> Optional[int]:
    return None

def parse_available_output_tokens_from_error(error: str) -> Optional[int]:
    return None

def save_context_length(model: str, context_length: int) -> None:
    pass

def is_local_endpoint(url: str) -> bool:
    return "localhost" in url or "127.0.0.1" in url

def query_ollama_num_ctx(model: str) -> Optional[int]:
    return None

def get_model_context_length(model: str) -> int:
    return 128000
