#!/usr/bin/env bash
# One-line entry point: download a disposable checkout, then run its installer.
set -euo pipefail

for dependency in git python3; do
  if ! command -v "$dependency" >/dev/null 2>&1; then
    echo "pstack requires $dependency; install it and try again" >&2
    exit 1
  fi
done

REPOSITORY="${PSTACK_REPOSITORY:-https://github.com/kyeshmz/opencode-pstack.git}"
REF="${PSTACK_REF:-main}"
CHECKOUT="$(mktemp -d "${TMPDIR:-/tmp}/opencode-pstack-install.XXXXXX")"
trap 'rm -rf "$CHECKOUT"' EXIT

git clone --quiet --depth=1 --branch "$REF" "$REPOSITORY" "$CHECKOUT/repo"
bash "$CHECKOUT/repo/install.sh" "$@"
