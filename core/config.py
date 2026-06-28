"""ConfigStore — dict / YAML 配置"""

from __future__ import annotations
from typing import Any
from interfaces.iconfig import IConfigStore

class ConfigStore(IConfigStore):
    def __init__(self, data: dict | str = None):
        self._data: dict = {}
        if isinstance(data, dict):
            self._data = data
        elif isinstance(data, str):
            import yaml; from pathlib import Path
            p = Path(data)
            if p.exists():
                with open(p) as f:
                    self._data = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split("."); val = self._data
        for k in keys:
            if isinstance(val, dict): val = val.get(k)
            else: return default
        return val if val is not None else default

    def set(self, key: str, value: Any) -> None:
        keys = key.split("."); d = self._data
        for k in keys[:-1]: d = d.setdefault(k, {})
        d[keys[-1]] = value

    def load(self) -> dict: return self._data
