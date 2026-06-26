"""Env loader - compatibility layer"""
import os
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

def load_hermes_dotenv(hermes_home: Optional[Path] = None, project_env: Optional[str] = None) -> List[Path]:
    loaded_paths = []
    if hermes_home is None:
        return loaded_paths
    env_file = hermes_home / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ:
                            os.environ[key] = value
            loaded_paths.append(env_file)
        except Exception as e:
            logger.warning(f"Failed to load .env: {e}")
    return loaded_paths
