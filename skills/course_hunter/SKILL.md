# Course Hunter Skill

## Name

course_hunter

## Purpose

Find and collect AI course material into the scouting pipeline.

## Entrypoint

Run:

```bash
python skills/course_hunter/hunt_deeplearning.py
```

## Output Contract

The script writes JSON and markdown artifacts to:

- `1_scouted_courses/incoming/`
- `1_scouted_courses/parsed/`
- `1_scouted_courses/validated/`

Each artifact includes source URL, retrieval timestamp, and extracted concept summary.
