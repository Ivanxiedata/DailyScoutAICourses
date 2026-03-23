from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


API_BASE = "https://api.firecrawl.dev/v1"
DEFAULT_QUERY = "site:coursera.org OR site:deeplearning.ai AI course"
ALLOWED_DOMAINS = {
    "coursera.org",
    "www.coursera.org",
    "deeplearning.ai",
    "www.deeplearning.ai",
    "fast.ai",
    "www.fast.ai",
    "huggingface.co",
    "www.huggingface.co",
    "github.com",
    "www.github.com",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_local_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def domain_of(url: str) -> str:
    clean = url.replace("https://", "").replace("http://", "")
    return clean.split("/")[0].lower()


def is_allowed_url(url: str) -> bool:
    return domain_of(url) in ALLOWED_DOMAINS


@dataclass
class CacheConfig:
    query_ttl_seconds: int = 24 * 3600
    url_ttl_seconds: int = 7 * 24 * 3600
    requests_per_minute: int = 20
    max_requests_per_run: int = 40


class JsonFileCache:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}
        else:
            self._data = {}

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self._data.get(key)
        if not entry:
            return None
        if time.time() > float(entry.get("expires_at", 0)):
            self._data.pop(key, None)
            self._flush()
            return None
        return entry.get("value")

    def set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        self._data[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds,
        }
        self._flush()

    def _flush(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")


class RateLimiter:
    def __init__(self, state_file: Path, per_minute: int, per_run: int):
        self.state_file = state_file
        self.per_minute = per_minute
        self.per_run = per_run
        self.calls_this_run = 0
        state_file.parent.mkdir(parents=True, exist_ok=True)
        if state_file.exists():
            try:
                self.state = json.loads(state_file.read_text(encoding="utf-8"))
            except Exception:
                self.state = {}
        else:
            self.state = {}

    def guard(self) -> None:
        if self.calls_this_run >= self.per_run:
            raise RuntimeError("Per-run Firecrawl budget reached.")
        minute_key = str(int(time.time() // 60))
        current = self.state.get(minute_key, 0)
        if current >= self.per_minute:
            raise RuntimeError("Per-minute Firecrawl rate limit reached.")
        self.state[minute_key] = current + 1
        self.calls_this_run += 1
        self._compact(minute_key)
        self.state_file.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def _compact(self, current_key: str) -> None:
        keys = list(self.state.keys())
        for key in keys:
            if key != current_key:
                try:
                    if int(current_key) - int(key) > 5:
                        self.state.pop(key, None)
                except ValueError:
                    self.state.pop(key, None)


class FirecrawlClient:
    def __init__(self, api_key: str, cache_cfg: CacheConfig, cache_root: Path):
        self.api_key = api_key
        self.cache_cfg = cache_cfg
        self.query_cache = JsonFileCache(cache_root / "query_cache.json")
        self.url_cache = JsonFileCache(cache_root / "url_cache.json")
        self.rate_limiter = RateLimiter(
            cache_root / "ratelimit_state.json",
            per_minute=cache_cfg.requests_per_minute,
            per_run=cache_cfg.max_requests_per_run,
        )

    def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.rate_limiter.guard()
        response = requests.post(
            f"{API_BASE}/{endpoint}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=45,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Firecrawl error {response.status_code}: {response.text}")
        return response.json()

    def search_courses(self, query: str, limit: int = 5) -> dict[str, Any]:
        key = sha(f"search::{query}::{limit}")
        cached = self.query_cache.get(key)
        if cached:
            return {"cached": True, **cached}

        result = self._post("search", {"query": query, "limit": limit})
        self.query_cache.set(key, result, self.cache_cfg.query_ttl_seconds)
        return {"cached": False, **result}

    def scrape_url(self, url: str) -> dict[str, Any]:
        if not is_allowed_url(url):
            raise RuntimeError(f"Blocked domain for url: {url}")
        key = sha(f"scrape::{url}")
        cached = self.url_cache.get(key)
        if cached:
            return {"cached": True, **cached}

        result = self._post("scrape", {"url": url, "formats": ["markdown"]})
        self.url_cache.set(key, result, self.cache_cfg.url_ttl_seconds)
        return {"cached": False, **result}

    def crawl_domain(self, url: str, limit: int = 5) -> dict[str, Any]:
        if not is_allowed_url(url):
            raise RuntimeError(f"Blocked domain for url: {url}")
        key = sha(f"crawl::{url}::{limit}")
        cached = self.url_cache.get(key)
        if cached:
            return {"cached": True, **cached}

        result = self._post(
            "crawl",
            {
                "url": url,
                "limit": limit,
                "scrapeOptions": {"formats": ["markdown"]},
            },
        )
        self.url_cache.set(key, result, self.cache_cfg.url_ttl_seconds)
        return {"cached": False, **result}

    def extract_data(self, url: str, schema: dict[str, Any]) -> dict[str, Any]:
        if not is_allowed_url(url):
            raise RuntimeError(f"Blocked domain for url: {url}")
        key = sha(f"extract::{url}::{json.dumps(schema, sort_keys=True)}")
        cached = self.url_cache.get(key)
        if cached:
            return {"cached": True, **cached}

        result = self._post("extract", {"url": url, "schema": schema})
        self.url_cache.set(key, result, self.cache_cfg.url_ttl_seconds)
        return {"cached": False, **result}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def normalize_search_result(item: dict[str, Any], idx: int) -> dict[str, Any]:
    url = item.get("url") or item.get("link") or ""
    return {
        "id": f"course_{idx:02d}",
        "retrieved_at_utc": utc_now(),
        "title": item.get("title", "Untitled"),
        "source_url": url,
        "topic": item.get("snippet", "")[:200],
        "provider_domain": domain_of(url) if url else "",
    }


def run_scout_flow(query: str, limit: int) -> int:
    load_local_env(Path(".env"))
    api_key = os.getenv("FIRECRAWL_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("FIRECRAWL_API_KEY is missing. Set it in environment or .env.")

    root = Path(".")
    cache_root = root / ".cache/firecrawl"
    incoming = root / "1_scouted_courses/incoming"
    parsed = root / "1_scouted_courses/parsed"
    validated = root / "1_scouted_courses/validated"
    incoming.mkdir(parents=True, exist_ok=True)
    parsed.mkdir(parents=True, exist_ok=True)
    validated.mkdir(parents=True, exist_ok=True)

    client = FirecrawlClient(api_key=api_key, cache_cfg=CacheConfig(), cache_root=cache_root)
    search_payload = client.search_courses(query=query, limit=limit)

    results = search_payload.get("data", []) or search_payload.get("results", [])
    normalized: list[dict[str, Any]] = []

    for idx, item in enumerate(results[:limit], start=1):
        course = normalize_search_result(item, idx)
        url = course["source_url"]
        if not url or not is_allowed_url(url):
            continue
        scrape_payload = client.scrape_url(url)
        markdown = (
            scrape_payload.get("data", {}).get("markdown")
            if isinstance(scrape_payload.get("data"), dict)
            else ""
        )
        course["summary"] = (markdown or "").strip()[:1200]
        normalized.append(course)

        write_json(incoming / f"{course['id']}.json", {"search_item": item, "scrape": scrape_payload})
        write_json(parsed / f"{course['id']}.json", course)
        (validated / f"{course['id']}.md").write_text(
            f"# {course['title']}\n\n"
            f"- Source: {course['source_url']}\n"
            f"- Domain: {course['provider_domain']}\n"
            f"- Retrieved: {course['retrieved_at_utc']}\n\n"
            f"## Extracted Summary\n\n{course['summary'] or 'No markdown extracted.'}\n",
            encoding="utf-8",
        )

    write_json(
        incoming / "search_manifest.json",
        {"query": query, "retrieved_at_utc": utc_now(), "count": len(normalized), "raw": search_payload},
    )
    print(f"Firecrawl scout completed. Validated items: {len(normalized)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Firecrawl-backed scout tools")
    sub = parser.add_subparsers(dest="command", required=True)

    scout = sub.add_parser("scout", help="Run full scouting flow")
    scout.add_argument("--query", default=DEFAULT_QUERY)
    scout.add_argument("--limit", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "scout":
        return run_scout_flow(query=args.query, limit=args.limit)
    raise RuntimeError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
