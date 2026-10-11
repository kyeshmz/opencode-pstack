# Set up pstack in OpenCode

## Install

From the pstack source checkout, run `./install.sh --opencode`.
The default `./install.sh` also installs OpenCode only. Skills and agents are
installed globally, with a slash-command wrapper for each skill. Existing
custom commands and per-role model choices are preserved.

The installation directory is `{{CONFIG_DIR}}`. Project-specific skills are
created separately in the target repository's `.opencode/skills/` directory.

## Pick your models

Start a new OpenCode session and run `/setup-pstack`. Setup discovers available
model IDs and variants, asks for your preferences, and writes
`{{CONFIG_DIR}}/instructions/pstack-models.md`. Fresh installs inherit the
parent model rather than guessing an available provider or model.

For panel roles, one comma-separated entry means one reviewer. `auto` and
`inherit-parent` both omit the subagent's model argument.

## Add project verification

If the target project lacks a usable verification harness, setup offers
`/create-verification-skill`. On approval, it creates
`<target-repository>/.opencode/skills/verify-<app>/SKILL.md` plus a feature map
and proves the launch, drive, evidence, and cleanup steps.

## Run a task

```text
/poteto-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Start each new task with `/poteto-mode` or mention `@poteto-mode`. OpenCode
does not provide Cursor's Option+Enter Custom Mode, cloud VMs, or `/loop`.
Parallel writing agents need isolated worktrees; background work still runs
on this machine and must not be assumed to continue with the laptop closed.

Next: [Route work through poteto-mode](./02-poteto-mode.md).
