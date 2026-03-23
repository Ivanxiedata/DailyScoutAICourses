from datetime import datetime
from pathlib import Path
import shutil


def main() -> int:
    root = Path(".")
    scaffold = root / "permanent_scaffold"
    plugin_dir = root / "3_core_logic_plugins/plugins/active"
    drafts_dir = root / "2_journal_drafts/final_markdown"
    builds_dir = root / "4_final_repositories/builds"
    builds_dir.mkdir(parents=True, exist_ok=True)

    build_name = datetime.now().strftime("build_%Y%m%d_%H%M%S")
    build_path = builds_dir / build_name
    shutil.copytree(scaffold, build_path)

    shutil.copy2(plugin_dir / "core_concept.py", build_path / "backend_fastapi/plugin/core_concept.py")
    shutil.copy2(plugin_dir / "ui_schema.json", build_path / "frontend_nextjs/plugin/ui_schema.json")

    draft_files = sorted(drafts_dir.glob("*.md"))
    if draft_files:
        shutil.copy2(draft_files[0], build_path / "JOURNAL.md")

    print(f"Created packaged repository at {build_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
