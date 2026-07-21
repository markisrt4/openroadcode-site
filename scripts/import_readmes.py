#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


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


def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()

    return fallback.replace("_", " ").replace("-", " ").title()


def write_jekyll_page(
    readme_path: Path,
    source_root: Path,
    output_root: Path,
) -> None:
    relative_directory = readme_path.parent.relative_to(source_root)

    if any(part in IGNORED_DIRECTORIES for part in relative_directory.parts):
        return

    markdown = readme_path.read_text(encoding="utf-8")
    title = extract_title(markdown, readme_path.parent.name)

    slug = slugify(relative_directory.as_posix())

    if not slug:
        slug = "project"

    output_directory = output_root / slug
    output_directory.mkdir(parents=True, exist_ok=True)

    output_path = output_directory / "index.md"

    front_matter = (
        "---\n"
        "layout: documentation\n"
        f'title: "{title}"\n'
        f'permalink: "/docs/{slug}/"\n'
        f'source_path: "{readme_path.relative_to(source_root)}"\n'
        "---\n\n"
    )

    output_path.write_text(
        front_matter + markdown,
        encoding="utf-8",
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

    args = parser.parse_args()

    source_root = args.source.resolve()
    output_root = args.output.resolve()

    if not source_root.is_dir():
        raise SystemExit(f"Source directory does not exist: {source_root}")

    if output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True)

    for readme_path in sorted(source_root.rglob("README.md")):
        write_jekyll_page(
            readme_path=readme_path,
            source_root=source_root,
            output_root=output_root,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())