#!/bin/bash
# Install git hooks from git-hooks/ into .git/hooks/
set -euo pipefail

HOOKS_DIR="$(git rev-parse --git-dir)/hooks"
SOURCE_DIR="$(dirname "$0")/git-hooks"

for hook in "$SOURCE_DIR"/*; do
  name=$(basename "$hook")
  dest="$HOOKS_DIR/$name"
  cp "$hook" "$dest"
  chmod +x "$dest"
  echo "Installed: $dest"
done

echo "All hooks installed."
