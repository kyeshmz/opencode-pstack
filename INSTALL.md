# pstack mirror (Claude + OpenCode installable)

Mirror of [`cursor/plugins`](https://github.com/cursor/plugins) `pstack/` only.
Upstream source: https://github.com/cursor/plugins/tree/main/pstack

Sync: `.github/workflows/sync-upstream.yml` runs every 6 hours plus manual dispatch.
It runs `scripts/sync-upstream.sh`, which sparse-checkouts upstream `pstack/`,
rsyncs it over this repo root (preserving overlay files), and **commits each
time there is a change** as `chore: sync upstream cursor/plugins@<sha>`.

Last synced upstream SHA: see `.upstream-sha`.

## Install

Skills are Agent Skills format (`skills/*/SKILL.md`), readable by both tools.

```bash
git clone <this-repo> pstack
cd pstack
./install.sh            # claude + opencode (default)
./install.sh --all      # claude + opencode + cursor
./install.sh --claude   # ~/.claude/skills + ~/.claude/agents
./install.sh --opencode  # ~/.config/opencode/skills + agents + sol model mapping
```

### Why the installer rewrites skill names

OpenCode and Claude Code require each `SKILL.md` frontmatter `name` to match
`^[a-z0-9]+(-[a-z0-9]+)*$` and equal its directory name. Upstream violates this
for `poteto-mode` (`name: Poteto Mode`) and `make-bot-ui` (`name: Make Bot UI`),
so `/poteto-mode` never registers. `install.sh` rewrites the `name:` line to
the directory slug on install for OpenCode and Claude. Repo files stay pristine
(upstream-owned, overwritten on every sync). Cursor copies install verbatim.

### Claude Code (plugin)

This repo ships `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`:

```
claude plugin marketplace add <github-owner>/<github-repo>
claude plugin install pstack
```

### OpenCode

OpenCode loads Agent Skills from `~/.config/opencode/skills/` (global) and turns
each into a slash command. `install.sh --opencode` copies normalized skills there,
installs agents to `~/.config/opencode/agents/pstack/`, and wires the sol model:

- `opencode/pstack-models.md` pins every pstack role to `openai/gpt-5.6-sol`
  (same shape as the `/setup-pstack` rule, so skill bodies resolve verbatim).
- Installed to `~/.config/opencode/instructions/pstack-models.md` and registered
  in `opencode.json` `instructions` (backup at `opencode.json.bak-pstack`),
  plus `~/.cursor/rules/pstack-models.mdc` (the literal path skills read).

Then run `/setup-pstack`, then `/poteto-mode`.

## Overlay files (not overwritten by sync)

- `.claude-plugin/` — Claude Code plugin + marketplace manifests
- `opencode/` — OpenCode overlays (sol model role mapping)
- `scripts/sync-upstream.sh` — sync script
- `.github/workflows/sync-upstream.yml` — auto-sync workflow
- `install.sh`, `INSTALL.md`, `.upstream-sha`

Everything else (`skills/`, `agents/`, `docs/`, `automations/`, `assets/`,
`.cursor-plugin/`, `README.md`, `LICENSE`, `.gitignore`) is upstream-owned
and gets overwritten on each sync.
