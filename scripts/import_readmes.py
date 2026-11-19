#!/usr/bin/env python3
"""Render the source-owned documentation inventory into Jekyll pages."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import quote

SOURCE_REPOSITORY_URL = "https://github.com/markisrt4/OpenRoadCode"
SOURCE_BRANCH = "master"


def slugify(value: str) -> str:
    value = value.lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9/-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-/")


def display_name(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def remove_first_heading(markdown: str) -> str:
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


def site_location(record: dict[str, str]) -> tuple[tuple[str, ...], str, str]:
    """Keep website routing separate from source documentation discovery."""
    relative = Path(record["path"])
    kind = record["kind"]
    if kind == "contributing":
        return ("contributing",), "contributing", "/docs/contributing/"
    if kind == "curated":
        if relative == Path("apps/orcUi/ARCHITECTURE.md"):
            return ("apps", "orcUi", "architecture"), "apps/orcui/architecture", "/docs/apps/orcui/architecture/"
        raise ValueError(f"No website route for curated guide: {relative}")
    if kind == "readme":
        directory = relative.parent
        if directory == Path("docs"):
            return ("docs",), "docs", "/docs/"
        parts = directory.parts if directory != Path(".") else ("project",)
    elif kind == "guide":
        parts = ("docs",) + relative.relative_to("docs").with_suffix("").parts
    else:
        raise ValueError(f"Unknown documentation kind: {kind}")
    slug = slugify("/".join(parts))
    if kind == "guide":
        slug = slugify("/".join(parts[1:]))
    return parts, slug, f"/docs/{slug}/"


def source_fallback_url(target_path: Path, source_root: Path) -> str | None:
    try:
        relative = target_path.relative_to(source_root)
    except ValueError:
        return None
    encoded_path = quote(relative.as_posix(), safe="/")
    kind = "tree" if target_path.is_dir() else "blob"
    return f"{SOURCE_REPOSITORY_URL}/{kind}/{SOURCE_BRANCH}/{encoded_path}"


def rewrite_markdown_links(markdown: str, source_path: Path, source_root: Path, routes: dict[Path, str]) -> str:
    link_pattern = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")

    def replace_link(match: re.Match[str]) -> str:
        label, destination = match.groups()
        destination = destination.strip()
        if not destination or destination.startswith(("http://", "https://", "mailto:", "#", "/")):
            return match.group(0)
        target, separator, fragment = destination.partition("#")
        target_path = (source_path.parent / target).resolve()
        rewritten = routes.get(target_path)
        if rewritten is None:
            rewritten = source_fallback_url(target_path, source_root)
        if rewritten is None:
            return match.group(0)
        if separator and fragment:
            rewritten += f"#{fragment}"
        return f"[{label}]({rewritten})"

    return link_pattern.sub(replace_link, markdown)


def add_to_tree(tree: dict[str, Any], parts: tuple[str, ...], title: str, url: str) -> None:
    node = tree
    for part in parts:
        node = node.setdefault(part, {})
    node["__page__"] = {"title": title, "url": url}


def serialize_tree(tree: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for key in sorted((name for name in tree if name != "__page__"), key=str.lower):
        branch = tree[key]
        item: dict[str, Any] = {"name": display_name(key)}
        page = branch.get("__page__")
        if page:
            item.update(page)
        children = serialize_tree(branch)
        if children:
            item["children"] = children
        result.append(item)
    return result


def import_documents(source_root: Path, output_root: Path, tree_output: Path, records: list[dict[str, str]]) -> None:
    """Import exactly the manifest entries, rejecting stale or colliding routes."""
    source_root = source_root.resolve()
    output_root = output_root.resolve()
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    tree_output.parent.mkdir(parents=True, exist_ok=True)
    destinations: dict[str, Path] = {}
    routes: dict[Path, str] = {}
    locations = []
    for record in records:
        source_path = (source_root / record["path"]).resolve()
        source_path.relative_to(source_root)
        if not source_path.is_file():
            raise FileNotFoundError(f"Stale documentation inventory: {source_path}")
        parts, slug, url = site_location(record)
        for destination in (f"slug:{slug}", f"url:{url}"):
            existing = destinations.get(destination)
            if existing is not None:
                raise RuntimeError(f"Documentation destination collision: {source_path} and {existing} both map to {destination}")
            destinations[destination] = source_path
        routes[source_path] = url
        locations.append((record, source_path, parts, slug, url))

    tree: dict[str, Any] = {}
    for record, source_path, parts, slug, url in locations:
        markdown = source_path.read_text(encoding="utf-8")
        title = record["title"]
        markdown = remove_first_heading(markdown)
        markdown = rewrite_markdown_links(markdown, source_path, source_root, routes)
        output_directory = output_root / slug
        output_directory.mkdir(parents=True, exist_ok=True)
        front_matter = (
            "---\n"
            "layout: documentation\n"
            f"title: {json.dumps(title)}\n"
            f"permalink: {json.dumps(url)}\n"
            f"source_path: {json.dumps(record['path'])}\n"
            "---\n\n"
        )
        (output_directory / "index.md").write_text(front_matter + markdown + "\n", encoding="utf-8")
        add_to_tree(tree, parts, title, url)
        print(f"Imported {source_path} -> {output_directory / 'index.md'}")
    tree_output.write_text(json.dumps(serialize_tree(tree), indent=2) + "\n", encoding="utf-8")
    print(f"Generated documentation tree: {tree_output}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tree-output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    records = json.loads(args.manifest.read_text(encoding="utf-8"))
    import_documents(args.source, args.output, args.tree_output, records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
