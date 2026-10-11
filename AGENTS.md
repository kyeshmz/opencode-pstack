# Working on the OpenCode pstack port

- `skills/`, `agents/`, `docs/`, and `automations/` mirror the Cursor upstream.
  Keep portable upstream content there. Put OpenCode-specific replacements in
  `opencode/skills/<skill-id>/SKILL.md` and conversion rules in
  `scripts/opencode-transform.py`; upstream sync preserves these overlays.
- New shared pstack skills belong in `skills/<skill-id>/SKILL.md`, with their
  scripts, references, and assets beside the entry file. Do not author pack
  skills in a global installation or a generated `.opencode/skills/` directory.
- In a consuming project, generated verification and personal mode skills
  belong in `<target-repository>/.opencode/skills/<skill-id>/SKILL.md`. Only
  create global skills when the user explicitly requests that scope.
- The OpenCode installer uses `${XDG_CONFIG_HOME:-$HOME/.config}/opencode`.
  Model choices live in `instructions/pstack-models.md` under that directory;
  no OpenCode workflow should create or depend on `~/.cursor/`.
- Resolve bundled skill resources from the loaded skill's base directory.
  Resolve generated project files and command working directories from the
  target repository or assigned worktree, not from the installed skill path.
- Validate installer changes with `python3 -m unittest discover -s scripts/tests`
  and `bash -n install.sh`. Tests must use a temporary HOME/config directory;
  do not install into the user's live configuration as part of a test.
