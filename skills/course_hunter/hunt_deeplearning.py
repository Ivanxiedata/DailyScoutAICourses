from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


COURSES = [
    {
        "title": "Neural Networks and Deep Learning",
        "provider": "DeepLearning.AI",
        "source_url": "https://www.coursera.org/learn/neural-networks-deep-learning",
        "topic": "neural networks fundamentals",
        "summary": "Introduces neural network building blocks, forward/backpropagation, and practical training workflows."
    },
    {
        "title": "Generative AI for Everyone",
        "provider": "DeepLearning.AI",
        "source_url": "https://www.coursera.org/learn/generative-ai-for-everyone",
        "topic": "generative AI foundations",
        "summary": "Explains large language model capabilities, risks, and practical adoption patterns."
    }
]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    root = Path(".")
    incoming = root / "1_scouted_courses/incoming"
    parsed = root / "1_scouted_courses/parsed"
    validated = root / "1_scouted_courses/validated"
    incoming.mkdir(parents=True, exist_ok=True)
    parsed.mkdir(parents=True, exist_ok=True)
    validated.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    for idx, course in enumerate(COURSES, start=1):
        slug = f"course_{idx:02d}"
        payload = {
            "id": slug,
            "retrieved_at_utc": now,
            **course
        }

        write_json(incoming / f"{slug}.json", payload)
        write_json(parsed / f"{slug}.json", payload)
        (validated / f"{slug}.md").write_text(
            f"# {course['title']}\n\n"
            f"- Provider: {course['provider']}\n"
            f"- Source: {course['source_url']}\n"
            f"- Topic: {course['topic']}\n\n"
            f"## Summary\n\n{course['summary']}\n",
            encoding="utf-8"
        )

    print("Course hunter completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
