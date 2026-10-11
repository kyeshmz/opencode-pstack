import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
VERIFY_PATH = ROOT / "scripts/verify-opencode-port.py"
SPEC = importlib.util.spec_from_file_location("verify_opencode_port", VERIFY_PATH)
assert SPEC and SPEC.loader
verify = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verify
SPEC.loader.exec_module(verify)


def fixture_git_environment(root, *, global_config=None):
    root = Path(root)
    home = root / "git-fixture-home"
    xdg = root / "git-fixture-xdg"
    template = root / "empty-git-template"
    temporary = root / "git-fixture-tmp"
    for directory in (home, xdg, template, temporary):
        directory.mkdir(parents=True, exist_ok=True)
    paths = [str(Path(sys.executable).resolve().parent), "/usr/local/bin", "/opt/homebrew/bin", "/usr/bin", "/bin"]
    return {
        "PATH": os.pathsep.join(dict.fromkeys(paths)),
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(xdg),
        "TMPDIR": str(temporary),
        "LANG": "C",
        "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": str(global_config) if global_config is not None else os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_TEMPLATE_DIR": str(template),
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
    }


def run(command, *, cwd=None, env):
    if env is None:
        raise AssertionError("fixture commands require an explicit sanitized environment")
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"command failed: {command!r}\n{result.stdout}\n{result.stderr}")
    return result


def git(cwd, *args, env):
    return run(["git", "-c", f"core.hooksPath={os.devnull}", *args], cwd=cwd, env=env)


def copy_policy_inputs(destination):
    if (ROOT / "oc-port-agent.json").is_file():
        shutil.copy2(ROOT / "oc-port-agent.json", destination / "oc-port-agent.json")
    shutil.copytree(ROOT / "opencode/porting", destination / "opencode/porting")
    (destination / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "scripts/sync-upstream.sh", destination / "scripts/sync-upstream.sh")
    if (ROOT / ".oc-port/.gitignore").is_file():
        (destination / ".oc-port").mkdir()
        shutil.copy2(ROOT / ".oc-port/.gitignore", destination / ".oc-port/.gitignore")


class PortPolicyTests(unittest.TestCase):
    def test_policy_is_one_narrow_combined_selection_with_local_schemas(self):
        local, hosted = verify.validate_scope(ROOT)
        if local is not None:
            self.assertEqual(len(local["selections"]), 1)
            self.assertEqual(local["selections"][0]["targetPaths"], verify.TARGET_PATHS)
        self.assertNotIn("opencode", hosted)
        if local is not None:
            self.assertEqual(local["selections"], hosted["selections"])

    def test_policy_scope_or_checkpoint_drift_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-policy-drift-") as temporary:
            fixture = Path(temporary)
            copy_policy_inputs(fixture)
            hosted_path = fixture / "opencode/porting/policy.json"
            hosted = json.loads(hosted_path.read_text(encoding="utf-8"))
            hosted["selections"][0]["targetPaths"].append("skills/**")
            hosted_path.write_text(json.dumps(hosted), encoding="utf-8")
            with self.assertRaisesRegex(verify.VerificationError, "target edit allowlist changed"):
                verify.validate_scope(fixture)

        with tempfile.TemporaryDirectory(prefix="oc-port-instructions-drift-") as temporary:
            fixture = Path(temporary)
            copy_policy_inputs(fixture)
            hosted_path = fixture / "opencode/porting/policy.json"
            hosted = json.loads(hosted_path.read_text(encoding="utf-8"))
            hosted["selections"][0]["instructions"]["nonGoals"][0] += " Changed intent."
            hosted_path.write_text(json.dumps(hosted), encoding="utf-8")
            with self.assertRaisesRegex(verify.VerificationError, "reviewed selection instructions"):
                verify.validate_scope(fixture)

        with tempfile.TemporaryDirectory(prefix="oc-port-checkpoint-drift-") as temporary:
            fixture = Path(temporary)
            (fixture / ".oc-port").mkdir()
            state = {
                "version": 1,
                "upstream": verify.UPSTREAM,
                "policyHash": verify.TRACKING_POLICY_HASH,
                "lastSyncedCommit": "f" * 39,
            }
            (fixture / ".oc-port/state.json").write_text(json.dumps(state), encoding="utf-8")
            with self.assertRaisesRegex(verify.VerificationError, "commit is malformed"):
                verify.validate_checkpoint(fixture)

    def test_plan_pins_are_required_and_selected_changes_must_match_raw_mirror(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-missing-packet-") as temporary:
            with self.assertRaisesRegex(verify.VerificationError, "needs a CLI packet"):
                verify.plan_metadata(Path(temporary), {}, required=True)

        with tempfile.TemporaryDirectory(prefix="oc-port-malformed-pin-") as temporary:
            fixture = Path(temporary)
            invalid = {
                "OC_PORT_UPSTREAM_COMMIT": "not-a-commit",
                "OC_PORT_TARGET_COMMIT": "b" * 40,
                "OC_PORT_HAS_SELECTIONS": "true",
            }
            with self.assertRaisesRegex(verify.VerificationError, "complete hexadecimal commits"):
                verify.plan_metadata(fixture, invalid, required=True)

            (fixture / ".upstream-sha").write_text(verify.BASELINE + "\n", encoding="ascii")
            stale = {
                "OC_PORT_UPSTREAM_COMMIT": "a" * 40,
                "OC_PORT_TARGET_COMMIT": "b" * 40,
                "OC_PORT_HAS_SELECTIONS": "true",
            }
            with self.assertRaisesRegex(verify.VerificationError, "mirror first"):
                verify.plan_metadata(fixture, stale, required=True)

            unselected_future = {
                "OC_PORT_UPSTREAM_COMMIT": "f" * 40,
                "OC_PORT_TARGET_COMMIT": "b" * 40,
                "OC_PORT_HAS_SELECTIONS": "false",
            }
            self.assertEqual(
                verify.plan_metadata(fixture, unselected_future, required=True),
                {
                    "upstreamCommit": "f" * 40,
                    "fromCommit": None,
                    "targetCommit": "b" * 40,
                    "hasSelections": False,
                },
            )

    def test_cli_packet_supplies_plan_source_and_selection_state(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-plan-packet-") as temporary:
            fixture = Path(temporary)
            packet_dir = fixture / ".oc-port/context"
            packet_dir.mkdir(parents=True)
            commit = "c" * 40
            (fixture / ".upstream-sha").write_text(commit + "\n", encoding="ascii")
            packet = {
                "upstream": verify.UPSTREAM,
                "plan": {"from": commit, "to": commit, "selections": [{"id": verify.SELECTION_ID}]},
            }
            (packet_dir / "packet.json").write_text(json.dumps(packet), encoding="utf-8")
            result = verify.plan_metadata(fixture, {}, required=True)
            self.assertEqual(result, {
                "upstreamCommit": commit,
                "fromCommit": commit,
                "targetCommit": None,
                "hasSelections": True,
            })
            conflicting_worker = {
                "OC_PORT_UPSTREAM_COMMIT": "d" * 40,
                "OC_PORT_TARGET_COMMIT": "b" * 40,
                "OC_PORT_HAS_SELECTIONS": "true",
            }
            with self.assertRaisesRegex(verify.VerificationError, "packet and trusted Worker plan pins disagree"):
                verify.plan_metadata(fixture, conflicting_worker, required=True)

    def test_malformed_cli_packet_is_rejected_without_falling_back_to_worker_values(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-malformed-packet-") as temporary:
            fixture = Path(temporary)
            packet_dir = fixture / ".oc-port/context"
            packet_dir.mkdir(parents=True)
            (packet_dir / "packet.json").write_text(json.dumps({
                "upstream": verify.UPSTREAM,
                "plan": {"from": verify.BASELINE, "to": "bad", "selections": []},
            }), encoding="utf-8")
            trusted_worker_values = {
                "OC_PORT_UPSTREAM_COMMIT": verify.BASELINE,
                "OC_PORT_TARGET_COMMIT": "b" * 40,
                "OC_PORT_HAS_SELECTIONS": "false",
            }
            with self.assertRaisesRegex(verify.VerificationError, "packet plan pin"):
                verify.plan_metadata(fixture, trusted_worker_values, required=True)

    def test_runtime_checkpoint_accepts_verified_progress_and_rejects_inconsistent_state(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-advanced-checkpoint-") as temporary:
            fixture = Path(temporary)
            (fixture / ".oc-port").mkdir()
            advanced = "d" * 40
            state = {
                "version": 1,
                "upstream": verify.UPSTREAM,
                "policyHash": verify.TRACKING_POLICY_HASH,
                "lastSyncedCommit": advanced,
            }
            state_path = fixture / ".oc-port/state.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertEqual(
                verify.validate_checkpoint(fixture, {"fromCommit": advanced}),
                state,
            )
            with self.assertRaisesRegex(verify.VerificationError, "starting commit"):
                verify.validate_checkpoint(fixture, {"fromCommit": "c" * 40})

            for field, value, error in (
                ("policyHash", "0" * 64, "policy hash"),
                ("upstream", {"repository": "https://example.invalid/source.git", "ref": "main"}, "configured source"),
                ("lastSyncedCommit", "not-a-commit", "commit is malformed"),
            ):
                changed = {**state, field: value}
                state_path.write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(field=field), self.assertRaisesRegex(verify.VerificationError, error):
                    verify.validate_checkpoint(fixture)

    def test_sequential_checkpoint_progression_requires_each_selected_source_pin(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-sequential-checkpoints-") as temporary:
            fixture = Path(temporary)
            state_dir = fixture / ".oc-port"
            state_dir.mkdir()
            state_path = state_dir / "state.json"
            packet_path = state_dir / "context/packet.json"
            packet_path.parent.mkdir()
            state = {
                "version": 1,
                "upstream": verify.UPSTREAM,
                "policyHash": verify.TRACKING_POLICY_HASH,
                "lastSyncedCommit": verify.BASELINE,
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")

            first_target = "d" * 40
            (fixture / ".upstream-sha").write_text(first_target + "\n", encoding="ascii")
            first_packet = {
                "upstream": verify.UPSTREAM,
                "plan": {"from": verify.BASELINE, "to": first_target, "selections": [{"id": verify.SELECTION_ID}]},
            }
            packet_path.write_text(json.dumps(first_packet), encoding="utf-8")
            first = verify.plan_metadata(fixture, {}, required=True)
            verify.validate_checkpoint(fixture, first)

            second_source = "e" * 40
            state["lastSyncedCommit"] = first_target
            state_path.write_text(json.dumps(state), encoding="utf-8")
            (fixture / ".upstream-sha").write_text(second_source + "\n", encoding="ascii")
            second_packet = {
                "upstream": verify.UPSTREAM,
                "plan": {"from": first_target, "to": second_source, "selections": [{"id": verify.SELECTION_ID}]},
            }
            packet_path.write_text(json.dumps(second_packet), encoding="utf-8")
            second = verify.plan_metadata(fixture, {}, required=True)
            verify.validate_checkpoint(fixture, second)

            second_packet["plan"]["from"] = verify.BASELINE
            packet_path.write_text(json.dumps(second_packet), encoding="utf-8")
            stale = verify.plan_metadata(fixture, {}, required=True)
            with self.assertRaisesRegex(verify.VerificationError, "starting commit"):
                verify.validate_checkpoint(fixture, stale)

            (fixture / ".upstream-sha").write_text(first_target + "\n", encoding="ascii")
            with self.assertRaisesRegex(verify.VerificationError, "mirror first"):
                verify.plan_metadata(fixture, {
                    "OC_PORT_UPSTREAM_COMMIT": second_source,
                    "OC_PORT_TARGET_COMMIT": "b" * 40,
                    "OC_PORT_HAS_SELECTIONS": "true",
                }, required=True)

    def test_hosted_verifier_uses_trusted_pins_without_internal_cli_state(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-hosted-verifier-") as temporary:
            fixture = Path(temporary) / "repo"

            def ignore(_directory, names):
                return {name for name in names if name in {".git", ".plans", ".oc-port", "oc-port-agent.json"}}

            shutil.copytree(ROOT, fixture, ignore=ignore)
            worker_env = {
                "OC_PORT_UPSTREAM_COMMIT": verify.BASELINE,
                "OC_PORT_TARGET_COMMIT": "b" * 40,
                "OC_PORT_HAS_SELECTIONS": "true",
            }
            result = verify.verify(fixture, require_plan=True, environ=worker_env)
            self.assertIn("plan " + verify.BASELINE, result)
            self.assertIn("selected=True", result)

    def test_mutated_raw_source_is_detected_by_hash_manifest(self):
        before = {
            "skills/source.md": ("before", 0o100644),
            "docs/guide.md": ("same", 0o100644),
            "README.md": ("user-owned overlay", 0o100644),
        }
        after = {
            "skills/source.md": ("before", 0o100644),
            "docs/guide.md": ("same", 0o100644),
            "README.md": ("overwritten overlay", 0o100644),
        }
        with self.assertRaisesRegex(verify.VerificationError, "installer changed protected source/overlay hashes"):
            verify.assert_source_unchanged(before, after)

    def test_bad_transform_fails_on_real_installer_strict_hit_assertion(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-bad-transform-") as temporary:
            temporary_root = Path(temporary)
            fixture = temporary_root / "repo"
            shutil.copytree(
                ROOT,
                fixture,
                ignore=lambda _directory, names: {
                    name for name in names if name in {".git", ".plans", ".oc-port", "node_modules", ".wrangler", "__pycache__"}
                },
            )
            source = fixture / "skills/no-comments/SKILL.md"
            text = source.read_text(encoding="utf-8")
            self.assertIn("Spawn `Task` with", text)
            source.write_text(text.replace("Spawn `Task` with", "Spawn the Task with", 1), encoding="utf-8")
            home = temporary_root / "home"
            home.mkdir()
            existing = home / "xdg config/opencode/skills/no-comments/SKILL.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("Existing installed skill must survive a failed conversion.\n", encoding="utf-8")
            with self.assertRaisesRegex(verify.VerificationError, "install.sh --opencode exited"):
                verify.run_install(fixture, home, temporary_root)
            self.assertEqual(existing.read_text(encoding="utf-8"), "Existing installed skill must survive a failed conversion.\n")
            self.assertFalse((home / "xdg config/opencode/skills/poteto-mode").exists())

    def test_isolated_generation_preserves_user_state_and_is_idempotent(self):
        before_sources = verify.source_manifest(ROOT)
        with tempfile.TemporaryDirectory(prefix="oc-port-generation-") as temporary:
            temporary_root = Path(temporary)
            home = temporary_root / "home"
            home.mkdir()
            sentinels = verify.prepare_isolated_home(home)
            first = verify.run_install(ROOT, home, temporary_root)
            first_tree = verify.tree_manifest(sentinels["config_dir"])
            counts = verify.verify_installed_output(ROOT, home, sentinels)
            second = verify.run_install(ROOT, home, temporary_root)
            second_tree = verify.tree_manifest(sentinels["config_dir"])
            self.assertEqual(first_tree, second_tree)
            self.assertIn("all ", first.stdout)
            self.assertIn("all ", second.stdout)
            self.assertGreater(counts[0], 0)
            self.assertGreater(counts[1], 0)
            self.assertGreater(counts[2], 0)
        verify.assert_source_unchanged(before_sources, verify.source_manifest(ROOT))

    def test_fresh_install_uses_nondefault_xdg_and_inherit_parent_seed(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-fresh-xdg-") as temporary:
            temporary_root = Path(temporary)
            home = temporary_root / "home"
            home.mkdir()
            verify.run_install(ROOT, home, temporary_root)
            config = home / "xdg config/opencode"
            model_file = config / "instructions/pstack-models.md"
            self.assertEqual(model_file.read_bytes(), (ROOT / "opencode/pstack-models.md").read_bytes())
            self.assertIn("inherit-parent", model_file.read_text(encoding="utf-8"))
            self.assertFalse((home / ".config").exists())
            self.assertFalse((home / ".cursor").exists())
            self.assertFalse((config / "opencode.json").exists())
            agents = (config / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(agents.count("<!-- pstack:opencode:start -->"), 1)
            self.assertEqual(agents.count("<!-- pstack:opencode:end -->"), 1)

    @unittest.skipUnless(shutil.which("git") and shutil.which("rsync"), "requires Git and real rsync for the local sync fixture")
    def test_sync_uses_real_rsync_and_preserves_policy_checkpoint_with_ci_identity(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-sync-rsync-") as temporary:
            temporary_root = Path(temporary)
            bare = temporary_root / "upstream.git"
            source = temporary_root / "source"
            target = temporary_root / "target"
            global_config = temporary_root / "gitconfig"
            global_config.write_text("[user]\n\tname = Global Fixture\n\temail = global@example.invalid\n", encoding="utf-8")
            fixture_env = fixture_git_environment(temporary_root, global_config=global_config)
            git(temporary_root, "init", "--bare", "--initial-branch=main", str(bare), env=fixture_env)
            git(temporary_root, "init", "--initial-branch=main", str(source), env=fixture_env)
            (source / "pstack").mkdir()
            (source / "pstack/README.md").write_text("upstream README revision\n", encoding="utf-8")
            (source / "pstack/skills").mkdir()
            (source / "pstack/skills/raw.md").write_text("upstream raw content\n", encoding="utf-8")
            git(source, "add", "pstack", env=fixture_env)
            git(source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "fixture source", env=fixture_env)
            git(source, "remote", "add", "origin", str(bare), env=fixture_env)
            git(source, "push", "-u", "origin", "main", env=fixture_env)

            git(temporary_root, "init", "--initial-branch=main", str(target), env=fixture_env)
            (target / "scripts").mkdir()
            shutil.copy2(ROOT / "scripts/sync-upstream.sh", target / "scripts/sync-upstream.sh")
            (target / "README.md").write_text("old mirror README\n", encoding="utf-8")
            (target / "agents").mkdir()
            (target / "agents/opencode-port-agent.md").write_text("overlay agent sentinel\n", encoding="utf-8")
            (target / "opencode").mkdir()
            (target / "opencode/pstack-models.md").write_text("overlay model sentinel\n", encoding="utf-8")
            (target / "oc-port-agent.json").write_text('{"policy":"keep"}\n', encoding="utf-8")
            (target / ".upstream-sha").write_text("old-mirror-sha\n", encoding="ascii")
            (target / ".oc-port/reports").mkdir(parents=True)
            (target / ".oc-port/.gitignore").write_text("/cache/\n", encoding="utf-8")
            (target / ".oc-port/state.json").write_text('{"checkpoint":"keep"}\n', encoding="utf-8")
            (target / ".oc-port/reports/retained.json").write_text('{"report":"keep"}\n', encoding="utf-8")
            git(target, "add", "-A", env=fixture_env)
            git(target, "-c", "user.name=Target", "-c", "user.email=target@example.invalid", "commit", "-m", "fixture target", env=fixture_env)

            global_before = global_config.read_bytes()
            sync_env = {
                **fixture_env,
                "GITHUB_ACTIONS": "true",
                "PSTACK_SYNC_TEST_FIXTURE": "1",
                "PSTACK_SYNC_FIXTURE_REPO": str(bare),
            }
            sync_result = run(["bash", "scripts/sync-upstream.sh"], cwd=target, env=sync_env)
            self.assertIn("Committed sync", sync_result.stdout)
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), "old mirror README\n")
            self.assertEqual((target / "oc-port-agent.json").read_text(encoding="utf-8"), '{"policy":"keep"}\n')
            self.assertEqual((target / ".oc-port/state.json").read_text(encoding="utf-8"), '{"checkpoint":"keep"}\n')
            self.assertEqual((target / ".oc-port/.gitignore").read_text(encoding="utf-8"), "/cache/\n")
            self.assertEqual((target / ".oc-port/reports/retained.json").read_text(encoding="utf-8"), '{"report":"keep"}\n')
            self.assertEqual((target / "agents/opencode-port-agent.md").read_text(encoding="utf-8"), "overlay agent sentinel\n")
            self.assertEqual((target / "opencode/pstack-models.md").read_text(encoding="utf-8"), "overlay model sentinel\n")
            author = git(target, "log", "-1", "--format=%an <%ae>", env=sync_env).stdout.strip()
            self.assertEqual(author, "github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>")
            self.assertEqual(global_config.read_bytes(), global_before)

    @unittest.skipUnless(shutil.which("git"), "requires Git for the local sync fixture")
    def test_sync_fixture_override_requires_explicit_local_test_mode(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-sync-override-") as temporary:
            temporary_root = Path(temporary)
            target = temporary_root / "target"
            fixture_env = fixture_git_environment(temporary_root)
            git(temporary_root, "init", "--initial-branch=main", str(target), env=fixture_env)
            (target / "scripts").mkdir()
            shutil.copy2(ROOT / "scripts/sync-upstream.sh", target / "scripts/sync-upstream.sh")
            result = subprocess.run(
                ["bash", "scripts/sync-upstream.sh"],
                cwd=target,
                env={**fixture_env, "PSTACK_SYNC_FIXTURE_REPO": str(temporary_root / "not-used.git")},
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("require PSTACK_SYNC_TEST_FIXTURE=1", result.stderr)

    def test_git_fixture_ignores_controlled_caller_template_and_config(self):
        with tempfile.TemporaryDirectory(prefix="oc-port-git-isolation-") as temporary:
            root = Path(temporary)
            caller_home = root / "caller-home"
            caller_home.mkdir()
            caller_template = caller_home / "template"
            (caller_template / "hooks").mkdir(parents=True)
            marker_hook = caller_template / "hooks/pre-commit"
            marker_hook.write_text("#!/bin/sh\ntouch inherited-template-hook-ran\n", encoding="utf-8")
            caller_config = caller_home / ".gitconfig"
            caller_config.write_text(
                f"[user]\n\tname = Caller Identity\n\temail = caller@example.invalid\n[init]\n\ttemplateDir = {caller_template}\n",
                encoding="utf-8",
            )
            target = root / "target"
            with patch.dict(os.environ, {
                "HOME": str(caller_home),
                "XDG_CONFIG_HOME": str(caller_home / "xdg"),
                "GIT_CONFIG_GLOBAL": str(caller_config),
                "GIT_TEMPLATE_DIR": str(caller_template),
            }):
                isolated_env = fixture_git_environment(root)
            git(root, "init", "--initial-branch=main", str(target), env=isolated_env)

            self.assertEqual(isolated_env["GIT_CONFIG_GLOBAL"], os.devnull)
            self.assertNotEqual(isolated_env["HOME"], str(caller_home))
            self.assertNotEqual(isolated_env["GIT_TEMPLATE_DIR"], str(caller_template))
            self.assertFalse((target / ".git/hooks/pre-commit").exists())
            identity = subprocess.run(
                ["git", "config", "--local", "--get", "user.name"],
                cwd=target,
                env=isolated_env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(identity.returncode, 0)


if __name__ == "__main__":
    unittest.main()
