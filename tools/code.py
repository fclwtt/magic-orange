"""Python code execution — subprocess sandbox (Hermes-style sys.executable)."""

from __future__ import annotations
import json, subprocess, tempfile, os, sys
from typing import Any


def execute_code(args: dict[str, Any]) -> str:
    code = args.get("code", "")
    if not code:
        return json.dumps({"error": "code required"})
    try:
        with tempfile.TemporaryDirectory(prefix="mo_exec_") as tmp:
            script = os.path.join(tmp, "_script.py")
            with open(script, "w", encoding="utf-8") as f:
                f.write(code)
            # Use sys.executable — works on all platforms (Windows/Linux/macOS)
            result = subprocess.run(
                [sys.executable, script],
                capture_output=True, text=True, timeout=30,
                cwd=tmp,
                env={**os.environ, "HOME": os.environ.get("HOME", "/tmp")},
            )
            out = result.stdout.strip()
            err = result.stderr.strip() if result.returncode != 0 else ""
            response = {}
            if out:
                response["stdout"] = out
            if err:
                response["stderr"] = err
            response["exit_code"] = result.returncode
            return json.dumps(response)
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Execution timed out (30s)"})
    except Exception as e:
        return json.dumps({"error": str(e)})


SCHEMAS = {
    "execute_code": {
        "description": "Execute Python code in a subprocess sandbox",
        "parameters": {"type": "object", "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
        }, "required": ["code"]},
    },
}
