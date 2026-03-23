import json
from pathlib import Path


def main() -> int:
    plugin_dir = Path("3_core_logic_plugins/plugins/active")
    plugin_dir.mkdir(parents=True, exist_ok=True)

    core_logic = """from typing import Any


def run(inputs: dict[str, Any]) -> dict[str, Any]:
    topic = str(inputs.get("topic", "")).strip()
    if not topic:
        return {"ok": False, "error": "Missing topic"}
    return {
        "ok": True,
        "topic": topic,
        "explanation": f"{topic} explained with isolated plugin logic."
    }
"""
    schema = {
        "title": "Course Logic Runner",
        "description": "Run isolated plugin logic",
        "fields": [
            {"name": "topic", "label": "Topic", "type": "text", "required": True}
        ],
    }

    (plugin_dir / "core_concept.py").write_text(core_logic, encoding="utf-8")
    (plugin_dir / "ui_schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"Wrote plugin files to {plugin_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
