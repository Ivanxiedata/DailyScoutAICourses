# Logic Coder Agent Rules

## Inputs

- Course artifacts in `1_scouted_courses/validated/`
- Article drafts in `2_journal_drafts/final_markdown/`

## Execution

1. Extract required data inputs from the concept.
2. Implement pure logic in `core_concept.py` with `run(inputs: dict)`.
3. Define all required frontend inputs in `ui_schema.json`.
4. Ensure returned result is JSON-serializable and deterministic for same input.

## Hard Constraints

- Do not create additional files.
- Do not write framework-specific backend/frontend code.
- Keep all side effects out of `run`.
