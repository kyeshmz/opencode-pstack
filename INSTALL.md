# pstack for OpenCode

This repository mirrors [Cursor's upstream pstack](https://github.com/cursor/plugins/tree/main/pstack)
and converts its skills and agents to native OpenCode instructions during installation.
Upstream files stay intact; OpenCode-specific overlays survive upstream sync.

## Install

One line, with no permanent checkout required:

```bash
curl -fsSL https://raw.githubusercontent.com/kyeshmz/opencode-pstack/main/bootstrap.sh | bash
```

Run the same line to update. It clones a temporary checkout, runs the OpenCode
installer, and removes only that temporary checkout afterward. It installs on
the machine where the command runs, so paths are generated for that machine.
You can [review the bootstrap script](https://github.com/kyeshmz/opencode-pstack/blob/main/bootstrap.sh)
before running it. Git, Python 3, and Bash are required.

Or, from an existing checkout:

```bash
./install.sh             # OpenCode only (default)
./install.sh --opencode  # same as the default
```

Start a new OpenCode session, run `/setup-pstack` to choose models, then
`/poteto-mode` for your first task. Fresh installs inherit the parent model.
Reinstallation preserves existing model choices and unmarked custom commands.
Before overwriting pack files, it saves their previous versions in a timestamped
`opencode-pstack-backups/` directory beside the global `opencode/` directory.
Unrelated skills, credentials, service settings, and session databases are not copied.

Python 3 and Bash are required. Installation converts and validates a temporary
copy first, so an upstream conversion mismatch fails before replacing skills.

### Where files go

The global base is `${XDG_CONFIG_HOME:-$HOME/.config}/opencode`:

| Content | Location under that base |
| --- | --- |
| Pack skills and bundled resources | `skills/<skill-id>/SKILL.md` |
| Subagents | `agents/<agent-id>.md` |
| Generated slash-command wrappers | `commands/<skill-id>.md` |
| User-owned per-role model choices | `instructions/pstack-models.md` |
| Managed persistent path guidance | `AGENTS.md` |
| Linked guides and installation instructions | `pstack/docs/`, `pstack/README.md` |

OpenCode V2 uses the directory name as the skill ID. The installer normalizes
frontmatter names for portability; V2 does not require that name to match the ID.
`disable-model-invocation: true` remains supported for manual-only skills.
Slash commands are separate from skills, so the installer creates wrappers that
load the exact skill ID and forward `$ARGUMENTS`. It also handles folded YAML
descriptions and nested skill directories.

OpenCode V2 currently does not load the config's `instructions` array. The
installer instead adds a marked block to global `AGENTS.md` directing pstack
workflows to read the model configuration. It preserves unrelated instructions
and backs up the file before changing it. It does not edit `opencode.json(c)`.

An OpenCode install does **not** create or depend on `~/.cursor/`.

## Where newly created files go

Every installed skill includes path and output-scope guidance:

- **Project skills:** `<target-repository>/.opencode/skills/<skill-id>/SKILL.md`.
  Verification skills, their feature maps, and personal mode skills default here.
- **Global skills:** `<global-base>/skills/<skill-id>/SKILL.md`, only when requested.
- **Shared pstack contributions:** `skills/<skill-id>/SKILL.md` in this source checkout.
- **OpenCode-specific replacements:** `opencode/skills/<skill-id>/SKILL.md` here.
- **Bundled resources:** relative to the loaded skill's base directory, not the
  shell's current directory. Run project commands in the target repo/worktree.
- **Scratch files:** the host's temporary directory, in a unique per-run location.

Existing OpenCode skills retain their location when updated. Global model
configuration is not a project output and is changed only on request.

## Platform differences

The conversion covers Cursor tool names/parameters, skill paths, session lookup,
model configuration paths, and workflow references to unavailable built-ins.
`setup-pstack` uses confirmed OpenCode model IDs and variants. `make-bot-ui`
requires a user-configured webhook backend rather than inventing Cursor routines
or secret-request tools.

OpenCode does not provide Cursor Custom Modes, `/loop`, cloud-agent VMs, or the
`cursor-team-kit` plugin. Use project verification skills, isolated worktrees,
and host-supported background work instead. Background work is local; do not
assume it continues when the laptop closes. The copied guides identify upstream
platform differences; installed skills are authoritative for OpenCode behavior.

The `automations/benny/` pack is an upstream Cursor automation integration, not
an OpenCode scheduler. The installer does not register or enable those automations.

### Other hosts (explicit compatibility installs)

```bash
./install.sh --claude  # ~/.claude/skills and ~/.claude/agents
./install.sh --cursor  # ~/.cursor/skills and ~/.cursor/agents
./install.sh --all     # all three targets
```

These compatibility copies retain upstream tool names and platform dependencies;
only the OpenCode copies receive the OpenCode conversion.

## Upstream sync and validation

`.github/workflows/sync-upstream.yml` runs every six hours and on manual dispatch.
`scripts/sync-upstream.sh` copies upstream pstack into this checkout and commits
changes. The last upstream revision is in `.upstream-sha`.

The sync preserves `AGENTS.md`, `README.md`, `INSTALL.md`, `install.sh`, `bootstrap.sh`, `opencode/`, `scripts/`,
`.github/`, `.claude-plugin/`, and `.upstream-sha`. Conversion rules assert their
expected match counts so upstream rewordings fail visibly instead of leaving
partially converted instructions.

Run the sandboxed installation tests with:

```bash
python3 -m unittest discover -s scripts/tests
bash -n install.sh
```

Tests use temporary home/config directories and do not alter your live setup.

## Structured Cursor pstack port policy

`oc-port-agent.json` and `opencode/porting/` are preserved OpenCode overlays
for selectively tracking the Cursor `plugins` repository's `pstack/` source.
The policy gives one selection the pstack skill, agent, guide, and README
Markdown context plus the two text scripts used by existing transformations.
Its edit allowlist covers reviewed OpenCode-specific installer, conversion,
skill, and guide overlays. It keeps upstream workflows, rationale, principles,
and acceptance intent intact; only verified OpenCode V2 host mechanics may differ.

The local CLI policy and `.oc-port/state.json` checkpoint are separate from
`.upstream-sha`, which remains raw-mirror provenance and does not prove
semantic parity. `opencode/porting/policy.json` is the hosted policy form and
does not contain executable or model settings. `registration.template.json`
is review material only. The recorded GitHub App installation ID is not proof
that access to this repository is enabled, and creating these files does not
activate a hosted registration. The hosted service also has no initial
`--full` adoption mode. Do not claim unattended synchronization is active.

Run `python3 scripts/verify-opencode-port.py` for a manual isolated install
check. Pinned plan verification uses
`python3 scripts/verify-opencode-port.py --require-plan`; it blocks if selected
source changes are newer than the mirrored `.upstream-sha`. Both modes create
a fresh temporary `HOME` and `XDG_CONFIG_HOME` and do not read global sessions
or credentials.

## Overlay files (not overwritten by sync)

- `.claude-plugin/` — Claude Code plugin + marketplace manifests
- `opencode/` — OpenCode overlays and user-owned model role defaults
- `scripts/sync-upstream.sh` — sync script (holds the overlay rsync excludes)
- `scripts/opencode-transform.py` — Cursor-to-OpenCode rewrite rules, run by
  `install.sh --opencode` on the installed copies; each rule asserts its hit
  count so upstream rewordings fail loudly
- `agents/opencode-port-agent.md` — the agent that owns this port; has its own
  rsync exclude because `agents/` is otherwise upstream-owned
- `.github/workflows/sync-upstream.yml` — auto-sync workflow
- `oc-port-agent.json`, `opencode/porting/`, and `.oc-port/` — structured port
  policy, protected schemas, documentation, and separate checkpoint. Local
  cache/context/result artifacts are ignored; state and reports are retained.
- `scripts/verify-opencode-port.py` and `scripts/tests/` — isolated installer
  and policy/sync regression checks
- `install.sh`, `INSTALL.md`, `.upstream-sha`

The six-hour mirror is still the only scheduled writer. `scripts/sync-upstream.sh`
excludes `oc-port-agent.json` and `.oc-port/` from rsync deletion. It uses a
GitHub Actions bot identity only on the individual CI commit invocation; no
global Git configuration is changed.

The upstream-owned `skills/`, `agents/` (except the port agent), `docs/`,
`automations/`, `assets/`, `.cursor-plugin/`, `LICENSE`, and `.gitignore` remain
pristine. `README.md`, `AGENTS.md`, and `bootstrap.sh` are existing
OpenCode-specific overlays preserved by the current sync script.
