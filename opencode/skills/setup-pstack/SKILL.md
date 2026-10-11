---
name: setup-pstack
description: Configure pstack's per-role models and reasoning budget in OpenCode. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack for OpenCode

## 1. Detect available models

Use the host's models tool, or `opencode models`, to discover available models.
Use exact `providerID/modelID` identifiers and only confirmed `#variant` values.
Do not translate Cursor model slugs by guessing. If discovery is unavailable,
ask the user for their available model IDs. `inherit-parent` and `auto` both
mean to omit the subagent's `model` argument.

## 2. Load current choices

Read `{{CONFIG_DIR}}/instructions/pstack-models.md` if it exists.
Preserve existing role choices. For missing roles, propose `inherit-parent`;
do not pin a model the user has not selected or confirmed. Read the supported
role labels from the template below.

## 3. Ask for budget and confirm the mapping

Use the `question` tool to ask about budget and show every role's proposed
model. A reasoning budget selects an available model variant; it is not a
suffix to invent for a model ID. If the provider offers no matching variant,
explain that limitation and retain the confirmed model or ask for another.

Panel roles accept comma-separated lists, one reviewer per entry.
`arena cross-judge pool` is a list from which Arena chooses one judge.
`swarm workers` applies to each worker unless a race specifies a model per arm.
Wait for approval before writing. Every non-alias entry must be available.

## 4. Write the model configuration

Write `{{CONFIG_DIR}}/instructions/pstack-models.md`, creating its parent
directory if needed. Use plain Markdown, not a Cursor `.mdc` rule or
`alwaysApply` frontmatter. Keep exactly one line per supported role:

```text
# pstack model configuration
# budget: inherit parent (choose confirmed variants during setup)
feature, refactoring: inherit-parent
bug-fix: inherit-parent
perf-issue: inherit-parent
hillclimb: inherit-parent
judgment and prose: inherit-parent
hardest tasks: inherit-parent
how explorer: inherit-parent
how explainer: inherit-parent
why investigators: inherit-parent
why synthesizer: inherit-parent
reflect tooling: inherit-parent
reflect judgment, divergent, synthesizer: inherit-parent
arena runners: inherit-parent, inherit-parent
arena cross-judge pool: inherit-parent, inherit-parent
swarm workers: inherit-parent
architect runners: inherit-parent, inherit-parent
interrogate reviewers: inherit-parent, inherit-parent
```

Skills read this file explicitly. OpenCode V2 does not load the configuration's
`instructions` array. The installer adds a small managed block to global
`{{CONFIG_DIR}}/AGENTS.md` that tells pstack workflows where to read these
choices. Preserve unrelated instructions; do not replace the whole file.

## 5. Confirm and offer verification

Report the exact path written. Start a new session to pick up refreshed skills.
Check the target project's `.opencode/skills/verify-*/` and existing harnesses.
If no suitable harness exists, offer `/create-verification-skill` once. On yes,
load that skill and create the output in the target project, not the global
installation. On no, move on.
