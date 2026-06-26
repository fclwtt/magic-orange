"""Auth - compatibility layer for MagicOrange"""
import threading
from typing import Optional, Dict, Any
from pathlib import Path

# Constants
CODEX_ACCESS_TOKEN_REFRESH_SKEW_SECONDS = 300
DEFAULT_AGENT_KEY_MIN_TTL_SECONDS = 60
KIMI_CODE_BASE_URL = "https://api.moonshot.cn"

# Provider registry
PROVIDER_REGISTRY = {}

# Lock for auth store
_auth_store_lock = threading.Lock()

def _codex_access_token_is_expiring(**kwargs) -> bool:
    return False

def _decode_jwt_claims(token: str) -> dict:
    return {}

def _import_codex_cli_tokens(**kwargs) -> dict:
    return {}

def _load_auth_store(**kwargs) -> dict:
    return {}

def _load_provider_state(**kwargs) -> dict:
    return {}

def _resolve_kimi_base_url(**kwargs) -> str:
    return KIMI_CODE_BASE_URL

def _resolve_zai_base_url(**kwargs) -> str:
    return ""

def _save_auth_store(**kwargs) -> None:
    pass

def _save_provider_state(**kwargs) -> None:
    pass

def read_credential_pool(**kwargs) -> dict:
    return {}

def write_credential_pool(**kwargs) -> None:
    pass

def get_api_key(**kwargs) -> Optional[str]:
    return None
