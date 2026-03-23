# Logic Coder Agent Rules

## Inputs

- Course artifacts in `1_scouted_courses/validated/`
- Article drafts in `2_journal_drafts/final_markdown/`

## Execution

1. Extract required data inputs from the concept.
2. Implement pure logic in `core_concept.py` with `run(inputs: dict) -> dict`.
3. Define all required frontend inputs in `ui_schema.json` using field types the DynamicForm understands (see repo `permanent_scaffold/frontend_nextjs` schema).
4. Ensure returned result is JSON-serializable and deterministic for the same input.

## Hard constraints

- **Output only** `core_concept.py` and `ui_schema.json` in `3_core_logic_plugins/plugins/active/`. No other new files.
- **NEVER** write FastAPI routing, HTTP handlers, or server startup code.
- **NEVER** write Next.js pages, React components, hooks, or CSS modules.
- **ONLY** deliver the two files above; the host app loads them dynamically.

## `ui_schema.json` contract

- Top-level: `title`, `description`, `fields` (array).
- Each field: `name`, `label`, `type`, optional `required`, `default`, `options` (for selects).
- Allowed `type` strings include: `text`, `text_input`, `number`, `select`, `textarea`, `checkbox`, `file_upload`.

## `core_concept.py` contract

- Must define `run(inputs: dict) -> dict`.
- No side effects inside `run` (no disk writes, network, env mutation, or global state updates).
