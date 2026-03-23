from typing import Any


def run(inputs: dict[str, Any]) -> dict[str, Any]:
    topic = str(inputs.get("topic", "")).strip()
    detail_level = str(inputs.get("detail_level", "intermediate")).strip().lower()
    key_points = inputs.get("key_points", [])

    if not topic:
        return {
            "ok": False,
            "error": "Missing required input: topic"
        }

    if not isinstance(key_points, list):
        key_points = [str(key_points)]

    bullets = [f"- {str(p).strip()}" for p in key_points if str(p).strip()]
    bullet_text = "\n".join(bullets) if bullets else "- No key points provided."

    explanation = (
        f"Topic: {topic}\n"
        f"Detail level: {detail_level}\n\n"
        "Core explanation:\n"
        f"{topic} can be understood by breaking it into practical building blocks.\n\n"
        "Key points:\n"
        f"{bullet_text}"
    )

    return {
        "ok": True,
        "topic": topic,
        "detail_level": detail_level,
        "explanation": explanation
    }
