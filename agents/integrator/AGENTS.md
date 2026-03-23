# Integrator Agent Rules

## Inputs

- Scaffold from `permanent_scaffold/`
- Plugin files from `3_core_logic_plugins/plugins/active/`
- Journal markdown from `2_journal_drafts/final_markdown/`

## Execution

1. Create a timestamped build directory in `4_final_repositories/builds/`.
2. Copy scaffold into that build directory.
3. Replace:
   - `backend_fastapi/plugin/core_concept.py`
   - `frontend_nextjs/plugin/ui_schema.json`
4. Add journal markdown into the build (for example `JOURNAL.md`).
5. Validate that backend and frontend plugin files both exist in the packaged repo.

## Completion Criteria

- Build directory is self-contained and ready for user `git clone`.
