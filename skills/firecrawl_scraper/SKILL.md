---
name: firecrawl-scraper
description: Integrates Firecrawl for AI course discovery, page scraping, and structured extraction with caching and rate limits. Use when scouting web courses or turning course pages into markdown/json artifacts.
---

# Firecrawl Scraper Skill

## Purpose

Provide Scout with safe web retrieval actions backed by Firecrawl.

## Exposed Tools

1. `search_courses(query, limit)`
   - Finds candidate course URLs for a topic query.
2. `scrape_url(url)`
   - Returns cleaned markdown for one page.
3. `crawl_domain(url, limit)`
   - Follows links from a seed URL and returns multiple page markdown results.
4. `extract_data(url, schema)`
   - Extracts structured JSON from a page based on a provided schema.

## Safety Controls

- Uses `FIRECRAWL_API_KEY` from environment.
- Query + URL cache to reduce repeated API calls.
- Per-minute request throttle.
- Per-run request budget cap.
- Domain allowlist for trusted course providers.

## Run Commands

```bash
python skills/firecrawl_scraper/firecrawl_tools.py scout
```

Optional custom query:

```bash
python skills/firecrawl_scraper/firecrawl_tools.py scout --query "deep learning course for engineers"
```

## Output Contract

Writes artifacts into:

- `1_scouted_courses/incoming/` (raw Firecrawl results)
- `1_scouted_courses/parsed/` (normalized JSON records)
- `1_scouted_courses/validated/` (markdown summaries for downstream writer)
