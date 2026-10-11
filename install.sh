#!/usr/bin/env bash
# Install OpenCode by default; other hosts are explicit compatibility targets.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DO_CLAUDE=0
DO_OPENCODE=0
DO_CURSOR=0

if [ "$#" -eq 0 ]; then
  DO_OPENCODE=1
else
  for arg in "$@"; do
    case "$arg" in
      --claude) DO_CLAUDE=1 ;;
      --opencode) DO_OPENCODE=1 ;;
      --cursor) DO_CURSOR=1 ;;
      --all) DO_CLAUDE=1; DO_OPENCODE=1; DO_CURSOR=1 ;;
      *) echo "unknown flag: $arg (use --opencode --claude --cursor --all)" >&2; exit 1 ;;
    esac
  done
fi

if [ "$DO_OPENCODE" -eq 1 ]; then
  python3 "$ROOT/scripts/install-opencode.py" "$ROOT" "${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
fi

# Compatibility installs retain upstream tool names and paths.
if [ "$DO_CLAUDE" -eq 1 ]; then
  mkdir -p "$HOME/.claude/skills" "$HOME/.claude/agents"
  cp -R "$ROOT/skills/." "$HOME/.claude/skills/"
  cp -R "$ROOT/agents/." "$HOME/.claude/agents/"
  python3 - "$ROOT/skills" "$HOME/.claude/skills" <<'PY'
from pathlib import Path
import re, sys
for source in Path(sys.argv[1]).rglob('SKILL.md'):
    md = Path(sys.argv[2]) / source.relative_to(sys.argv[1])
    text = md.read_text()
    frontmatter = re.match(r'\A---\n(.*?)\n---', text, re.S)
    if frontmatter:
        normalized = re.sub(r'^name:.*$', f'name: {md.parent.name}', frontmatter[1], count=1, flags=re.M)
        md.write_text(text[:frontmatter.start(1)] + normalized + text[frontmatter.end(1):])
PY
  echo "installed Claude Code compatibility skills and agents"
fi

if [ "$DO_CURSOR" -eq 1 ]; then
  mkdir -p "$HOME/.cursor/skills" "$HOME/.cursor/agents"
  cp -R "$ROOT/skills/." "$HOME/.cursor/skills/"
  cp -R "$ROOT/agents/." "$HOME/.cursor/agents/"
  echo "installed Cursor compatibility skills and agents"
fi

echo "done."
