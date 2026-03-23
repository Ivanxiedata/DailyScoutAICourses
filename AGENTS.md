# Workspace agent (OpenClaw 2026.3.13)

This repository uses **workspace mode**: one agent, one root. At the start of a session, read `IDENTITY.md`, `USER.md`, and `TOOLS.md`. Pipeline rules below apply on every turn.

---

## Phase: Scout (course discovery)

### Inputs

- Firecrawl skill package in `skills/firecrawl_scraper/`
- `FIRECRAWL_API_KEY` from environment
- Trusted source domain allowlist

### Search strategy (critical)

- NEVER use generic search terms like "AI courses" or "learn machine learning".
- ALWAYS use advanced search operators to target developer materials.
- Primary targets:
  - `site:github.com "deeplearning.ai" path:*.ipynb`
  - `site:github.com "langchain" OR "anthropic" tutorial course`
- Extract real technical implementation detail, frameworks used, and core concept code.

### Execution

1. Run `python skills/firecrawl_scraper/firecrawl_tools.py scout` when batch tooling is appropriate, or use the Firecrawl tool actions directly.
2. Tool actions: `search_courses(query, limit)`, `scrape_url(url)`, `crawl_domain(url, limit)`, `extract_data(url, schema)`.
3. Enforce caching and request throttling before each API call.
4. Write raw artifacts to `1_scouted_courses/incoming/`.
5. Normalize extractable text/json into `1_scouted_courses/parsed/`.
6. Move quality-checked items to `1_scouted_courses/validated/`.

### Completion criteria

- At least one validated course package exists when a scout run is requested.
- Each package includes source metadata and extracted learning content.
- No budget/rate-limit rule was exceeded during execution.

---

## Multi-Agent Protocol

The pipeline is four **logical roles** in order. The same workspace agent performs whichever phase Ivan asks for; default full pipeline order is **Scout → Writer → Logic Coder → Integrator**.

### 1. Scout (see above)

**Skills:** `skills/firecrawl_scraper/` (primary tooling). Use `skills/scout-master/SKILL.md` when the user asks to "scout" or run the first task in that skill’s wording. Use `skills/course_hunter/` when a scripted hunt fits the request.

**Hard rule:** Never write into `2_journal_drafts`, `3_core_logic_plugins`, or `permanent_scaffold` during scout-only work.

### 2. Technical Writer (journal prose)

**Inputs:** `1_scouted_courses/validated/`

**Mission:** Turn raw course material into clear, accurate, approachable markdown without losing technical truth.

**Execution:**

1. Identify one primary core concept from the selected course.
2. Produce a markdown draft with: concept overview, why it matters, step-by-step mental model, practical implementation notes.
3. Save draft to `2_journal_drafts/drafts/`.
4. After review, promote to `2_journal_drafts/final_markdown/`.

**Completion:** A readable markdown article exists in `final_markdown/`.

**Constraints:** Do not write or modify plugin code, backend, or frontend app files in this phase.

### 3. Logic Coder (plugin pair)

**Inputs:** `1_scouted_courses/validated/`, `2_journal_drafts/final_markdown/`

**Mission:** Produce exactly two files the host app loads: pure Python logic + UI schema.

**Execution:**

1. Extract required data inputs from the concept.
2. Implement `run(inputs: dict) -> dict` in `core_concept.py`.
3. Define frontend inputs in `ui_schema.json` using types the DynamicForm understands (see `permanent_scaffold/frontend_nextjs`).
4. Ensure output is JSON-serializable and deterministic for the same input.

**Hard constraints:**

- **Output only** `core_concept.py` and `ui_schema.json` under `3_core_logic_plugins/plugins/active/`. No other new files unless Ivan explicitly overrides.
- **NEVER** write FastAPI routing, HTTP handlers, or server startup code.
- **NEVER** write Next.js pages, React components, hooks, or CSS modules.

**`ui_schema.json` contract:** Top-level `title`, `description`, `fields` (array). Each field: `name`, `label`, `type`, optional `required`, `default`, `options` (selects). Allowed `type` values include: `text`, `text_input`, `number`, `select`, `textarea`, `checkbox`, `file_upload`.

**`core_concept.py` contract:** Must define `run(inputs: dict) -> dict`. No side effects inside `run` (no disk writes, network, env mutation, or global state). No secrets or API keys in generated files.

### 4. Integrator (shippable repo)

**Inputs:** `permanent_scaffold/`, `3_core_logic_plugins/plugins/active/`, `2_journal_drafts/final_markdown/`

**Mission:** Assemble a self-contained build users can clone and run.

**Execution:**

1. Create a timestamped directory under `4_final_repositories/builds/`.
2. Copy `permanent_scaffold/` into that build directory.
3. Replace plugin payloads:
   - `backend_fastapi/plugin/core_concept.py`
   - `frontend_nextjs/plugin/ui_schema.json`
4. Add the final journal article (for example `JOURNAL.md`).
5. Confirm both plugin files exist in the packaged tree.

**Completion:** Build directory is self-contained and ready for `git clone`.

**Hard rule:** Do not alter source pipeline artifacts outside the new build folder (copy, do not mutate originals in place).

---

## Triggering from OpenClaw CLI

Use the main workspace agent with a clear phase in the message, for example:

- Scout: reference Firecrawl / `1_scouted_courses/validated/` and the URL or query.
- Writer: point at validated course files and desired draft name.
- Logic Coder: point at drafts + concept to implement.
- Integrator: request a new timestamped build under `4_final_repositories/builds/`.

See `QUICKSTART.md` for gateway + example agent invocation.
