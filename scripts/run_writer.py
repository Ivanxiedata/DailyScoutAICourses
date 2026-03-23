from pathlib import Path


def main() -> int:
    source_dir = Path("1_scouted_courses/validated")
    drafts_dir = Path("2_journal_drafts/drafts")
    drafts_dir.mkdir(parents=True, exist_ok=True)

    md_files = sorted(source_dir.glob("*.md"))
    if not md_files:
        print("No validated markdown files found.")
        return 1

    source = md_files[0].read_text(encoding="utf-8")
    output = drafts_dir / "journal_draft.md"
    output.write_text(
        "# AI Journal Draft\n\n"
        "## Core Concept\n\n"
        "Derived from validated course material.\n\n"
        "## Source Notes\n\n"
        f"{source}\n",
        encoding="utf-8",
    )
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
