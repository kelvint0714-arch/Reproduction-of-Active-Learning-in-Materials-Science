"""Validate the repository's reproduction recipe inventory.

This script checks documentation completeness only. It does not claim that any
paper has been reproduced or that upstream URLs are currently reachable.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "reproduction" / "manifest.json"
ALLOWED_RECIPE_STATUSES = {
    "recipe-ready",
    "source-lock-needed",
    "reimplementation-only",
    "offline-only",
    "blocked",
}
ALLOWED_EXECUTION_STATUSES = {
    "not_started",
    "source_locked",
    "environment_ready",
    "running",
    "result_check",
    "unified_reimplementation",
    "blocked",
    "completed",
}
REQUIRED_SECTION_PATTERNS = {
    "定位与边界": r"^##\s+.*定位与边界",
    "来源锁定": r"^##\s+.*来源锁定",
    "环境": r"^##\s+.*环境",
    "T0": r"^#{2,3}\s+T0\b",
    "T1": r"^#{2,3}\s+T1\b",
    "T2": r"^#{2,3}\s+T2\b",
    "T3": r"^#{2,3}\s+T3\b",
    "T4": r"^#{2,3}\s+T4\b",
    "公平性与评价": r"^##\s+.*(?:公平性与评价|评价与公平性)",
    "证据交付": r"^##\s+.*证据交付",
    "停止条件": r"^##\s+.*停止条件",
}
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*]\(([^)]+)\)")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def check_local_links(errors: list[str]) -> None:
    markdown_files = [
        REPO_ROOT / "README.md",
        *(REPO_ROOT / "papers").rglob("*.md"),
        *(REPO_ROOT / "reproduction").rglob("*.md"),
    ]
    for markdown_path in markdown_files:
        text = markdown_path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if (
                not target
                or target.startswith("#")
                or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I)
            ):
                continue
            resolved = (markdown_path.parent / target).resolve()
            if not resolved.exists():
                relative_source = markdown_path.relative_to(REPO_ROOT)
                fail(
                    errors,
                    f"{relative_source}: broken local link {raw_target!r}",
                )


def main() -> int:
    errors: list[str] = []
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = manifest.get("entries", [])

    if len(entries) != 32:
        fail(errors, f"manifest should contain 32 recipes, found {len(entries)}")

    ids = [entry.get("id") for entry in entries]
    duplicate_ids = sorted(
        item for item, count in Counter(ids).items() if count > 1
    )
    if duplicate_ids:
        fail(errors, f"duplicate IDs: {duplicate_ids}")

    dedicated_cards = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "papers").rglob("*.md")
        if path.name not in {"README.md", "LITERATURE_WATCH.md"}
    }
    manifest_dedicated_cards = {
        entry.get("card")
        for entry in entries
        if entry.get("card") != "papers/LITERATURE_WATCH.md"
    }
    cards_without_recipes = sorted(
        dedicated_cards.difference(manifest_dedicated_cards)
    )
    recipes_without_cards = sorted(
        manifest_dedicated_cards.difference(dedicated_cards)
    )
    if cards_without_recipes:
        fail(errors, f"paper cards missing from manifest: {cards_without_recipes}")
    if recipes_without_cards:
        fail(errors, f"manifest card paths not found: {recipes_without_cards}")

    watch_text = (
        REPO_ROOT / "papers" / "LITERATURE_WATCH.md"
    ).read_text(encoding="utf-8")
    verified_watch_ids = set(
        re.findall(r"^\|\s*(W\d{2})\s*\|", watch_text, re.M)
    )
    manifest_watch_ids = {
        entry.get("id")
        for entry in entries
        if entry.get("card") == "papers/LITERATURE_WATCH.md"
    }
    if verified_watch_ids != manifest_watch_ids:
        fail(
            errors,
            "verified watch IDs and manifest differ: "
            f"watch={sorted(verified_watch_ids)}, "
            f"manifest={sorted(manifest_watch_ids)}",
        )

    for entry in entries:
        paper_id = entry.get("id", "<missing-id>")
        recipe_status = entry.get("recipe_status")
        execution_status = entry.get("execution_status")
        expected_recipe = f"reproduction/recipes/{paper_id}/README.md"
        if entry.get("recipe") != expected_recipe:
            fail(
                errors,
                f"{paper_id}: recipe path should be {expected_recipe!r}",
            )
        if recipe_status not in ALLOWED_RECIPE_STATUSES:
            fail(errors, f"{paper_id}: invalid recipe_status {recipe_status!r}")
        if execution_status not in ALLOWED_EXECUTION_STATUSES:
            fail(
                errors,
                f"{paper_id}: invalid execution_status {execution_status!r}",
            )
        if execution_status == "completed":
            fail(
                errors,
                f"{paper_id}: completed is forbidden without run-evidence checks",
            )

        card_path = REPO_ROOT / entry.get("card", "")
        recipe_path = REPO_ROOT / entry.get("recipe", "")
        if not card_path.is_file():
            fail(errors, f"{paper_id}: missing card {card_path}")
        if not recipe_path.is_file():
            fail(errors, f"{paper_id}: missing recipe {recipe_path}")
            continue

        text = recipe_path.read_text(encoding="utf-8")
        if not re.search(rf"^#\s+.*\b{re.escape(paper_id)}\b", text, re.M):
            fail(errors, f"{paper_id}: H1 does not contain paper ID")
        if f"`{recipe_status}`" not in text[:700]:
            fail(
                errors,
                f"{paper_id}: manifest recipe_status is not declared near H1",
            )
        for section, pattern in REQUIRED_SECTION_PATTERNS.items():
            if not re.search(pattern, text, re.M):
                fail(errors, f"{paper_id}: missing section {section}")
        if "reproduction/runs/" not in text:
            fail(errors, f"{paper_id}: missing run-evidence destination")
        if "git clone" not in text and recipe_status not in {
            "reimplementation-only",
            "blocked",
        }:
            fail(errors, f"{paper_id}: missing source clone command")

    recipe_dirs = {
        path.parent.name
        for path in (REPO_ROOT / "reproduction" / "recipes").glob("*/README.md")
    }
    extra_dirs = sorted(recipe_dirs.difference(ids))
    missing_dirs = sorted(set(ids).difference(recipe_dirs))
    if extra_dirs:
        fail(errors, f"recipe directories not in manifest: {extra_dirs}")
    if missing_dirs:
        fail(errors, f"manifest recipes without directories: {missing_dirs}")

    check_local_links(errors)

    if errors:
        print("Recipe validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    status_counts = Counter(entry["recipe_status"] for entry in entries)
    print(f"Validated {len(entries)} reproduction recipes.")
    for status, count in sorted(status_counts.items()):
        print(f"- {status}: {count}")
    print("Execution evidence was not evaluated; no item is marked completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
