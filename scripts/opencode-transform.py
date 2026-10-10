#!/usr/bin/env python3
"""Install-time OpenCode conversion for pstack skills/agents.

Usage: opencode-transform.py <installed-skills-dir> <installed-agents-dir>

Repo files stay pristine (upstream-owned, overwritten on every sync). This
rewrites the INSTALLED copies: Cursor tool names/params become OpenCode ones
(`subagent` tool with `agent:`, `question` tool), Cursor paths become OpenCode
paths (`.opencode/skills/`, `~/.config/opencode/skills/`, session CLI instead
of `~/.cursor/projects/` transcripts), and Cursor-platform features without an
OpenCode equivalent (`/loop`, `deslop`/`cursor-team-kit`, cloud agents) become
explicit run-native instructions.

Each rule asserts its expected hit count and the script exits 1 on mismatch,
so an upstream rewording fails loudly instead of half-applying. Idempotent:
install.sh re-copies from the repo before running this.

Deliberately NOT converted (see INSTALL.md):
- `~/.cursor/rules/pstack-models.mdc`: the installer mirrors that path, and
  `setup-pstack` writes it, so it works on disk on any host.
- Model slugs (`claude-opus-5-5-xhigh`, ...): overridden by the installed
  rule; the rejection-fallback prose still applies.
- `make-bot-ui` (Cursor webhook platform), `origin`/`gh`/Bugbot forge refs.
"""

import os
import sys

REPO_SKILLS = sys.argv[1]
INSTALLED_SKILLS = sys.argv[2]
REPO_AGENTS = sys.argv[3]
INSTALLED_AGENTS = sys.argv[4]

# Overlay-owned: never rewritten (this file documents the raw Cursor strings
# the rules match on, so rewriting it would corrupt the doc).
SKIP_BASENAMES = {'opencode-port-agent.md'}

# (scope, old, new, expected_hits)
# scope None = every *.md under both dirs; otherwise a path relative to SKILLS.
RULES = [
    # ---- generic tool renames (all md files) ----
    (None, '`subagent_type`: `generalPurpose`', '`agent`: `general`', 6),
    (None, '`subagent_type: "poteto-agent"`', '`agent: "poteto-agent"`', 3),
    (None, '`subagent_type: "Comment Sicko"`', '`agent: "comment-sicko"`', 1),
    (None, 'Substituting `generalPurpose`', 'Substituting `general`', 1),
    (None, 'the Task tool', 'the `subagent` tool', 9),
    (None, 'one Task subagent', 'one subagent', 2),
    (None, 'Spawn `Task` with', 'Spawn a `subagent` with', 1),
    (None, 'Defaults for every `Task` call', 'Defaults for every `subagent` call', 1),
    (None, 'omit Task `model`', 'omit subagent `model`', 2),
    (None, 'Multiple `Task` calls', 'Multiple `subagent` calls', 1),
    (None, '`Task` prompts that name a skill path', '`subagent` prompts that name a skill path', 3),
    (None, 'in the `Task` response body', 'in the `subagent` response body', 1),
    (None, '`run_in_background: true`', '`background: true`', 2),
    (None, '- `readonly`: `true`', '- read-only permissions (deny file edits)', 4),
    (None, '- `readonly`: `false` (agent mode)', '- full tool access', 2),
    (None, 'agent mode (`readonly: false`)', 'full tool access', 1),
    (None, 'Readonly strips MCPs.', 'Restricted permissions strip MCP access.', 2),
    # ---- AskQuestion -> question tool ----
    (None, 'Prefer AskQuestion over free text.', 'Prefer the `question` tool over free text.', 2),
    (None, 'About to `AskQuestion` on', 'About to use the `question` tool on', 1),
    (None, 'or use `AskQuestion`.', 'or use the `question` tool.', 1),
    (None, 'confirm intent with `AskQuestion`', 'confirm intent with the `question` tool', 1),
    (None, 'Use the `AskQuestion` tool (structured multi-choice)',
     'Use the `question` tool (structured multi-choice)', 1),
    (None, '`allow_multiple: true`', '`multiple: true`', 1),
    # ---- poteto-mode ----
    ('poteto-mode/SKILL.md',
     "Agent-facing prose also follows the **create-skill** skill (Cursor's built-in for authoring SKILL.md files).",
     'Agent-facing prose also follows the Agent Skills format (a `<dir>/SKILL.md` with `name`/`description` frontmatter).',
     1),
    ('poteto-mode/SKILL.md',
     'Before commit → the `deslop` skill from the `cursor-team-kit` plugin (`/deslop`).',
     'Before commit → a manual slop-strip pass over the diff.', 1),
    ('poteto-mode/SKILL.md',
     'Shipping UI / IDE / CLI → the matching control skill. `cursor-team-kit` publishes `control-cli` (CLIs and TUIs) and `control-ui` (browser / Electron / web UIs). For bug fixes, reproduce first on the same surface yourself.',
     "Shipping UI / IDE / CLI → the matching verification skill: a project `verify-*` skill for the surface (generate one with `/create-verification-skill` if none exists). For bug fixes, reproduce first on the same surface yourself.",
     1),
    ('poteto-mode/SKILL.md',
     "and not Cursor's built-in babysit skill, whose description matches the same words.",
     'and not any other similarly-named babysit skill.', 1),
    ('poteto-mode/SKILL.md',
     'Reaching for `drive` inside a phase agent stops that agent finishing its turn.',
     'Starting a babysit `drive` loop inside a phase agent stops that agent finishing its turn.', 1),
    ('poteto-mode/SKILL.md', '"/loop until X"', '"run until X"', 2),
    ('poteto-mode/SKILL.md',
     'set their own `subagent_type` for diverse-model review',
     'set their own `agent` for diverse-model review', 1),
    ('poteto-mode/SKILL.md',
     'from a transcript, cloud-agent URL, or pushed branch',
     'from an exported session or pushed branch', 1),
    ('poteto-mode/SKILL.md', 'a Cursor restart', 'an app restart', 1),
    ('poteto-mode/SKILL.md',
     'agent mode (readonly strips MCP)',
     'full tool access (restricted permissions strip MCP access)', 1),
    # ---- why ----
    ('why/SKILL.md',
     'open files, recent edits, cursor location, what was just discussed',
     'open files, recent edits, what was just discussed', 1),
    ('why/SKILL.md',
     "list the available MCPs from the Cursor environment. Use the available-tools map when present. Otherwise inspect the `mcps/` directory Cursor exposes for enabled MCP servers.",
     "list the available MCPs from this session's tool list.", 1),
    ('why/SKILL.md',
     'Do not use readonly/Ask mode.',
     'Do not use a restricted-permission agent.', 1),
    ('why/SKILL.md',
     'Readonly/Ask mode strips MCPs and defeats that.',
     'A restricted-permission agent strips MCPs and defeats that.', 1),
    # ---- arena ----
    ('arena/SKILL.md',
     'Spawn one readonly judge subagent on that model',
     'Spawn one judge subagent with read-only permissions on that model', 1),
    # ---- swarm ----
    ('swarm/SKILL.md',
     'Fan out N parallel cloud workers.',
     'Fan out N parallel workers.', 1),
    ('swarm/SKILL.md',
     'N is total workers, not the cloud concurrency limit.',
     'N is total workers.', 1),
    ('swarm/SKILL.md',
     'Spawn all N workers in one message with `subagent_type: generalPurpose`, `environment: "cloud"`, `run_in_background: true`, and the step 4 model, left unset for `auto` or `inherit-parent`. Use `environment: "local"` only when the worker needs access to something on the user\'s computer.',
     "Spawn all N workers in one message with `agent: general`, `background: true`, and the step 4 model, left unset for `auto` or `inherit-parent`. Workers run on this machine with the user's tools and filesystem.",
     1),
    ('swarm/SKILL.md',
     'When a worker must start from a non-default pushed branch, pass `cloud_base_branch`.',
     'When a worker must start from a non-default pushed branch, its brief names the branch and tells it to check that branch out first.',
     1),
    # ---- reflect ----
    ('reflect/SKILL.md',
     """### 1. Locate the active transcript

The parent finds its own transcript file before fanning out. The system prompt names the active workspace's `agent-transcripts/` directory. Use that path. Do not glob across `~/.cursor/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.

```bash
ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10
```

Three transcript layouts: legacy flat (`<id>.jsonl`), current nested (`<id>/<id>.jsonl`), and subagent (`<parent>/subagents/<child>.jsonl`).

For each candidate, read the first JSONL line and check that `message.content[0].text` contains the conversation's opening user prompt. Take the matching path. If no path resolves, write a tight digest of the session and pass that instead.""",
     """### 1. Locate the active transcript

Export the current session to a file the reviewers can read. Find its ID with `opencode session list --format json` from the project directory (the current session is the most recently updated; match by recency and title), then `opencode session export <id> > /tmp/reflect-<id>.json`. Pass that path where the reviewer templates say `<ABSOLUTE_PATH>`. Never export another project's sessions. If no session resolves, write a tight digest of the session and pass that instead.""",
     1),
    ('reflect/SKILL.md',
     'One message, three `Task` calls, `subagent_type: generalPurpose`, with `model` set as below, agent mode (`readonly: false`).',
     'One message, three `subagent` calls with `agent: general`, `model` set as below, and full tool access.',
     1),
    ('reflect/SKILL.md',
     'One `Task` call, `subagent_type: generalPurpose`, with `model` from the `reflect judgment, divergent, synthesizer` line',
     'One `subagent` call with `agent: general`, `model` from the `reflect judgment, divergent, synthesizer` line',
     1),
    ('reflect/SKILL.md',
     "hand to Cursor's built-in `create-skill` skill and run its draft / test / iterate loop.",
     'draft, test, and iterate the SKILL.md directly (frontmatter `name` matching its directory, one-scalar `description`).',
     1),
    ('reflect/SKILL.md',
     'hand to `create-skill` and run its description-optimization loop.',
     'rewrite its `description` directly and re-test whether it triggers.', 1),
    ('reflect/SKILL.md',
     'hand creation to `create-skill`. Do not invent the shape ad hoc.',
     'draft the `<kebab-name>/SKILL.md` directly in the Agent Skills shape. Do not invent the shape ad hoc.',
     1),
    ('reflect/SKILL.md',
     '`new skill via create-skill: <kebab-name>`',
     '`new skill: <kebab-name>`', 1),
    # ---- reflect references (same two rules in all three files) ----
    ('reflect/references/judgment-reviewer.md',
     '- `Read` tool calls against any `SKILL.md` file (workspace `.cursor/skills/`, user-level `~/.cursor/skills/`, or plugin-installed paths under `~/.cursor/plugins/`)',
     '- `Read` tool calls against any `SKILL.md` file (project `.opencode/skills/`, user-level `~/.config/opencode/skills/`, or plugin-provided skill paths)',
     1),
    ('reflect/references/tooling-reviewer.md',
     '- `Read` tool calls against any `SKILL.md` file (workspace `.cursor/skills/`, user-level `~/.cursor/skills/`, or plugin-installed paths under `~/.cursor/plugins/`)',
     '- `Read` tool calls against any `SKILL.md` file (project `.opencode/skills/`, user-level `~/.config/opencode/skills/`, or plugin-provided skill paths)',
     1),
    ('reflect/references/divergent-reviewer.md',
     '- `Read` tool calls against any `SKILL.md` file (workspace `.cursor/skills/`, user-level `~/.cursor/skills/`, or plugin-installed paths under `~/.cursor/plugins/`)',
     '- `Read` tool calls against any `SKILL.md` file (project `.opencode/skills/`, user-level `~/.config/opencode/skills/`, or plugin-provided skill paths)',
     1),
    ('reflect/references/synthesizer.md',
     'propose `new skill via create-skill:` only when',
     'propose `new skill:` only when', 1),
    ('reflect/references/synthesizer.md',
     '<draft a new skill via create-skill>',
     '<draft a new SKILL.md directly>', 1),
    ('reflect/references/synthesizer.md',
     '<new skill via create-skill: <kebab-name>>',
     '<new skill: <kebab-name>>', 1),
    # ---- recall ----
    ('recall/SKILL.md',
     'Transcripts live at `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl`, where `<slug>` is the workspace path with the leading slash dropped and each "/" turned into "-" (so `/Users/you/proj` becomes `Users-you-proj`). Every line is one chat message.',
     'Sessions are listed per project with `opencode session list --format json` (run from the project directory; newest first) and read with `opencode session export <session-id>` (full transcript as JSON; add `--sanitize` when the content will be logged or quoted). Never search another project\'s sessions without being asked.',
     1),
    ('recall/SKILL.md',
     'Tell every subagent to order candidates by real modification time (`ls -t`) and never by UUID name',
     'Tell every subagent to order candidates by recency (`session list` is newest-first) and never by session-ID name',
     1),
    ('recall/SKILL.md',
     'each citing the chat UUID',
     'each citing the session ID', 1),
    # ---- show-me-your-work ----
    ('show-me-your-work/SKILL.md',
     "Read this run's transcript under the active workspace's `agent-transcripts/` directory (the system prompt names the path). Don't glob across `~/.cursor/projects/*/`. That reads unrelated private chats.",
     "Read this run's transcript with `opencode session export <this session's ID>` (find it via `opencode session list --format json` from the project directory). Don't trawl other projects' sessions. That reads unrelated private chats.",
     1),
    # ---- automate-me ----
    ('automate-me/SKILL.md', '~/.cursor/skills/', '~/.config/opencode/skills/', 2),
    ('automate-me/SKILL.md', '.cursor/skills/', '.opencode/skills/', 4),
    ('automate-me/SKILL.md',
     "This skill orchestrates three others: an inline mining pass (see step 1), Cursor's built-in `create-skill` (authoring), and the **unslop** skill (prose discipline). It sequences them. It doesn't replace them.",
     "This skill orchestrates three others: an inline mining pass (see step 1), direct SKILL.md authoring (see step 4), and the **unslop** skill (prose discipline). It sequences them. It doesn't replace them.",
     1),
    ('automate-me/SKILL.md',
     "Locate the active workspace's transcripts before fanning out. The system prompt names the workspace's `agent-transcripts/` directory. Use only that path. Don't glob across `~/.cursor/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.",
     "Locate the active workspace's sessions before fanning out: `opencode session list --format json` from the project directory, newest first. Use only that project's sessions. Don't search other projects' sessions. That crosses workspace boundaries and reads private chats from unrelated projects.",
     1),
    ('automate-me/SKILL.md',
     "Use Cursor's built-in `create-skill` skill to author the skill.",
     'Author the SKILL.md directly in the Agent Skills shape (`name` matching its directory, one-scalar `description`).',
     1),
    ('automate-me/SKILL.md',
     "follow `create-skill`'s YAML rules.",
     'follow plain YAML rules.', 1),
    ('automate-me/SKILL.md',
     'Apply the **unslop** skill and `create-skill`\'s writing guidelines to every line.',
     'Apply the **unslop** skill to every line.', 1),
    ('automate-me/SKILL.md',
     "A `create-skill`-style test/iterate benchmark loop isn't useful here.",
     "A test/iterate benchmark loop isn't useful here.", 1),
    ('automate-me/SKILL.md',
     '`create-skill` alone, no mining required.',
     'Direct SKILL.md authoring alone, no mining required.', 1),
    ('automate-me/SKILL.md',
     'Drafts or revises a personal -mode skill via create-skill + unslop',
     'Drafts or revises a personal -mode skill by direct authoring + unslop', 1),
    # ---- setup-pstack ----
    ('setup-pstack/SKILL.md',
     'model slugs you can pass to a `Task` subagent in this session',
     'models you can pass to a `subagent` call in this session (`opencode models` lists them as `providerID/modelID`)',
     1),
    ('setup-pstack/SKILL.md',
     "If Cursor also exposes a models API or CLI that lists the user's entitled models, prefer it for completeness.",
     "If the host also exposes a models API or CLI that lists the user's entitled models (`opencode models` on OpenCode), prefer it for completeness.",
     1),
    ('setup-pstack/SKILL.md',
     'on the ladder `max` > `xhigh` > `high` > `medium` > `low`.',
     'on the ladder `max` > `xhigh` > `high` > `medium` > `low`. Slugs without an effort token (such as OpenCode `providerID/modelID` IDs) have nothing to adjust: keep the slug unless the user picks another detected model.',
     1),
    # ---- poteto-help ----
    ('poteto-help/SKILL.md',
     """Whether `/poteto-mode` stays on depends on how the user starts it:

- Enter on `/poteto-mode` attaches the skill to one message. It fades as the chat moves on.
- Option+Enter on Mac or Alt+Enter on Windows, or Use as Mode from the skill entry, makes it a Custom Mode. It stays in context every turn until the user exits the mode, and it stays out of casual turns.
- Cursor's docs list Custom Modes in the Agents Window and the CLI. Elsewhere, start each new task with `/poteto-mode`.""",
     "Start each new task with `/poteto-mode`. It runs as one message and fades as the chat moves on, so re-invoke it when the task changes. (On Cursor, Option+Enter pins it as a persistent Custom Mode. OpenCode has no equivalent.)",
     1),
    ('poteto-help/SKILL.md',
     "Link [Cursor's skills docs](https://cursor.com/docs/skills)",
     "Link [OpenCode's skills docs](https://opencode.ai/docs/skills)", 1),
    (None, 'as cloud agents', 'as background subagents', 1),
    ('poteto-help/SKILL.md',
     '- `/deslop`, `control-cli`, and `control-ui` ship in the `cursor-team-kit` plugin.',
     '- No `deslop` or `control-*` plugin ships on OpenCode: strip slop by hand and drive each surface with a project `verify-*` skill.',
     1),
    ('poteto-help/SKILL.md',
     '- `/loop` and `/create-skill` are Cursor built-ins.',
     '- No `/loop` on OpenCode: keep watches inside the run. No built-in skill authoring: write SKILL.md files directly.',
     1),
    ('poteto-help/SKILL.md',
     "can start Cursor's own skill for the same job instead",
     'can start another similarly-named skill instead', 1),
    ('poteto-help/SKILL.md',
     "Cursor's Plan Mode works alongside it.",
     "OpenCode's plan agent (Tab to switch) works alongside it.", 1),
    ('poteto-help/SKILL.md',
     'It was started with Enter. Start it as a Custom Mode, or start each task with `/poteto-mode`.',
     'Start each task with `/poteto-mode`.', 1),
    ('poteto-help/SKILL.md',
     'Give each agent its own worktree, or run them as cloud agents, which each get their own machine.',
     'Give each agent its own worktree.', 1),
    ('poteto-help/SKILL.md',
     'do the work under it, and mention once that a Custom Mode keeps it on.',
     'do the work under it, and mention once that starting each task with `/poteto-mode` keeps it on.',
     1),
    ('poteto-help/SKILL.md',
     '`/loop` needs a check that can pass or fail, not a duration.',
     'An overnight run needs a check that can pass or fail, not a duration.', 1),
    ('poteto-help/SKILL.md',
     'pstack is built for Cursor. Its skills use the Agent Skills format, so other tools can read them. But most workflow skills, including `/poteto-mode`, `/how`, `/why`, and `/teach`, spawn Cursor subagents with per-role models, and Custom Modes and `/loop` are Cursor features, so those parts may not work there.',
     'pstack was built for Cursor; this install rewrites the Cursor-only parts (subagent tool names, session lookup, `/loop`, cloud agents) to OpenCode equivalents. Custom Modes have no equivalent: start each task with `/poteto-mode`.',
     1),
    ('poteto-help/references/recipes.md', '/loop until done', 'run until done', 1),
    ('poteto-help/references/prompting.md',
     'give `/loop` that predicate',
     'give the run that predicate', 1),
    # ---- playbooks ----
    ('poteto-mode/playbooks/multi-phase-plan.md',
     'Browser, Electron, and web UIs use `control-ui` from `cursor-team-kit`. CLIs and TUIs use `control-cli` from `cursor-team-kit`. Native mobile uses whatever simulator-driving skill the repo has.',
     "Browser, Electron, web UIs, CLIs, and TUIs use the project's `verify-*` skill for that surface (generate one with `/create-verification-skill` if none exists). Native mobile uses whatever simulator-driving skill the repo has.",
     1),
    ('poteto-mode/playbooks/multi-phase-plan.md',
     'arm the audit tick as `/loop 1h`',
     'arm the hourly audit tick', 1),
    ('poteto-mode/playbooks/multi-phase-plan.md',
     'Run `/deslop` before each commit',
     'Run a manual slop-strip pass before each commit', 1),
    ('poteto-mode/playbooks/multi-phase-plan.md',
     'Each live lane runs on its own cloud VM at the PR head. Drive through `control-ui` or `control-cli` from `cursor-team-kit`.',
     "Each live lane runs at the PR head. Drive it through the surface's `verify-*` skill.",
     1),
    ('poteto-mode/playbooks/opening-a-pr.md',
     'Run `/deslop` from `cursor-team-kit` over the diff before commit.',
     'Run a manual slop-strip pass over the diff before commit.', 1),
    ('poteto-mode/playbooks/opening-a-pr.md',
     'runs `interrogate`, `/deslop`, and `/no-comments`',
     'runs `interrogate`, a manual slop-strip pass, and `/no-comments`', 1),
    ('poteto-mode/playbooks/shipping.md',
     'each a Cursor cloud agent, each exercising the real surface with the matching control skill (such as `control-ui` or `control-cli` from `cursor-team-kit`) against parent versus head',
     "each a background subagent, each exercising the real surface with the matching `verify-*` skill against parent versus head",
     1),
    ('poteto-mode/playbooks/shipping.md',
     'Hold the watch under `/loop` in dynamic mode.',
     'Hold the watch inside this run.', 1),
    ('poteto-mode/playbooks/babysit.md',
     "This playbook replaces Cursor's built-in babysit skill for these requests",
     'This playbook replaces any other similarly-named babysit skill for these requests', 1),
    ('poteto-mode/playbooks/babysit.md',
     'Run `drive` and `background` under `/loop` in dynamic mode.',
     'Keep the watch inside this run.', 1),
    ('poteto-mode/playbooks/autopilot-full.md',
     'One Cursor cloud agent per PR owns build',
     'One background subagent per PR owns build', 1),
    ('poteto-mode/playbooks/autopilot-full.md',
     'a slop-strip (the `deslop` skill from the `cursor-team-kit` plugin (`/deslop`))',
     'a manual slop-strip pass over the diff', 1),
    ('poteto-mode/playbooks/autopilot-full.md',
     'arm `/loop 1h` with a prompt that runs this tick. `/loop` works in local and cloud roots.',
     'arm the hourly audit tick with a prompt that runs this tick.', 1),
    ('poteto-mode/playbooks/autopilot-full.md',
     'with the matching control skill, such as `control-cli` or `control-ui` from `cursor-team-kit`, or a named driver where none exists',
     'with the matching `verify-*` skill, or a named driver where none exists', 1),
    ('poteto-mode/playbooks/bug-fix.md',
     "Drive a long or stubborn hunt with Cursor's `/loop` command.",
     'Drive a long or stubborn hunt inside this run.', 1),
    ('poteto-mode/playbooks/authoring-a-skill.md',
     "1. Use the **create-skill** skill (Cursor's built-in for authoring SKILL.md files).",
     '1. Author the SKILL.md directly in the Agent Skills shape (`name` matching its directory, one-scalar `description`).',
     1),
    ('poteto-mode/playbooks/autopilot-stack.md',
     'One Cursor cloud agent per PR owns its change end to end',
     'One background subagent per PR owns its change end to end', 1),
    ('poteto-mode/playbooks/autopilot-stack.md',
     'a slop-strip (the `deslop` skill from the `cursor-team-kit` plugin (`/deslop`))',
     'a manual slop-strip pass over the diff', 1),
    ('poteto-mode/playbooks/autopilot-stack.md',
     'arms `/loop 1h` with a prompt that runs this tick',
     'arms the hourly audit tick with a prompt that runs this tick', 1),
    ('poteto-mode/playbooks/autonomous-run.md',
     "Pick the wake mechanism using Cursor's `/loop` command (a built-in, not a pstack skill).",
     'Pick the wake mechanism: a background watcher subagent.', 1),
    ('poteto-mode/playbooks/visual-parity.md',
     '`/loop` per component until the diff is zero.',
     'Repeat per component until the diff is zero.', 1),
    ('poteto-mode/playbooks/session-pickup.md',
     "A local transcript under the active workspace's `agent-transcripts/` directory (the system prompt names the path. Do not glob across `~/.cursor/projects/*/`, that crosses workspace boundaries and reads private chats from unrelated projects), a cloud-agent URL, or a pushed branch.",
     "An exported session (`opencode session list --format json` from the project directory, then `opencode session export <id>`; never another project's sessions), or a pushed branch.",
     1),
    ('poteto-mode/playbooks/eval.md',
     "Read each candidate's local transcript under the active workspace's `agent-transcripts/` directory (the system prompt names this path). Do not glob across `~/.cursor/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.",
     "Read each candidate's session via `opencode session export <id>` (list with `opencode session list --format json`). Never read another project's sessions. That crosses workspace boundaries and reads private chats from unrelated projects.",
     1),
    ('poteto-mode/playbooks/worktree-cleanup.md',
     "since a hand-typed `myrepo-worktrees/x` misses one that lives at `.cursor/worktrees/myrepo/x` (principle-encode-lessons-in-structure)",
     "since a hand-typed `myrepo-worktrees/x` misses one that lives under a different root (principle-encode-lessons-in-structure)",
     1),
    ('poteto-mode/playbooks/worktree-cleanup.md',
     'The transcript scan is slow, so background it.',
     'The session scan is slow, so run it in a background subagent.', 1),
    ('poteto-mode/playbooks/worktree-cleanup.md',
     'Get that set from the user or sidebar',
     'Get that set from the user or the sessions list', 1),
    ('poteto-mode/playbooks/worktree-cleanup.md',
     'fan subagents out to read the transcripts and report whether the chat is pinned or ongoing',
     'fan subagents out to export and read the sessions and report whether the chat is pinned or ongoing',
     1),
    ('poteto-mode/playbooks/worktree-cleanup.md',
     '`~/Library/Application Support/Cursor` (`state.vscdb.backup`, and `snapshots/roots/<root>` where a `<root>` named for a folder you opened as a workspace balloons)',
     '`~/.local/share/opencode` (the session database, snapshots, and logs, which grow with use)',
     1),
    ('poteto-mode/playbooks/orchestrate.md',
     'a nested spawn has the full Task schema including `environment`',
     'a nested spawn has the full `subagent` schema including `background`', 1),
    ('poteto-mode/playbooks/orchestrate.md',
     '- **Worker / verifier.** Always `environment: "cloud"` unless the task needs this machine: `control-ui` or `control-cli` runtime verification (from `cursor-team-kit`). Reading local transcripts under `agent-transcripts/`. Simulators and local IDE state. Auth that exists only here. Cloud agents cannot read the local store, so their briefs inline what they need or point at repo paths. Prefer fewer, broader workers. One writer per worktree or branch (principle-separate-before-serializing-shared-state). Run a unit\'s verifier on a different model family from its worker.',
     '- **Worker / verifier.** Spawned via the `subagent` tool with `background: true` for parallel waves. Everything runs on this machine, so briefs point at local paths and read the local session store with `opencode session export`. Prefer fewer, broader workers. One writer per worktree or branch (principle-separate-before-serializing-shared-state). Run a unit\'s verifier on a different model family from its worker.',
     1),
    ('poteto-mode/playbooks/orchestrate.md',
     "the cloud agent's status in the Cursor dashboard",
     "the subagent's status", 1),
    ('poteto-mode/playbooks/orchestrate.md',
     'Work that exists only on one VM when that VM dies was never done.',
     "Work that exists only in one worker's unpushed state when that worker ends was never done.",
     1),
    ('poteto-mode/playbooks/orchestrate.md',
     'Local spawns may reference the standing-orders file by store path. Verbatim paste is for cloud spawns and every resume.',
     'Spawns may reference the standing-orders file by store path. Verbatim paste is for every resume.',
     1),
    ('poteto-mode/playbooks/orchestrate.md',
     'its spawn budget with the cloud default and the local exception list',
     'its spawn budget', 1),
    ('poteto-mode/playbooks/orchestrate.md',
     'Restacks run in cloud. A local restack at this scale takes the laptop down.',
     'A restack at this scale is heavy; run it in a background subagent.', 1),
    ('poteto-mode/playbooks/orchestrate.md',
     'After a Cursor restart: local agents are dead, cloud work is not.',
     'After an app restart: running subagents are dead.', 1),
    ('poteto-mode/playbooks/orchestrate.md',
     'reattach cloud work by PR and branch rather than agent id',
     'reattach work by PR and branch rather than agent id', 1),
    ('poteto-mode/playbooks/orchestrate.md',
     'Transcript mtime is not liveness.',
     'Session recency is not liveness.', 1),
    # ---- verify-skill output paths (project-local skills dir differs) ----
    ('create-verification-skill/SKILL.md',
     '.cursor/skills/verify-', '.opencode/skills/verify-', 3),
    ('maintain-verification-skill/SKILL.md',
     '.cursor/skills/verify-', '.opencode/skills/verify-', 1),
    # ---- check-plan marker must match the rewritten tick wording ----
    ('poteto-mode/scripts/check-plan.mjs', '"/loop 1h"', '"hourly audit tick"', 1),
]


def md_files():
    # Only this repo's own skills/agents: the global dirs may hold the user's
    # unrelated skills (and agents/research/), which must never be rewritten.
    for repo_base, inst_base in ((REPO_SKILLS, INSTALLED_SKILLS),
                                 (REPO_AGENTS, INSTALLED_AGENTS)):
        for root, _, files in os.walk(inst_base):
            for f in files:
                if f.endswith('.md') and f not in SKIP_BASENAMES:
                    p = os.path.join(root, f)
                    rel = os.path.relpath(p, inst_base)
                    if os.path.exists(os.path.join(repo_base, rel)):
                        yield p


def main():
    failures = []
    # Scoped (file-specific) rules first: several contain generic patterns
    # (e.g. a full spawn line holding `subagent_type:`), and must match
    # before the generic rewrite removes their anchors.
    ordered = [r for r in RULES if r[0] is not None] + [r for r in RULES if r[0] is None]
    for scope, old, new, expected in ordered:
        if scope is None:
            targets = list(md_files())
        else:
            p = os.path.join(INSTALLED_SKILLS, scope)
            targets = [p] if os.path.isfile(p) else []
            if not targets:
                failures.append(f'{scope}: file missing')
                continue
        hits = 0
        for p in targets:
            txt = open(p).read()
            n = txt.count(old)
            if n:
                hits += n
                open(p, 'w').write(txt.replace(old, new))
        status = 'OK ' if hits == expected else 'FAIL'
        print(f'{status} [{hits}/{expected}] {old[:70]}')
        if hits != expected:
            failures.append(f'{old[:70]}: hit {hits}, expected {expected}')

    # ---- worktree-audit.sh: transcript dir -> session-CLI scan ----
    sh = os.path.join(INSTALLED_SKILLS, 'poteto-mode/scripts/worktree-audit.sh')
    txt = open(sh).read()
    old_a = ("# Transcripts dir: ~/.cursor/projects/<slugified-repo-path>/agent-transcripts.\n"
             "slug=$(printf '%s' \"$main_wt\" | sed 's#^/##; s#/#-#g')\n"
             "transcripts=\"$HOME/.cursor/projects/$slug/agent-transcripts\"\n"
             "now=$(date +%s)\n")
    new_a = ("# Recent chats: on OpenCode, sessions are listed per project (newest first)\n"
             "# and read with `opencode session export`. Export each (capped) once to temp\n"
             "# files, then grep per worktree below.\n"
             "now=$(date +%s)\n"
             "sessions_dir=$(mktemp -d)\n"
             "if command -v opencode >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then\n"
             "\t(cd \"$main_wt\" 2>/dev/null && opencode session list --format json 2>/dev/null \\\n"
             "\t\t| jq -r '.[:40] | .[] | \"\\(.updated) \\(.id)\"') > \"$sessions_dir/index\" 2>/dev/null || true\n"
             "\twhile read -r updated id; do\n"
             "\t\t[ -n \"${id:-}\" ] && opencode session export \"$id\" > \"$sessions_dir/$id.json\" 2>/dev/null || true\n"
             "\tdone < \"$sessions_dir/index\"\n"
             "fi\n")
    old_b = ("\t# Most recent chat whose transcript operated in this worktree. Match path\n"
             "\t# followed by \"/\" or a quote so glint-482 does not match glint-482-r37.\n"
             "\tlast=\"-\"; last_ts=0\n"
             "\tif [ -d \"$transcripts\" ]; then\n"
             "\t\tf=$(rg -l -e \"${wt}/\" -e \"${wt}\\\"\" \"$transcripts\" 2>/dev/null \\\n"
             "\t\t\t| xargs stat -f '%m %N' 2>/dev/null | sort -rn | head -1)\n"
             "\t\tif [ -n \"$f\" ]; then last_ts=$(echo \"$f\" | awk '{print $1}')\n"
             "\t\t\tlast=$(date -r \"$last_ts\" '+%Y-%m-%d' 2>/dev/null); fi\n"
             "\tfi\n")
    new_b = ("\t# Most recent session that operated in this worktree: first hit scanning\n"
             "\t# newest-first. Match path followed by \"/\" or a quote so glint-482 does\n"
             "\t# not match glint-482-r37.\n"
             "\tlast=\"-\"; last_ts=0\n"
             "\tif [ -f \"$sessions_dir/index\" ]; then\n"
             "\t\twhile read -r updated id; do\n"
             "\t\t\tf=\"$sessions_dir/$id.json\"\n"
             "\t\t\tif [ -f \"$f\" ] && grep -q -F -e \"${wt}/\" -e \"${wt}\\\"\" \"$f\" 2>/dev/null; then\n"
             "\t\t\t\tlast_ts=$((updated / 1000))\n"
             "\t\t\t\tlast=$(date -r \"$last_ts\" '+%Y-%m-%d' 2>/dev/null || echo \"?\")\n"
             "\t\t\t\tbreak\n"
             "\t\t\tfi\n"
             "\t\tdone < \"$sessions_dir/index\"\n"
             "\tfi\n")
    old_c = 'rm -f "$prs"\n'
    new_c = 'rm -f "$prs"\nrm -rf "$sessions_dir"\n'
    for label, o, n in (('audit.sh block A', old_a, new_a),
                        ('audit.sh block B', old_b, new_b),
                        ('audit.sh cleanup', old_c, new_c)):
        c = txt.count(o)
        print(f'{"OK " if c == 1 else "FAIL"} [{c}/1] {label}')
        if c != 1:
            failures.append(f'{label}: hit {c}, expected 1')
        else:
            txt = txt.replace(o, n)
    open(sh, 'w').write(txt)

    if failures:
        print(f'\n{len(failures)} rule(s) mismatched:')
        for f in failures:
            print(f'  - {f}')
        sys.exit(1)
    print(f'\nall {len(RULES)} md rules + audit.sh blocks applied')


if __name__ == '__main__':
    main()
