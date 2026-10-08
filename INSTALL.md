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
./install.sh --opencode  # ~/.config/opencode/skills
```

### Claude Code (plugin)

This repo ships `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`:

```
claude plugin marketplace add <github-owner>/<github-repo>
claude plugin install pstack
```

### OpenCode

OpenCode loads Agent Skills from `~/.config/opencode/skills/` (global) or
`.opencode/skills/` (project). `install.sh --opencode` copies there. No
`opencode.json` plugin entry needed because these are skills, not a JS plugin.

Then run `/setup-pstack`, then `/poteto-mode`.

## Overlay files (not overwritten by sync)

- `.claude-plugin/` — Claude Code plugin + marketplace manifests
- `scripts/sync-upstream.sh` — sync script
- `.github/workflows/sync-upstream.yml` — auto-sync workflow
- `install.sh`, `INSTALL.md`, `.upstream-sha`

Everything else (`skills/`, `agents/`, `docs/`, `automations/`, `assets/`,
`.cursor-plugin/`, `README.md`, `LICENSE`, `.gitignore`) is upstream-owned
and gets overwritten on each sync.
