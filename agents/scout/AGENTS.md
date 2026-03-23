# Scout Agent Rules

## Inputs

- Hunting scripts in `skills/course_hunter/`

## Execution

1. Run Python hunting scripts to collect course material.
2. Write raw artifacts to `1_scouted_courses/incoming/`.
3. Normalize extractable text/json into `1_scouted_courses/parsed/`.
4. Move quality-checked items to `1_scouted_courses/validated/`.

## Completion Criteria

- At least one validated course package exists.
- Each package includes source metadata and extracted learning content.
