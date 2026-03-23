# TOOLS.md - Local Notes

Skills define how tools work. This file records what is enabled and allowed for this workspace.

## Firecrawl scout tools (enabled)

These tools from `skills/firecrawl_scraper` are **explicitly enabled** and should be available whenever course scouting is in scope:

- **`search_courses`** — search for course-like targets with structured queries (see `AGENTS.md` for operator strategy).
- **`scrape_url`** — fetch and extract content from a single URL.

Use them per `AGENTS.md` execution steps and rate-limit rules. Other actions from the same skill (for example `crawl_domain`, `extract_data`) remain documented in `AGENTS.md` where relevant.

---

Add camera names, SSH aliases, TTS preferences, and other environment-specific notes below as needed.
