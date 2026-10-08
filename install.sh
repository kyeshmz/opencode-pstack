#!/usr/bin/env bash
# Install pstack skills/agents to Claude Code and OpenCode (plus Cursor).
# Usage: ./install.sh [--claude] [--opencode] [--cursor] (default: claude + opencode)
#
# OpenCode and Claude Code require each SKILL.md frontmatter `name` to be
# lowercase-hyphen and match its directory name (^[a-z0-9]+(-[a-z0-9]+)*$).
# Upstream violates this for poteto-mode ("Poteto Mode") and make-bot-ui
# ("Make Bot UI"), so those skills never register. This installer rewrites the
# `name:` line to the directory slug on install. Repo files stay pristine
# (upstream-owned, overwritten on every sync).
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

# Copy a skills/ or agents/ tree, normalizing frontmatter `name` to the
# directory/file slug when it does not match ^[a-z0-9]+(-[a-z0-9]+)*$.
install_tree_normalized() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  cp -R "$src/." "$dest/"
  python3 - "$dest" <<'EOF'
import os, re, sys
dest = sys.argv[1]
pat = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
fixed = []
for entry in sorted(os.listdir(dest)):
    full = os.path.join(dest, entry)
    if entry.startswith('.'):
        continue
    if os.path.isdir(full):
        md = os.path.join(full, 'SKILL.md')
        slug = entry
    elif entry.endswith('.md'):
        md = full
        slug = entry[:-3]
    else:
        continue
    if not os.path.exists(md):
        continue
    txt = open(md).read()
    m = re.match(r'\A---\n(.*?)\n---', txt, re.S)
    if not m:
        continue
    fm = m.group(1)
    nm = re.search(r'^name:\s*(.+?)\s*$', fm, re.M)
    if nm and nm.group(1).strip().strip('\'"') != slug:
        new_fm = re.sub(r'^name:\s*.+?$', f'name: {slug}', fm, count=1, flags=re.M)
        open(md, 'w').write(txt[:m.start(1)] + new_fm + txt[m.end(1):])
        fixed.append(slug)
if fixed:
    print(f'normalized names: {", ".join(fixed)}')
EOF
  echo "installed $src -> $dest"
}

copy_dir() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  cp -R "$src/." "$dest/"
  echo "installed $src -> $dest"
}

if [ "$DO_CLAUDE" -eq 1 ]; then
  install_tree_normalized "$ROOT/skills" "$HOME/.claude/skills"
  if [ -d "$ROOT/agents" ]; then
    install_tree_normalized "$ROOT/agents" "$HOME/.claude/agents"
  fi
fi

if [ "$DO_OPENCODE" -eq 1 ]; then
  install_tree_normalized "$ROOT/skills" "$HOME/.config/opencode/skills"
  if [ -d "$ROOT/agents" ]; then
    install_tree_normalized "$ROOT/agents" "$HOME/.config/opencode/agents/pstack"
  fi
  # Sol model role mapping: readable both as an OpenCode instructions file
  # and at the ~/.cursor/rules path the skill bodies reference verbatim.
  mkdir -p "$HOME/.config/opencode/instructions"
  cp "$ROOT/opencode/pstack-models.md" "$HOME/.config/opencode/instructions/pstack-models.md"
  echo "installed opencode/pstack-models.md -> $HOME/.config/opencode/instructions/pstack-models.md"
  mkdir -p "$HOME/.cursor/rules"
  cp "$ROOT/opencode/pstack-models.md" "$HOME/.cursor/rules/pstack-models.mdc"
  echo "installed opencode/pstack-models.md -> $HOME/.cursor/rules/pstack-models.mdc"
  # Register the instructions file in opencode.json (idempotent, backs up first).
  python3 - "$HOME" <<'EOF'
import json, os, shutil, sys
home = sys.argv[1]
cfg_path = os.path.join(home, '.config/opencode/opencode.json')
entry = os.path.join(home, '.config/opencode/instructions/pstack-models.md')
with open(cfg_path) as f:
    cfg = json.load(f)
inst = cfg.get('instructions') or []
if entry not in inst:
    shutil.copy(cfg_path, cfg_path + '.bak-pstack')
    cfg['instructions'] = inst + [entry]
    with open(cfg_path, 'w') as f:
        json.dump(cfg, f, indent=2)
        f.write('\n')
    print(f'registered instructions entry (backup at {cfg_path}.bak-pstack)')
else:
    print('instructions entry already registered')
EOF
fi

if [ "$DO_CURSOR" -eq 1 ]; then
  copy_dir "$ROOT/skills" "$HOME/.cursor/skills"
  if [ -d "$ROOT/agents" ]; then
    copy_dir "$ROOT/agents" "$HOME/.cursor/agents"
  fi
  mkdir -p "$HOME/.cursor/rules"
  cp "$ROOT/opencode/pstack-models.md" "$HOME/.cursor/rules/pstack-models.mdc"
  echo "installed opencode/pstack-models.md -> $HOME/.cursor/rules/pstack-models.mdc"
fi

echo "done."
echo "Claude Code plugin alternative: claude plugin marketplace add <owner>/<repo>"
