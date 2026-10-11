#!/usr/bin/env bash
# Sync pstack/ from cursor/plugins into this repo root.
# Upstream-owned paths are overwritten. Overlay paths are preserved.
# Commits each time there is a change.
set -euo pipefail

UPSTREAM_REPO="https://github.com/cursor/plugins.git"
UPSTREAM_BRANCH="main"
UPSTREAM_SUBDIR="pstack"

# A local bare-repository source is available only for the isolated rsync test.
if [ "${PSTACK_SYNC_TEST_FIXTURE:-}" = "1" ]; then
  if [ -z "${PSTACK_SYNC_FIXTURE_REPO:-}" ] || [[ "$PSTACK_SYNC_FIXTURE_REPO" != /* ]]; then
    echo "PSTACK_SYNC_TEST_FIXTURE=1 requires an absolute local bare repository path" >&2
    exit 2
  fi
  UPSTREAM_REPO="$PSTACK_SYNC_FIXTURE_REPO"
  UPSTREAM_BRANCH="${PSTACK_SYNC_FIXTURE_BRANCH:-main}"
  if [ "$(git -C "$UPSTREAM_REPO" rev-parse --is-bare-repository 2>/dev/null || true)" != "true" ]; then
    echo "fixture source must be a local bare Git repository" >&2
    exit 2
  fi
elif [ -n "${PSTACK_SYNC_FIXTURE_REPO:-}${PSTACK_SYNC_FIXTURE_BRANCH:-}" ]; then
  echo "PSTACK_SYNC_FIXTURE_REPO/BRANCH require PSTACK_SYNC_TEST_FIXTURE=1" >&2
  exit 2
fi
if ! git check-ref-format --branch "$UPSTREAM_BRANCH" >/dev/null 2>&1; then
  echo "invalid upstream branch name" >&2
  exit 2
fi

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
  --exclude='opencode/' \
  --exclude='.claude-plugin/' \
  --exclude='install.sh' \
  --exclude='bootstrap.sh' \
  --exclude='INSTALL.md' \
  --exclude='README.md' \
  --exclude='AGENTS.md' \
  --exclude='.upstream-sha' \
  --exclude='/oc-port-agent.json' \
  --exclude='/.oc-port/' \
  --exclude='agents/opencode-port-agent.md' \
  "$SRC/" "$ROOT/"

echo "$UPSTREAM_SHA" > "$ROOT/.upstream-sha"

cd "$ROOT"
if git diff --quiet && git diff --cached --quiet; then
  echo "No changes from upstream."
  exit 0
fi

git add -A
if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
  git -c user.name='github-actions[bot]' \
    -c user.email='41898282+github-actions[bot]@users.noreply.github.com' \
    commit -m "chore: sync upstream cursor/plugins@$UPSTREAM_SHA" \
    -m "Source: https://github.com/cursor/plugins/tree/$UPSTREAM_SHA/pstack"
else
  git commit -m "chore: sync upstream cursor/plugins@$UPSTREAM_SHA" -m "Source: https://github.com/cursor/plugins/tree/$UPSTREAM_SHA/pstack"
fi
echo "Committed sync for $UPSTREAM_SHA"
