#!/usr/bin/env bash
# Sync pstack/ from cursor/plugins into this repo root.
# Upstream-owned paths are overwritten. Overlay paths are preserved.
# Commits each time there is a change.
set -euo pipefail

UPSTREAM_REPO="https://github.com/cursor/plugins.git"
UPSTREAM_BRANCH="main"
UPSTREAM_SUBDIR="pstack"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "Fetching $UPSTREAM_REPO@$UPSTREAM_BRANCH ..."
git clone --depth=1 --branch "$UPSTREAM_BRANCH" --filter=blob:none --sparse "$UPSTREAM_REPO" "$TMPDIR/upstream" >&2
cd "$TMPDIR/upstream"
git sparse-checkout set "$UPSTREAM_SUBDIR"
UPSTREAM_SHA="$(git rev-parse HEAD)"
echo "Upstream SHA: $UPSTREAM_SHA"

SRC="$TMPDIR/upstream/$UPSTREAM_SUBDIR"

# rsync upstream into repo root, preserving overlay files/dirs.
# Overlay = everything this mirror adds on top of upstream pstack/.
rsync -a --delete \
  --exclude='.git/' \
  --exclude='.github/' \
  --exclude='scripts/' \
  --exclude='.claude-plugin/' \
  --exclude='install.sh' \
  --exclude='INSTALL.md' \
  --exclude='.upstream-sha' \
  "$SRC/" "$ROOT/"

echo "$UPSTREAM_SHA" > "$ROOT/.upstream-sha"

cd "$ROOT"
if git diff --quiet && git diff --cached --quiet; then
  echo "No changes from upstream."
  exit 0
fi

git add -A
git commit -m "chore: sync upstream cursor/plugins@$UPSTREAM_SHA" -m "Source: https://github.com/cursor/plugins/tree/$UPSTREAM_SHA/pstack"
echo "Committed sync for $UPSTREAM_SHA"
