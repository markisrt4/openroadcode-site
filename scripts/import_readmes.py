#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any


IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "dist",
}


def slugify(value: str) -> str:
    value = value.lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9/-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-/")


def display_name(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()

    return display_name(fallback)


def remove_first_heading(markdown: str) -> str:
    """
    Remove the first top-level Markdown heading when it is the first
    meaningful line in the document.

    The generated Jekyll layout already displays page.title.
    """
    lines = markdown.splitlines()

    for index, line in enumerate(lines):
        if not line.strip():
            continue

        if re.match(r"^#\s+", line):
            del lines[index]

            if index < len(lines) and not lines[index].strip():
                del lines[index]

        break

    return "\n".join(lines).lstrip()


def add_to_tree(
    tree: dict[str, Any],
    path_parts: tuple[str, ...],
    title: str,
    url: str,
) -> None:
    node = tree

    for part in path_parts:
        node = node.setdefault(part, {})

    node["__page__"] = {
        "title": title,
        "url": url,
    }


def serialize_tree(tree: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    for key in sorted(
        (name for name in tree if name != "__page__"),
        key=str.lower,
    ):
        branch = tree[key]

        item: dict[str, Any] = {
            "name": display_name(key),
        }

        page = branch.get("__page__")

        if page:
            item["title"] = page["title"]
            item["url"] = page["url"]

        children = serialize_tree(branch)

        if children:
            item["children"] = children

        result.append(item)

    return result


def write_jekyll_page(
    readme_path: Path,
    source_root: Path,
    output_root: Path,
    tree: dict[str, Any],
) -> None:
    relative_directory = readme_path.parent.relative_to(source_root)

    if any(part in IGNORED_DIRECTORIES for part in relative_directory.parts):
        return

    markdown = readme_path.read_text(encoding="utf-8")
    title = extract_title(markdown, readme_path.parent.name or "Project")
    markdown = remove_first_heading(markdown)

    path_parts = relative_directory.parts or ("project",)
    slug = slugify("/".join(path_parts))
    url = f"/docs/{slug}/"

    output_directory = output_root / slug
    output_directory.mkdir(parents=True, exist_ok=True)

    output_path = output_directory / "index.md"

    front_matter = (
        "---\n"
        "layout: documentation\n"
        f"title: {json.dumps(title)}\n"
        f"permalink: {json.dumps(url)}\n"
        f"source_path: {json.dumps(str(readme_path.relative_to(source_root)))}\n"
        "---\n\n"
    )

    output_path.write_text(
        front_matter + markdown + "\n",
        encoding="utf-8",
    )

    add_to_tree(
        tree=tree,
        path_parts=path_parts,
        title=title,
        url=url,
    )

    print(f"Imported {readme_path} -> {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import repository README files into a Jekyll site."
    )

    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Root of the Open Road Code source repository.",
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Destination Jekyll collection directory.",
    )

    parser.add_argument(
        "--tree-output",
        required=True,
        type=Path,
        help="Destination JSON file for the documentation tree.",
    )

    args = parser.parse_args()

    source_root = args.source.resolve()
    output_root = args.output.resolve()
    tree_output = args.tree_output.resolve()

    if not source_root.is_dir():
        raise SystemExit(f"Source directory does not exist: {source_root}")

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)
    tree_output.parent.mkdir(parents=True, exist_ok=True)

    tree: dict[str, Any] = {}

    for readme_path in sorted(source_root.rglob("README.md")):
        write_jekyll_page(
            readme_path=readme_path,
            source_root=source_root,
            output_root=output_root,
            tree=tree,
        )

    serialized_tree = serialize_tree(tree)

    tree_output.write_text(
        json.dumps(serialized_tree, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Generated documentation tree: {tree_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
