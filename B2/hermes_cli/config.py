"""Config - compatibility layer"""
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def get_hermes_home() -> Path:
    home = os.environ.get("MAGIC_ORANGE_HOME", os.path.expanduser("~/.magic-orange"))
    path = Path(home)
    path.mkdir(parents=True, exist_ok=True)
    return path

def load_config(hermes_home: Optional[Path] = None) -> Dict[str, Any]:
    if hermes_home is None:
        hermes_home = get_hermes_home()
    config_path = hermes_home / "config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
    return {}
