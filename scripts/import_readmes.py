#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import quote


IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "dist",
}

SOURCE_REPOSITORY_URL = "https://github.com/markisrt4/OpenRoadCode"
SOURCE_BRANCH = "master"

CURATED_GUIDES = {
    Path("apps/orcUi/ARCHITECTURE.md"): (
        ("apps", "orcUi", "architecture"),
        "apps/orcui/architecture",
        "/docs/apps/orcui/architecture/",
    ),
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


def is_ignored(path: Path, source_root: Path) -> bool:
    relative = path.relative_to(source_root)
    return any(part in IGNORED_DIRECTORIES for part in relative.parts)


def readme_site_location(
    readme_path: Path,
    source_root: Path,
) -> tuple[tuple[str, ...], str, str]:
    relative_directory = readme_path.parent.relative_to(source_root)
    if relative_directory.parts == ("docs",):
        return ("docs",), "docs", "/docs/"
    path_parts = relative_directory.parts or ("project",)
    slug = slugify("/".join(path_parts))
    return path_parts, slug, f"/docs/{slug}/"


def guide_site_location(
    guide_path: Path,
    source_root: Path,
) -> tuple[tuple[str, ...], str, str]:
    relative = guide_path.relative_to(source_root / "docs").with_suffix("")
    relative_parts = relative.parts
    slug = slugify("/".join(relative_parts))
    path_parts = ("docs",) + relative_parts
    return path_parts, slug, f"/docs/{slug}/"


def curated_guide_site_location(
    guide_path: Path,
    source_root: Path,
) -> tuple[tuple[str, ...], str, str] | None:
    try:
        relative = guide_path.relative_to(source_root)
    except ValueError:
        return None
    return CURATED_GUIDES.get(relative)


def source_path_to_site_url(
    target_path: Path,
    source_root: Path,
) -> str | None:
    try:
        relative = target_path.relative_to(source_root)
    except ValueError:
        return None

    if relative == Path("CONTRIBUTING.md"):
        return "/docs/contributing/"

    curated = CURATED_GUIDES.get(relative)
    if curated is not None and target_path.is_file():
        return curated[2]

    if target_path.name == "README.md" and target_path.is_file():
        _, _, url = readme_site_location(target_path, source_root)
        return url

    docs_root = source_root / "docs"
    if (
        target_path.is_file()
        and target_path.suffix.lower() == ".md"
        and target_path != docs_root / "README.md"
    ):
        try:
            target_path.relative_to(docs_root)
        except ValueError:
            return None
        _, _, url = guide_site_location(target_path, source_root)
        return url

    return None


def source_fallback_url(target_path: Path, source_root: Path) -> str | None:
    try:
        relative = target_path.relative_to(source_root)
    except ValueError:
        return None
    encoded_path = quote(relative.as_posix(), safe="/")
    kind = "tree" if target_path.is_dir() else "blob"
    return f"{SOURCE_REPOSITORY_URL}/{kind}/{SOURCE_BRANCH}/{encoded_path}"


def rewrite_markdown_links(
    markdown: str,
    source_path: Path,
    source_root: Path,
) -> str:
    link_pattern = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")

    def replace_link(match: re.Match[str]) -> str:
        label, destination = match.groups()
        destination = destination.strip()
        if (
            not destination
            or destination.startswith(("http://", "https://", "mailto:", "#", "/"))
        ):
            return match.group(0)

        target, separator, fragment = destination.partition("#")
        target_path = (source_path.parent / target).resolve()
        site_url = source_path_to_site_url(target_path, source_root)
        if site_url is not None:
            rewritten = site_url
        else:
            fallback_url = source_fallback_url(target_path, source_root)
            if fallback_url is None:
                return match.group(0)
            rewritten = fallback_url

        if separator and fragment:
            rewritten += f"#{fragment}"
        return f"[{label}]({rewritten})"

    return link_pattern.sub(replace_link, markdown)


def add_to_tree(
    tree: dict[str, Any],
    path_parts: tuple[str, ...],
    title: str,
    url: str,
) -> None:
    node = tree
    for part in path_parts:
        node = node.setdefault(part, {})
    node["__page__"] = {"title": title, "url": url}


def serialize_tree(tree: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for key in sorted((name for name in tree if name != "__page__"), key=str.lower):
        branch = tree[key]
        item: dict[str, Any] = {"name": display_name(key)}
        page = branch.get("__page__")
        if page:
            item["title"] = page["title"]
            item["url"] = page["url"]
        children = serialize_tree(branch)
        if children:
            item["children"] = children
        result.append(item)
    return result


def write_page(
    source_path: Path,
    source_root: Path,
    output_root: Path,
    tree: dict[str, Any],
    path_parts: tuple[str, ...],
    slug: str,
    url: str,
    fallback_title: str,
) -> None:
    markdown = source_path.read_text(encoding="utf-8")
    title = extract_title(markdown, fallback_title)
    markdown = remove_first_heading(markdown)
    markdown = rewrite_markdown_links(markdown, source_path, source_root)

    output_directory = output_root / slug
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / "index.md"

    front_matter = (
        "---\n"
        "layout: documentation\n"
        f"title: {json.dumps(title)}\n"
        f"permalink: {json.dumps(url)}\n"
        f"source_path: {json.dumps(str(source_path.relative_to(source_root)))}\n"
        "---\n\n"
    )
    output_path.write_text(front_matter + markdown + "\n", encoding="utf-8")
    add_to_tree(tree=tree, path_parts=path_parts, title=title, url=url)
    print(f"Imported {source_path} -> {output_path}")


def write_jekyll_page(
    readme_path: Path,
    source_root: Path,
    output_root: Path,
    tree: dict[str, Any],
) -> None:
    if is_ignored(readme_path, source_root):
        return
    path_parts, slug, url = readme_site_location(readme_path, source_root)
    write_page(
        source_path=readme_path,
        source_root=source_root,
        output_root=output_root,
        tree=tree,
        path_parts=path_parts,
        slug=slug,
        url=url,
        fallback_title=readme_path.parent.name or "Project",
    )


def write_guide_page(
    guide_path: Path,
    source_root: Path,
    output_root: Path,
    tree: dict[str, Any],
) -> None:
    if is_ignored(guide_path, source_root):
        return
    path_parts, slug, url = guide_site_location(guide_path, source_root)
    write_page(
        source_path=guide_path,
        source_root=source_root,
        output_root=output_root,
        tree=tree,
        path_parts=path_parts,
        slug=slug,
        url=url,
        fallback_title=guide_path.stem,
    )


def write_curated_guide_page(
    guide_path: Path,
    source_root: Path,
    output_root: Path,
    tree: dict[str, Any],
) -> None:
    location = curated_guide_site_location(guide_path, source_root)
    if location is None or not guide_path.is_file():
        return
    path_parts, slug, url = location
    write_page(
        source_path=guide_path,
        source_root=source_root,
        output_root=output_root,
        tree=tree,
        path_parts=path_parts,
        slug=slug,
        url=url,
        fallback_title=guide_path.stem,
    )


def write_contributing_page(
    contributing_path: Path,
    source_root: Path,
    output_root: Path,
    tree: dict[str, Any],
) -> None:
    write_page(
        source_path=contributing_path,
        source_root=source_root,
        output_root=output_root,
        tree=tree,
        path_parts=("contributing",),
        slug="contributing",
        url="/docs/contributing/",
        fallback_title="Contributing",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import OpenRoadCode repository documentation into Jekyll."
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tree-output", required=True, type=Path)
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
        write_jekyll_page(readme_path, source_root, output_root, tree)

    docs_root = source_root / "docs"
    if docs_root.is_dir():
        for guide_path in sorted(docs_root.rglob("*.md")):
            if guide_path.name == "README.md":
                continue
            write_guide_page(guide_path, source_root, output_root, tree)

    for relative_path in CURATED_GUIDES:
        write_curated_guide_page(
            source_root / relative_path,
            source_root,
            output_root,
            tree,
        )

    contributing_path = source_root / "CONTRIBUTING.md"
    if contributing_path.is_file():
        write_contributing_page(contributing_path, source_root, output_root, tree)

    tree_output.write_text(
        json.dumps(serialize_tree(tree), indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated documentation tree: {tree_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
