from importlib import import_module
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AI Journal Plugin Backend", version="1.0.0")


class RunRequest(BaseModel):
    inputs: dict[str, Any] = Field(default_factory=dict)


def load_plugin_runner():
    try:
        module = import_module("plugin.core_concept")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Failed to import plugin.core_concept: {exc}") from exc

    runner = getattr(module, "run", None)
    if runner is None or not callable(runner):
        raise RuntimeError("plugin.core_concept must define a callable run(inputs: dict)")
    return runner


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/run")
def run_plugin(req: RunRequest) -> dict[str, Any]:
    try:
        runner = load_plugin_runner()
        result = runner(req.inputs)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not isinstance(result, dict):
        raise HTTPException(status_code=500, detail="Plugin run() must return a dict")
    return result
