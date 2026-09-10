#!/usr/bin/env bash

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

source_root=""
jekyll_args=()
while (($#)); do
  case "$1" in
    --source)
      if (($# < 2)); then
        echo "--source requires an OpenRoadCode checkout path" >&2
        exit 2
      fi
      source_root="$2"
      shift 2
      ;;
    *)
      jekyll_args+=("$1")
      shift
      ;;
  esac
done

if [[ -n "$source_root" ]]; then
  source_root="$(cd "$source_root" && pwd)"
  inventory_script="$source_root/scripts/docs_inventory.py"
  if [[ ! -f "$inventory_script" ]]; then
    echo "Documentation inventory script not found: $inventory_script" >&2
    exit 1
  fi

  manifest="$(mktemp "${TMPDIR:-/tmp}/openroadcode-docs.XXXXXX.json")"
  trap 'rm -f "$manifest"' EXIT

  echo "Generating documentation inventory from $source_root"
  python3 "$inventory_script" --source "$source_root" --check --manifest "$manifest"

  echo "Importing documentation into Jekyll"
  python3 "$project_dir/scripts/import_readmes.py" \
    --source "$source_root" \
    --manifest "$manifest" \
    --output "$project_dir/_docs" \
    --tree-output "$project_dir/_data/docs_tree.json"
fi

if ! command -v bundle >/dev/null 2>&1; then
  echo "Bundler is not installed. Install Ruby/Bundler before starting the site." >&2
  exit 1
fi

if ! bundle check >/dev/null 2>&1; then
  echo "Installing the project gems..."
  bundle install
fi

host="127.0.0.1"
port="4000"
for ((index = 0; index < ${#jekyll_args[@]}; index++)); do
  case "${jekyll_args[$index]}" in
    --host)
      if ((index + 1 < ${#jekyll_args[@]})); then
        host="${jekyll_args[$((index + 1))]}"
      fi
      ;;
    --port)
      if ((index + 1 < ${#jekyll_args[@]})); then
        port="${jekyll_args[$((index + 1))]}"
      fi
      ;;
  esac
done

site_url="http://${host}:${port}"
docs_url="${site_url}/docs/"

if command -v xdg-open >/dev/null 2>&1 && command -v curl >/dev/null 2>&1; then
  (
    for _ in {1..40}; do
      if curl --silent --fail --output /dev/null "$docs_url"; then
        xdg-open "$docs_url" >/dev/null 2>&1 || true
        exit
      fi
      sleep 0.25
    done
  ) &
fi

echo "Starting Open Road Code documentation at $docs_url"
exec bundle exec jekyll serve "${jekyll_args[@]}"
