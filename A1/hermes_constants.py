"""Hermes constants - compatibility layer for MagicOrange"""
import os
from pathlib import Path

def get_hermes_home() -> Path:
    """Get Hermes home directory (MagicOrange uses ~/.magic-orange)"""
    home = os.environ.get("MAGIC_ORANGE_HOME", os.path.expanduser("~/.magic-orange"))
    path = Path(home)
    path.mkdir(parents=True, exist_ok=True)
    return path

OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

def get_hermes_dir(*args, **kwargs):
    """Get Hermes directory"""
    from pathlib import Path
    return Path(__file__).parent
