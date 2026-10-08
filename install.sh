#!/usr/bin/env bash
# Install pstack skills/agents to Claude Code and OpenCode.
# Usage: ./install.sh [--claude] [--opencode] [--cursor] (default: claude + opencode)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DO_CLAUDE=0
DO_OPENCODE=0
DO_CURSOR=0

if [ "$#" -eq 0 ]; then
  DO_CLAUDE=1
  DO_OPENCODE=1
else
  for a in "$@"; do
    case "$a" in
      --claude) DO_CLAUDE=1 ;;
      --opencode) DO_OPENCODE=1 ;;
      --cursor) DO_CURSOR=1 ;;
      --all) DO_CLAUDE=1; DO_OPENCODE=1; DO_CURSOR=1 ;;
      *) echo "unknown flag: $a (use --claude --opencode --cursor --all)"; exit 1 ;;
    esac
  done
fi

copy_dir() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  cp -R "$src/." "$dest/"
  echo "installed $src -> $dest"
}

if [ "$DO_CLAUDE" -eq 1 ]; then
  copy_dir "$ROOT/skills" "$HOME/.claude/skills"
  if [ -d "$ROOT/agents" ]; then
    copy_dir "$ROOT/agents" "$HOME/.claude/agents"
  fi
fi

if [ "$DO_OPENCODE" -eq 1 ]; then
  copy_dir "$ROOT/skills" "$HOME/.config/opencode/skills"
fi

if [ "$DO_CURSOR" -eq 1 ]; then
  copy_dir "$ROOT/skills" "$HOME/.cursor/skills"
  if [ -d "$ROOT/agents" ]; then
    copy_dir "$ROOT/agents" "$HOME/.cursor/agents"
  fi
fi

echo "done."
echo "Claude Code plugin alternative: claude plugin marketplace add <owner>/<repo>"
