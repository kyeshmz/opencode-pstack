import importlib.util
import os
from pathlib import Path
import re
import subprocess
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('install_opencode', ROOT / 'scripts/install-opencode.py')
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)


class OpenCodeInstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='pstack-test-')
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.config_home = self.home / 'custom config'
        self.base = self.config_home / 'opencode'
        self.environment = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(self.config_home))

    def install(self, *flags, success=True):
        result = subprocess.run(
            ['bash', str(ROOT / 'install.sh'), *flags], env=self.environment,
            cwd=self.home, capture_output=True, text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_default_only_installs_opencode_and_respects_xdg(self):
        self.install()
        self.assertTrue((self.base / 'skills/poteto-mode/SKILL.md').is_file())
        self.assertFalse((self.home / '.cursor').exists())
        self.assertFalse((self.home / '.claude').exists())
        self.assertFalse((self.home / '.config/opencode').exists())

    def test_all_skills_have_native_paths_and_matching_commands(self):
        self.install('--opencode')
        source = sorted((ROOT / 'skills').rglob('SKILL.md'))
        installed = sorted((self.base / 'skills').rglob('SKILL.md'))
        self.assertEqual(len(installed), len(source))
        for md in installed:
            text = md.read_text()
            self.assertIn(f'name: {md.parent.name}\n', text)
            self.assertIn('## OpenCode paths and output scope', text)
            self.assertIn('<target-repository>/.opencode/skills/<skill-id>/SKILL.md', text)
            self.assertIn(str(self.base / 'instructions/pstack-models.md'), text)
            self.assertNotIn('~/.cursor/', text)
            self.assertNotIn('pstack-models.mdc', text)
            self.assertNotIn('claude-opus-5-5-xhigh', text)
            self.assertNotIn('grok-4.7-xhigh-fast', text)
            command = (self.base / 'commands' / f'{md.parent.name}.md').read_text()
            self.assertIn(f'id: "{md.parent.name}"', command)
            self.assertIn('$ARGUMENTS', command)
        for md in (self.base / 'skills').rglob('*.md'):
            self.assertNotRegex(md.read_text(), r'~?/\.cursor/|subagent_type|AskQuestion|`Task`')

    def test_creation_and_maintenance_outputs_use_project_paths(self):
        self.install()
        for slug in ('create-verification-skill', 'maintain-verification-skill', 'automate-me'):
            text = (self.base / 'skills' / slug / 'SKILL.md').read_text()
            self.assertNotIn('.cursor/skills/', text)
            self.assertIn('.opencode/skills/', text)
        mode = (self.base / 'skills/automate-me/SKILL.md').read_text()
        self.assertIn(str(self.base / 'skills') + '/<handle>-mode/', mode)
        plan = (self.base / 'skills/poteto-mode/playbooks/multi-phase-plan.md').read_text()
        self.assertIn('<target-repository>/docs/plans/<task-slug>.md', plan)
        orchestration = (self.base / 'skills/poteto-mode/playbooks/orchestrate.md').read_text()
        self.assertIn('<target-repository>/.opencode/pstack/runs/<run-id>/', orchestration)
        self.assertNotIn('path in the system prompt', orchestration)

    def test_native_overlays_and_agent_modes(self):
        self.install()
        setup = (self.base / 'skills/setup-pstack/SKILL.md').read_text()
        self.assertNotIn('{{CONFIG_DIR}}', setup)
        self.assertNotIn('alwaysApply:', setup)
        self.assertIn('providerID/modelID', setup)
        for md in (self.base / 'agents').glob('*.md'):
            self.assertIn('mode: subagent\n', md.read_text())
            self.assertNotIn('is_background:', md.read_text())
        self.assertIn('does not provide Cursor', (self.base / 'skills/make-bot-ui/SKILL.md').read_text())

    def test_model_choices_custom_commands_and_unrelated_files_survive_reinstall(self):
        self.install()
        models = self.base / 'instructions/pstack-models.md'
        models.write_text('# custom\nswarm workers: custom/confirmed-model\n')
        custom = self.base / 'commands/how.md'
        custom.write_text('My custom command\n')
        unrelated = self.base / 'skills/unrelated/SKILL.md'
        unrelated.parent.mkdir()
        unrelated.write_text('My unrelated skill\n')
        stale = self.base / 'commands/removed-pstack-skill.md'
        stale.write_text(INSTALLER.COMMAND_MARKER)
        self.install()
        self.assertEqual(models.read_text(), '# custom\nswarm workers: custom/confirmed-model\n')
        self.assertEqual(custom.read_text(), 'My custom command\n')
        self.assertEqual(unrelated.read_text(), 'My unrelated skill\n')
        self.assertFalse(stale.exists())
        self.assertFalse((self.base / 'commands/unrelated.md').exists())
        self.assertEqual((self.base / 'AGENTS.md').read_text().count(INSTALLER.START), 1)

    def test_existing_instructions_and_jsonc_are_preserved(self):
        self.base.mkdir(parents=True)
        agents = self.base / 'AGENTS.md'
        agents.write_text('# My guidance\nUse tests.\n')
        config = self.base / 'opencode.jsonc'
        original = '{\n // keep comments\n "model": "custom/model",\n}\n'
        config.write_text(original)
        self.install()
        self.assertTrue(agents.read_text().startswith('# My guidance\nUse tests.\n'))
        self.assertEqual(Path(str(agents) + '.bak-pstack').read_text(), '# My guidance\nUse tests.\n')
        self.assertEqual(config.read_text(), original)

    def test_malformed_managed_block_fails_before_install(self):
        self.base.mkdir(parents=True)
        agents = self.base / 'AGENTS.md'
        original = '# User text\n' + INSTALLER.START
        agents.write_text(original)
        self.install(success=False)
        self.assertEqual(agents.read_text(), original)
        self.assertFalse((self.base / 'skills').exists())

    def test_linked_guides_and_bundled_resources_exist(self):
        self.install()
        help_md = self.base / 'skills/poteto-help/SKILL.md'
        for link in re.findall(r'\]\(([^)]+)\)', help_md.read_text()):
            if link.startswith(('http', '#')):
                continue
            self.assertTrue((help_md.parent / link.split('#')[0]).exists(), link)
        self.assertTrue((self.base / 'skills/create-verification-skill/references/feature-map-example/README.md').is_file())
        self.assertTrue((self.base / 'skills/poteto-mode/scripts/check-plan.mjs').is_file())
        self.assertIn('Set up pstack in OpenCode', (self.base / 'pstack/docs/guide/01-setup.md').read_text())

    def test_normalization_and_wrappers_support_nested_skills_and_block_descriptions(self):
        skills = self.home / 'skills'
        md = skills / 'category/nested-skill/SKILL.md'
        md.parent.mkdir(parents=True)
        md.write_text('---\nname: Display Name\ndescription: >-\n  A multiline\n  description.\ndisable-model-invocation: true\n---\nBody\n')
        INSTALLER.normalize_skills(skills)
        INSTALLER.commands(skills, self.home / 'commands')
        text = (self.home / 'commands/nested-skill.md').read_text()
        self.assertIn('description: "A multiline description."', text)
        self.assertIn('id: "nested-skill"', text)
        self.assertIn('disable-model-invocation: true', md.read_text())

    def test_home_config_fallback(self):
        self.environment.pop('XDG_CONFIG_HOME', None)
        self.base = self.home / '.config/opencode'
        self.install()
        self.assertTrue((self.base / 'skills/setup-pstack/SKILL.md').is_file())
        self.assertIn(str(self.base), (self.base / 'AGENTS.md').read_text())

    def test_upstream_drift_fails_without_publishing_partial_skills(self):
        source = self.home / 'source'
        for tree in ('skills', 'agents', 'scripts', 'opencode', 'docs'):
            shutil.copytree(ROOT / tree, source / tree, ignore=shutil.ignore_patterns('__pycache__', 'node_modules'))
        shutil.copy2(ROOT / 'INSTALL.md', source / 'INSTALL.md')
        skill = source / 'skills/reflect/SKILL.md'
        skill.write_text(skill.read_text().replace('### 1. Locate the active transcript', '### New upstream wording'))
        result = subprocess.run([
            sys.executable, str(source / 'scripts/install-opencode.py'), str(source), str(self.base),
        ], capture_output=True, text=True, env=self.environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('rule(s) mismatched', result.stdout)
        self.assertFalse(self.base.exists())

    def test_install_leaves_upstream_sources_untouched(self):
        paths = [ROOT / 'skills/setup-pstack/SKILL.md', ROOT / 'skills/poteto-mode/scripts/worktree-audit.sh', ROOT / 'agents/poteto-agent.md']
        before = [path.read_bytes() for path in paths]
        self.install()
        self.assertEqual(before, [path.read_bytes() for path in paths])

    def test_bootstrap_installs_from_a_disposable_checkout(self):
        repository = self.home / 'bootstrap-source'
        repository.mkdir()
        (repository / 'install.sh').write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\n'
            'printf "%s\\n" "$*" > "$HOME/bootstrap-arguments"\n'
        )
        subprocess.run(['git', 'init', '-b', 'main', str(repository)], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(repository), 'add', 'install.sh'], check=True, capture_output=True)
        subprocess.run([
            'git', '-C', str(repository), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
            'commit', '-m', 'Test bootstrap fixture',
        ], check=True, capture_output=True)
        scratch = self.home / 'scratch'
        scratch.mkdir()
        environment = dict(self.environment, PSTACK_REPOSITORY=str(repository), TMPDIR=str(scratch))
        result = subprocess.run(['bash', str(ROOT / 'bootstrap.sh'), '--opencode'], env=environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.home / 'bootstrap-arguments').read_text(), '--opencode\n')
        self.assertEqual(list(scratch.iterdir()), [])

    def test_changed_pack_files_are_backed_up_before_replacement(self):
        md = self.base / 'skills/poteto-mode/SKILL.md'
        md.parent.mkdir(parents=True)
        original = 'Existing customized pack skill\n'
        md.write_text(original)
        self.install()
        backups = list((self.config_home / 'opencode-pstack-backups/opencode').glob('*/skills/poteto-mode/SKILL.md'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), original)
        self.assertIn('## OpenCode paths and output scope', md.read_text())


if __name__ == '__main__':
    unittest.main()
