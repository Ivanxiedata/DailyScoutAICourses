"""
FastAPI entrypoint that runs AI journal plugins.

Loads `core_concept.py` in one of two ways (in order of precedence):

1. PLUGIN_FILE — absolute or cwd-relative path to a `core_concept.py` file
   (uses importlib.util.spec_from_file_location so agents can drop new logic
   under `3_core_logic_plugins/` without editing this repo's package plugin).

2. PLUGIN_MODULE — dotted import path (default: plugin.core_concept)

If PLUGIN_FILE is unset and
`../../3_core_logic_plugins/plugins/active/core_concept.py` exists relative to
this file, that path is used automatically.

Set PLUGIN_AUTO_RELOAD=1 (default) to reload the plugin on every /api/run.
Set PLUGIN_AUTO_RELOAD=0 to cache the loaded runner (better for production).
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AI Journal Plugin Backend", version="1.0.0")

_DYNAMIC_MODULE_NAME = "_streamline_dynamic_core_concept"

_cached_plugin_key: str | None = None
_cached_runner: Callable[..., dict[str, Any]] | None = None


class RunRequest(BaseModel):
    inputs: dict[str, Any] = Field(default_factory=dict)


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _default_repo_plugin_file() -> Path | None:
    """Prefer the pipeline's active plugin when present (repo layout)."""
    here = Path(__file__).resolve().parent
    candidate = (here / "../../3_core_logic_plugins/plugins/active/core_concept.py").resolve()
    return candidate if candidate.is_file() else None


def _resolve_plugin_path(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def _get_plugin_file_path() -> Path | None:
    env_path = os.getenv("PLUGIN_FILE", "").strip()
    if env_path:
        return _resolve_plugin_path(env_path)
    return _default_repo_plugin_file()


def _purge_dynamic_module() -> None:
    sys.modules.pop(_DYNAMIC_MODULE_NAME, None)


def _plugin_cache_key() -> str:
    plugin_file = _get_plugin_file_path()
    if plugin_file is not None:
        return f"file:{plugin_file.resolve()}"
    mod = os.getenv("PLUGIN_MODULE", "plugin.core_concept").strip() or "plugin.core_concept"
    return f"module:{mod}"


def _load_runner_from_file(path: Path, *, reload: bool) -> Callable[..., dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"PLUGIN_FILE does not exist: {path}")

    if reload:
        _purge_dynamic_module()
    else:
        existing = sys.modules.get(_DYNAMIC_MODULE_NAME)
        if existing is not None:
            runner = getattr(existing, "run", None)
            if callable(runner):
                return runner  # type: ignore[return-value]

    spec = importlib.util.spec_from_file_location(_DYNAMIC_MODULE_NAME, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load plugin spec from {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[_DYNAMIC_MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        _purge_dynamic_module()
        raise RuntimeError(f"Error executing plugin module {path}: {exc}") from exc

    runner = getattr(module, "run", None)
    if runner is None or not callable(runner):
        _purge_dynamic_module()
        raise RuntimeError(f"Plugin at {path} must define a callable run(inputs: dict)")

    return runner  # type: ignore[return-value]


def _load_runner_from_module(dotted: str, *, reload: bool) -> Callable[..., dict[str, Any]]:
    try:
        if reload and dotted in sys.modules:
            module = importlib.reload(sys.modules[dotted])
        else:
            module = importlib.import_module(dotted)
    except Exception as exc:
        raise RuntimeError(f"Failed to import {dotted}: {exc}") from exc

    runner = getattr(module, "run", None)
    if runner is None or not callable(runner):
        raise RuntimeError(f"{dotted} must define a callable run(inputs: dict)")
    return runner  # type: ignore[return-value]


def load_plugin_runner() -> Callable[..., dict[str, Any]]:
    global _cached_plugin_key, _cached_runner

    auto_reload = _truthy("PLUGIN_AUTO_RELOAD", default=True)
    key = _plugin_cache_key()

    if not auto_reload and _cached_runner is not None and _cached_plugin_key == key:
        return _cached_runner

    plugin_file = _get_plugin_file_path()
    if plugin_file is not None:
        runner = _load_runner_from_file(plugin_file, reload=auto_reload)
    else:
        dotted = os.getenv("PLUGIN_MODULE", "plugin.core_concept").strip() or "plugin.core_concept"
        runner = _load_runner_from_module(dotted, reload=auto_reload)

    if not auto_reload:
        _cached_plugin_key = key
        _cached_runner = runner
    else:
        _cached_plugin_key = None
        _cached_runner = None

    return runner


def plugin_probe() -> dict[str, Any]:
    """Non-secret metadata for /api/health debugging."""
    plugin_file = _get_plugin_file_path()
    auto_reload = _truthy("PLUGIN_AUTO_RELOAD", default=True)
    if plugin_file is not None:
        return {
            "mode": "file",
            "path": str(plugin_file),
            "exists": plugin_file.is_file(),
            "auto_reload": auto_reload,
        }
    module_name = os.getenv("PLUGIN_MODULE", "plugin.core_concept").strip() or "plugin.core_concept"
    return {
        "mode": "module",
        "module": module_name,
        "auto_reload": auto_reload,
    }


@app.get("/api/health")
def health() -> dict[str, Any]:
    probe = plugin_probe()
    status = "ok"
    if probe.get("mode") == "file" and probe.get("exists") is False:
        status = "degraded"
    return {"status": status, "plugin": probe}


@app.post("/api/run")
def run_plugin(req: RunRequest) -> dict[str, Any]:
    try:
        runner = load_plugin_runner()
        result = runner(req.inputs)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not isinstance(result, dict):
        raise HTTPException(status_code=500, detail="Plugin run() must return a dict")
    return result
