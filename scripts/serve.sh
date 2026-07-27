#!/usr/bin/env bash

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

if ! command -v bundle >/dev/null 2>&1; then
  echo "Bundler is not installed. Run: sudo gem install bundler" >&2
  exit 1
fi

if ! bundle check >/dev/null 2>&1; then
  echo "Installing the project gems..."
  bundle install
fi

site_url="http://localhost:4000"

if command -v xdg-open >/dev/null 2>&1 && command -v curl >/dev/null 2>&1; then
  (
    for _ in {1..40}; do
      if curl --silent --fail --output /dev/null "$site_url"; then
        xdg-open "$site_url" >/dev/null 2>&1 || true
        exit
      fi
      sleep 0.25
    done
  ) &
fi

echo "Starting Open Road Code at $site_url"
exec bundle exec jekyll serve "$@"
