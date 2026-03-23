# Automated AI Journal MVP

This repository implements a plug-and-play AI journal pipeline built for OpenClaw.

## Pipeline

1. `1_scouted_courses`: raw and processed course discovery output
2. `2_journal_drafts`: natural language article drafts
3. `3_core_logic_plugins`: isolated plugin logic and UI schema
4. `4_final_repositories`: packaged full-stack outputs

## Permanent Scaffold

- `permanent_scaffold/backend_fastapi`: generic backend that imports plugin logic
- `permanent_scaffold/frontend_nextjs`: generic frontend that renders from plugin schema

## Agents

Agent role rules are stored under `agents/*/{SOUL.md,AGENTS.md}`.

## Skills

Skills are stored under `skills/` and can be installed/updated with `install_skills.sh`.
#debug
Inside the sandbox, when openclaw can't get an agent reply -> please use openshell term -> tab -> open Sandboxes -> press [r] for rules -> approve the policy