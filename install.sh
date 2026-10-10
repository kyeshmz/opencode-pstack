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
# When $3 is "opencode", also inject OpenCode skill metadata into
# SKILL.md files (repo files stay pristine; transform is install-time only):
#   metadata:
#     opencode/slash: "true"        (forward-compat with OpenCode builds
#                                    that expose skills as /<name>; the
#                                    v2.0.26 binary ignores it, so the
#                                    installer ALSO generates commands/
#                                    wrappers below, which is what actually
#                                    registers /<name> in the TUI.
#                                    See https://opencode.ai/docs/skills/
#                                    and https://opencode.ai/docs/commands/.)
#     opencode/autoinvoke: "false"  (only when upstream sets
#                                    disable-model-invocation: true,
#                                    preserving Cursor's manual-only intent)
install_tree_normalized() {
  local src="$1" dest="$2" mode="${3:-}"
  mkdir -p "$dest"
  cp -R "$src/." "$dest/"
  python3 - "$dest" "$mode" <<'EOF'
import os, re, sys
dest = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else ""
want_slash = (mode == "opencode")
pat = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
fixed = []
slashed = []
for entry in sorted(os.listdir(dest)):
    full = os.path.join(dest, entry)
    if entry.startswith('.'):
        continue
    if os.path.isdir(full):
        md = os.path.join(full, 'SKILL.md')
        slug = entry
        is_skill = True
    elif entry.endswith('.md'):
        md = full
        slug = entry[:-3]
        is_skill = False
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
        fm = re.sub(r'^name:\s*.+?$', f'name: {slug}', fm, count=1, flags=re.M)
        fixed.append(slug)
    if want_slash and is_skill:
        manual_only = bool(re.search(r'^disable-model-invocation:\s*true\s*$', fm, re.M))
        has_slash = 'opencode/slash' in fm
        has_autoinvoke = 'opencode/autoinvoke' in fm
        if 'metadata:' not in fm:
            block = 'metadata:\n  opencode/slash: "true"'
            if manual_only:
                block += '\n  opencode/autoinvoke: "false"'
            fm = fm.rstrip('\n') + '\n' + block + '\n'
        else:
            if not has_slash:
                fm = re.sub(r'^metadata:\s*$', 'metadata:\n  opencode/slash: "true"',
                            fm, count=1, flags=re.M)
            if manual_only and not has_autoinvoke:
                fm = re.sub(r'^metadata:\s*$', 'metadata:\n  opencode/autoinvoke: "false"',
                            fm, count=1, flags=re.M)
                # If slash was just added above, metadata: line is gone;
                # append autoinvoke under the slash line instead.
                if 'opencode/autoinvoke' not in fm:
                    fm = re.sub(r'^(  opencode/slash:.*)$',
                                r'\1\n  opencode/autoinvoke: "false"',
                                fm, count=1, flags=re.M)
        if not has_slash or (manual_only and not has_autoinvoke):
            slashed.append(slug)
    if txt[:m.start(1)] + fm + txt[m.end(1):] != txt:
        open(md, 'w').write(txt[:m.start(1)] + fm + txt[m.end(1):])
if fixed:
    print(f'normalized names: {", ".join(fixed)}')
if slashed:
    print(f'opencode slash enabled: {len(slashed)} skills')
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
  install_tree_normalized "$ROOT/skills" "$HOME/.config/opencode/skills" opencode
  if [ -d "$ROOT/agents" ]; then
    # Flat layout: an agents/*.md file named <x>.md registers agent <x>.
    # A pstack/ subdir would namespace them (pstack/poteto-agent) and break
    # the `subagent_type: "poteto-agent"` references in the skill bodies.
    install_tree_normalized "$ROOT/agents" "$HOME/.config/opencode/agents"
    # Clean up the old nested location (only the two files we put there).
    rm -f "$HOME/.config/opencode/agents/pstack/poteto-agent.md" "$HOME/.config/opencode/agents/pstack/comment-sicko.md"
    rmdir "$HOME/.config/opencode/agents/pstack" 2>/dev/null || true
  fi
  # Cursor-to-OpenCode conversion (repo files stay pristine; the transform
  # rewrites the installed copies and fails loudly on upstream drift).
  # Scoped to this repo's own skills/agents so the user's unrelated global
  # skills are never touched.
  python3 "$ROOT/scripts/opencode-transform.py" \
    "$ROOT/skills" "$HOME/.config/opencode/skills" \
    "$ROOT/agents" "$HOME/.config/opencode/agents"
  # OpenCode keeps skills (loaded on demand via the `skill` tool) and slash
  # commands (commands/*.md -> /<name> in the TUI) as separate mechanisms:
  # skills do NOT automatically appear as /commands. Generate one thin
  # wrapper per installed skill that loads it via the `skill` tool and
  # forwards any typed arguments. Generated files carry a marker comment;
  # reinstalls only write files that are missing or already marked, so a
  # user's own commands/<name>.md is never clobbered. Stale marked wrappers
  # (skill removed upstream) are deleted.
  python3 - "$ROOT/skills" "$HOME/.config/opencode/skills" "$HOME/.config/opencode/commands" <<'EOF'
import os, re, sys
repo_dir, skills_dir, cmds_dir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(cmds_dir, exist_ok=True)
marker = '<!-- generated by pstack install.sh (do not edit: overwritten on reinstall) -->'
slugs = set()
# Only wrap this repo's own skills: the global skills dir may contain the
# user's unrelated skills, which must not gain slash commands unasked.
for entry in sorted(os.listdir(repo_dir)):
    if entry.startswith('.'):
        continue
    if not os.path.isdir(os.path.join(repo_dir, entry)):
        continue
    md = os.path.join(skills_dir, entry, 'SKILL.md')
    if not os.path.isfile(md):
        print(f'skipping {entry}: not installed under skills/')
        continue
    txt = open(md).read()
    m = re.match(r'\A---\n(.*?)\n---', txt, re.S)
    if not m:
        print(f'skipping {entry}: no frontmatter')
        continue
    fm = m.group(1)
    def field(key):
        mm = re.search(r'^%s:\s*(.+?)\s*$' % key, fm, re.M)
        return mm.group(1).strip().strip('\'"') if mm else None
    name, desc = field('name'), field('description')
    if not name or not desc:
        print(f'skipping {entry}: missing name/description')
        continue
    slugs.add(entry)
    dest = os.path.join(cmds_dir, entry + '.md')
    desc_q = desc.replace('\\', '\\\\').replace('"', '\\"')
    body = ('---\n'
            'description: "%s"\n'
            '---\n'
            '%s\n\n'
            'Use the `skill` tool to load the "%s" skill, then follow it for this task. Read the full skill content before acting.\n\n'
            '$ARGUMENTS\n') % (desc_q, marker, name)
    if os.path.isfile(dest):
        cur = open(dest).read()
        if marker not in cur:
            print(f'keeping custom commands/{entry}.md (unmarked, skipping)')
            continue
        if cur == body:
            continue
    open(dest, 'w').write(body)
    print(f'wrote commands/{entry}.md')
for f in sorted(os.listdir(cmds_dir)):
    if not f.endswith('.md'):
        continue
    p = os.path.join(cmds_dir, f)
    if not os.path.isfile(p):
        continue
    cur = open(p).read()
    if marker in cur and f[:-3] not in slugs:
        os.remove(p)
        print(f'removed stale commands/{f}')
EOF
  # Sol model role mapping: readable both as an OpenCode instructions file
  # and at the ~/.cursor/rules path the skill bodies reference verbatim.
  mkdir -p "$HOME/.config/opencode/instructions"
  cp "$ROOT/opencode/pstack-models.md" "$HOME/.config/opencode/instructions/pstack-models.md"
  echo "installed opencode/pstack-models.md -> $HOME/.config/opencode/instructions/pstack-models.md"
  mkdir -p "$HOME/.cursor/rules"
  cp "$ROOT/opencode/pstack-models.md" "$HOME/.cursor/rules/pstack-models.mdc"
  echo "installed opencode/pstack-models.md -> $HOME/.cursor/rules/pstack-models.mdc"
  # Register the instructions file in opencode.json (idempotent, backs up first).
  # NOTE: opencode.json is JSONC (comments, trailing commas), so strict
  # json.load fails on real-world configs. Check by plain text search first
  # (common case: already registered, no write needed). Only fall back to a
  # tolerant parse + text insert when the entry is actually missing.
  python3 - "$HOME" <<'EOF'
import os, re, shutil, sys
home = sys.argv[1]
cfg_path = os.path.join(home, '.config/opencode/opencode.json')
entry = os.path.join(home, '.config/opencode/instructions/pstack-models.md')
try:
    raw = open(cfg_path).read()
except FileNotFoundError:
    print(f'no config at {cfg_path}, skipping instructions registration')
    sys.exit(0)
if entry in raw:
    print('instructions entry already registered')
    sys.exit(0)
shutil.copy(cfg_path, cfg_path + '.bak-pstack')
try:
    import json
    cleaned = re.sub(r',(\s*[}\]])', r'\1', raw)  # tolerate trailing commas
    cfg = json.loads(cleaned)
    inst = cfg.get('instructions') or []
    cfg['instructions'] = inst + [entry]
    with open(cfg_path, 'w') as f:
        json.dump(cfg, f, indent=2)
        f.write('\n')
    print(f'registered instructions entry (backup at {cfg_path}.bak-pstack)')
except Exception as e:
    # Last resort: text-insert into an existing "instructions" array,
    # or create the key after the opening brace.
    m = re.search(r'"instructions"\s*:\s*\[(.*?)\]', raw, re.S)
    if m:
        sep = '' if m.group(1).strip() == '' else ', '
        raw = (raw[:m.end(1)] + sep + f'"{entry}"' + raw[m.end(1):])
    else:
        raw = re.sub(r'\{', '{\n  "instructions": [\n    "%s"\n  ],' % entry,
                     raw, count=1)
    open(cfg_path, 'w').write(raw)
    print(f'registered instructions entry via text insert (backup at {cfg_path}.bak-pstack, parse note: {e})')
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
