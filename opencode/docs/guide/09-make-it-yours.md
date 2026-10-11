# Make pstack yours in OpenCode

## Capture recurring preferences

Run `/automate-me` to mine relevant OpenCode sessions for repeated preferences.
It asks which patterns to retain, then creates or updates a personal mode skill.
By default it writes into the target project's
`.opencode/skills/<handle>-mode/SKILL.md`. An established category may instead
use `.opencode/skills/<handle>/<handle>-mode/SKILL.md`.

Only when you request a global skill should it write into
`{{CONFIG_DIR}}/skills/<handle>-mode/SKILL.md`. Existing OpenCode skills stay
in their original location. Do not search other projects' sessions without
authorization.

## Create or edit a skill

Use `skill-creator` if available, or author a directory-based `SKILL.md` with
`name` and `description` YAML frontmatter. The unique directory name is the
OpenCode skill ID. Keep scripts, references, templates, and assets beside it;
agents resolve them from the loaded skill's base directory.

Generated project files belong in the target repository, not the globally
installed pack. Shared contributions to pstack itself belong in the source
checkout's `skills/<skill-id>/` tree. OpenCode-specific replacements belong
in `opencode/skills/<skill-id>/SKILL.md` so upstream sync preserves them.

Test the skill against a realistic task before relying on it. A new skill can
be mentioned as `@skill-id` or loaded through the `skill` tool. The installer
generates slash wrappers for pack skills; authoring a project skill alone does
not create a new slash wrapper.
