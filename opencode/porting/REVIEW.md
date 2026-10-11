# Phase 2 independent review

Reviewed, repair-rechecked, and concurrent-main-reconciled on 2026-10-10 by GPT-6.1 Sol. **Disposition: no blocking finding in the reconciliation onto `origin/main` at `30a3cbd1cbf83159e56d83790fc43b4493eb5fc6`; approved for the planner to publish a draft configuration PR within the current measured scope.** Prior R1–R4 closures remain intact. This approval does not authorize merge, model inference, App activation, or hosted deployment, and does not certify full pstack semantic parity.

Implementation was read-only. No commit, remote write, App action, deployment, Docker run, model inference, global install, checkpoint update, or credential inspection was performed. Reproductions used disposable copies and controlled environments; launcher privilege calls were mocked, not executed.

## Current-base concurrent-main reconciliation review

This section supersedes earlier-base counts, installer assumptions, policy hashes, and scope statements below. Current `AGENTS.md` and incoming user changes are authoritative. Implementation/state/incoming files remained read-only during this review; only this report and the permitted plan log were updated. No broader App/core/provider audit or live permission request was performed.

### Preservation and current scope

- Offline byte/mode audit confirms **180 incoming `origin/main` files unchanged** outside the three deliberately modified port overlays (`INSTALL.md`, `agents/opencode-port-agent.md`, and `scripts/sync-upstream.sh`). This includes incoming `install.sh`, `scripts/install-opencode.py`, conversion rules, `bootstrap.sh`, `AGENTS.md`, root `README.md`, model template, native skill/guide overlays, and `scripts/tests/test_opencode_install.py`. The entire incoming `INSTALL.md` is preserved verbatim as the current file's prefix; policy documentation is additive.
- The current diff against `origin/main` contains **15 paths**, all port-owned configuration/state/schema/report/verifier/new-test or the three declared overlay modifications. There is no incoming installer/native-overlay/test/model/source deletion or rewrite in this branch delta. The plan's earlier reconciliation log stated 16; 15 is the independently observed current count.
- Exactly **163 remaining Cursor source files/content/modes** match `ccb5507cec1546dc88135c1139c811e6c59115ba:pstack`. Root `README.md` is the intentional pre-existing user-owned overlay, not a failed raw-source comparison; it remains unchanged from incoming main. It is protected by policy and preserved by sync.
- The selection retains the correct `pstack/` source prefix and Cursor rationale/acceptance intent. Its seven target entries cover the real entry point, staged Python installer, strict transform, native skill/guide trees, INSTALL guidance, and repository port-agent guidance. Raw source, root README/AGENTS/bootstrap, model defaults, incoming tests, policy/schema/verifier/checkpoint, and workflows remain outside model edit permission. Native overlays are eligible adaptation paths for future selected port proposals but are unchanged by this reconciliation.
- Fresh pstack model defaults are now **`inherit-parent`**, not Sol-pinned defaults. The runner's `opencode/gpt-6-luna` choice is independent of those roles. Current policy/port documentation preserves confirmed user choices, omits guessed model aliases, retains explicit Claude/Cursor compatibility flags, and identifies unsupported platform semantics as blocked rather than granted privileges.

### Current installer/verifier evidence

All required commands ran with fresh controlled HOME/XDG and sanitized parent environments, including the complete incoming test suite:

```text
$ bash -n install.sh scripts/sync-upstream.sh bootstrap.sh
[exit 0; no output]

$ python3 -m unittest discover -s scripts/tests -p 'test_*.py'
.............................
Ran 29 tests in 8.578s
OK

$ python3 scripts/verify-opencode-port.py
verified isolated OpenCode install twice: 51 skills, 2 flat agents,
50 generated wrappers; 189 protected source/overlay hashes unchanged;
un-pinned manual baseline

$ git diff --check
[exit 0; no output]

$ git diff origin/main --name-only
[exit 0; 15 port-owned delta paths, audited as described above]
```

The two actual installs use a nondefault XDG path containing a space. They verify native manual-only frontmatter without speculative metadata, marked wrappers/custom-command collision and stale-wrapper cleanup, user-selected role bytes, managed AGENTS guidance/preimage/backup, unrelated skill/agent sentinels, byte-preserved JSON/JSONC, native skill replacements and exact guide-overlay copies, strict conversion failures before publication, and repeated-install idempotency. Default OpenCode installation produces no `.cursor` or fallback `.config` tree. Only `poteto-agent` and `comment-sicko` are installed globally as subagents; the repository's port-agent file is intentionally excluded and is not counted as an installed third agent. Incoming tests exercise explicit compatibility, resource/guide links, fallback XDG behavior, staged failure, and backups without changing their source.

### Actual policy/checkpoint and both plan interfaces

Actual original-tool `loadConfig`, `parseState`, `policyHash`, hosted `parsePolicy`, registration projection, and Ajv Draft 2020-12 validation accepted the current policy. Local schemas remain exact original-tool copies. The current normalized policy hash is:

```text
54a24fc368ab6359852544853451e4af50a18d3d10c7806bf85cd2ef018561f6
```

`lastSyncedCommit` and `.upstream-sha` remain at ccb, not latest upstream HEAD. Runtime progression still checks source/policy identity and CLI `plan.from`; malformed/conflicting packets, checkpoint mismatches, and selected-source mirror lag remain covered by the passing suite.

The actual CLI `writePacket()` generated a disposable adopt packet with **122 exact selected ccb files in each snapshot**. Complete plan size was **1,130,603 bytes**, below 2,000,000; future plans remain bounded and are not guaranteed to fit. Both complete configured command chains passed independently:

```text
CLI packet fixture:
  bash -n install.sh scripts/sync-upstream.sh bootstrap.sh   exit 0
  full unittest discovery                                 29 tests, OK
  verify-opencode-port.py --require-plan                   exit 0
  51 skills, 2 agents, 50 wrappers, 189 protected hashes; selected=True

Hosted-pin fixture, internal CLI config/state omitted:
  bash -n install.sh scripts/sync-upstream.sh bootstrap.sh   exit 0
  full unittest discovery                                 29 tests, OK
  verify-opencode-port.py --require-plan                   exit 0
  51 skills, 2 agents, 50 wrappers, 186 protected hashes; selected=True
```

The hosted fixture's three fewer hashes are the intentionally omitted root CLI config, state, and internal ignore file, not lost raw source. CLI packet SHA-256 remained `20e80e589bfd3a7b1143a800c4208902b6aa3fc0a50de49fa7bc38ff9ab43c19` after its full chain; its state bytes remained unchanged. Current-target ccb state/mirror bytes stayed unchanged throughout, and no packet was written to the current target. Prior launcher-source/digest/child-environment evidence is carried forward from the repair recheck; no broad original-App re-audit was needed or claimed.

### Current publication/activation limits

The configuration is approved for **draft-only** publication on this reconciled base. It is not published by this review. The planner reports fresh read-only App-access evidence for App `5266090` / installation `170044765`, but the grant is **`repository_selection: all`**. Do not describe it as target-only or least-privilege access; scope acceptance/narrowing remains an operator decision before activation, with other access preserved. This review made no App/key/provider/backend call or permission change. Hosted backend/registration, production runtime compatibility, inference, manual approval, and full pstack semantic equivalence remain separate unproved gates.

## Prior-base targeted repair recheck — historical evidence

The bounded repairs were inspected in the live target verifier/tests and the original tool's metadata adapter, launcher source/digest, and sandbox tests. No broader App or architecture audit was performed.

| Finding | Status | Independently observed closure |
| --- | --- | --- |
| R1: launcher strips trusted pins | Resolved | Exact launcher source preserves the three public request-derived pins, rejects malformed pin values, and strips unrelated secret/model fields. The selected and unselected launcher regressions both pass. The digest matches the source; the bundled inventory verifier remains unchanged. |
| R2: configured suite fails with packet present | Resolved | Missing/malformed/conflicting packet tests use private roots. The complete configured command chain passes in a disposable target with a packet generated by the actual CLI `writePacket()` API and containing both complete baseline source snapshots. Packet bytes are unchanged after verification. |
| R3: checkpoint permanently frozen | Resolved | Runtime validation binds state to source identity, the reviewed normalized policy hash, and CLI `plan.from`, without requiring the initial SHA forever. Sequential checkpoint regressions pass. An advanced-state/unselected-future packet passes the complete installer verifier; mismatched starting checkpoint and policy hash are rejected. Current seed remains unchanged. |
| R4: Git fixtures inherit caller configuration | Resolved | All fixture command helpers require explicit environments. Git initialization, commits, staging, local pushes, and config checks use owned HOME/XDG/config/template/PATH settings; hooks are disabled in the Git helper. The controlled caller-template/config regression and real rsync fixture pass. |

The launcher digest is now `8496f5af1077ecf152130b9382983b99ad1385e7849ff4a91ff9b242e6cc6366`. The environment regression executes the exact launcher code with privilege operations and `execvpe` mocked, capturing its final child argv/environment. It is a real code-path contract check, not an actual root/nonroot process or Docker/live-runtime test. Metadata still comes from `RunnerRequest.plan`; similarly named extra fields do not replace its pinned values.

### Commands and results observed in this recheck

All commands below ran with fresh controlled HOME/XDG and sanitized environments:

```text
$ python3 -m unittest discover -s scripts/tests -p 'test_*.py'
..............
Ran 14 tests in 2.851s
OK

$ python3 scripts/verify-opencode-port.py
verified isolated OpenCode install twice: 51 skills, 3 flat agents,
50 generated wrappers; 164 raw source hashes unchanged; un-pinned manual baseline

$ git diff --check
[exit 0; no output]

$ npm test -- --project node test/sandbox.test.ts
Test Files 1 passed (1)
Tests 34 passed (34)
[includes selected and unselected exact-launcher environment tests]

$ npm run typecheck
tsc --project tsconfig.json --noEmit
[exit 0]
```

The actual CLI-generated packet had 122 selected files in each baseline snapshot and the actual normalized policy hash `257e684570980d95172a23c12edaf8882cf6839214e803128d1f7e4c95f8c548`. Independently rerunning every command from `oc-port-agent.json.verification` in that disposable target produced:

```text
bash -n install.sh scripts/sync-upstream.sh                  exit 0
python3 -m unittest discover -s scripts/tests -p 'test_*.py'  14 tests, OK
python3 scripts/verify-opencode-port.py --require-plan
    51 skills, 3 flat agents, 50 wrappers; 164 hashes unchanged
    plan ccb5507cec1546dc88135c1139c811e6c59115ba (selected=True)
```

Packet SHA-256 remained `09b9c6f3001354ca2c944a5cf9f26245ad29542177e92d067342d811030a1140`; the fixture's initial state bytes also remained unchanged. A separate disposable progression case used an advanced checkpoint and an unselected future source packet and passed the full pinned installer check with `selected=False`. Starting-checkpoint and policy-hash mismatches each exited 1 with the corresponding explicit blocker. Synthetic progression fixtures prove the validation interface, not that those invented commits were actually ported or merged.

Offline source recheck reconfirmed all 164 upstream files/content/modes exactly match `ccb5507cec1546dc88135c1139c811e6c59115ba:pstack`. Installer, transform, model map, workflow, and mirror SHA still match the target HEAD versions. Current `.oc-port/state.json` bytes and `.upstream-sha` bytes remained unchanged at ccb throughout; no packet was written to the current target. The policy/selection/schema scope guards and selected-source mirror equality remain intact.

## Initial findings — resolved; historical evidence

The following records explain the original blockers. Their original reproductions and proposed repairs are retained as history; the closure assessment above supersedes their blocking disposition.

### R1 — Hosted plan pins disappear at the privilege-drop boundary

**Priority: high.** The original tool's `apps/cloudflare/src/sandbox.ts:129-139,603-613` validates the pinned request and adds `OC_PORT_UPSTREAM_COMMIT`, `OC_PORT_TARGET_COMMIT`, and `OC_PORT_HAS_SELECTIONS` to the sandbox exec environment. However, `apps/cloudflare/src/sandbox-helper-assets.ts:13-17,38-41` constructs the actual child environment using `SAFE_ENV_KEYS`, which contains none of these keys.

The new tests in `apps/cloudflare/test/sandbox.test.ts:470-498,596-608` inspect the environment passed to the fake sandbox, not the environment passed by the launcher to the verification child. They therefore pass while the real metadata contract is broken. Hosted snapshots omit the internal CLI packet, so `--require-plan` has no alternative source for its pins.

**Reproduction:** extracted the exact bundled launcher source and ran its real `main()` with mocked UID/GID operations, a controlled environment containing all required existing keys plus the three pins, and a mocked `execvpe`. Captured result:

```text
pins at execvpe: {'OC_PORT_UPSTREAM_COMMIT': None,
                 'OC_PORT_TARGET_COMMIT': None,
                 'OC_PORT_HAS_SELECTIONS': None}
Hosted verifier consequence: --require-plan needs a CLI packet or trusted Worker plan environment
```

**Smallest repair:** authorize a narrow change to the original tool's `apps/cloudflare/src/sandbox-helper-assets.ts` to preserve exactly these validated public metadata keys across the launcher boundary, and update its source digest consistently. Keep all other environment filtering, privilege dropping, static command permissions, and helper/inventory guards intact. Extend `apps/cloudflare/test/sandbox.test.ts` with a launcher-to-child contract regression, including selected and unselected plans. This additional implementation file is outside the reviewer's ownership and requires planner approval; do not substitute model text, operator environment overrides, or argv-based arbitrary execution.

### R2 — The configured CLI unit suite fails whenever its required packet exists

**Priority: high.** `scripts/tests/test_port_policy.py:95-113` tests missing plan metadata against the live `ROOT`, expecting `plan_metadata(ROOT, {}, required=True)` to raise. The actual CLI calls `writePacket()` before running all configured verification commands (`src/sync.ts:82,105` in the original tool). Consequently, even a valid, mirror-matching packet makes this test fail, before the final pinned installer check is reached.

**Reproduction:** copied the target into a disposable directory and used the actual built CLI's `loadConfig()` and `writePacket()` to write a baseline-pinned adopt packet. Running the exact configured unit-suite command produced:

```text
CLI packet fixture unit-suite exit: 1
FAIL: test_plan_pins_are_required_and_selected_changes_must_match_raw_mirror
AssertionError: VerificationError not raised
Ran 10 tests
FAILED (failures=1)
```

**Smallest repair:** perform missing, malformed, and stale-packet assertions against separate temporary roots, never against a runtime root that can legitimately contain the host's packet. Add a regression that runs the configured suite in a disposable tree with an actual CLI-generated valid packet present. It must pass without deleting or weakening the protected packet or relaxing `--require-plan`.

### R3 — Runtime checkpoint validation permanently freezes the initial baseline

**Priority: high.** `scripts/verify-opencode-port.py:291-298,587-590` rejects every `lastSyncedCommit` other than the initial `ccb5507…` checkpoint. The original CLI intentionally writes `lastSyncedCommit = plan.to` only after successful verification, in its proposal branch (`src/sync.ts:113-124`). After that reviewed proposal merges, every later CLI run and manual installer check fails because the committed checkpoint has legitimately advanced. This also affects checkpoint-only proposals for unrelated upstream changes.

The initial configuration audit should prove that this PR records the explicit reviewed baseline. That is distinct from the runtime verifier's responsibility to accept later host-managed checkpoints and reject mismatched policy or plan state.

**Reproduction:** in a disposable state fixture, retained the actual normalized policy hash and source metadata but changed `lastSyncedCommit` to another complete upstream SHA. The original CLI's actual `parseState()` accepted it; the target verifier rejected it:

```text
Actual CLI parseState accepts advanced checkpoint
Advanced checkpoint rejected by verifier: initial checkpoint moved from the explicitly reviewed baseline
```

**Smallest repair:** separate one-time baseline auditing from runtime checkpoint validation. Runtime validation must preserve complete commit syntax, source identity, and the actual normalized policy-hash contract; for CLI plans, check consistency with the trusted packet's starting checkpoint where applicable. Do not rewrite the checkpoint, acknowledge upstream HEAD automatically, or bypass mirror equality for selected changes. Add regressions for a legitimate already-advanced checkpoint, mismatched policy/starting checkpoint, and an unselected future source commit with an older raw mirror.

### R4 — Local Git fixtures inherit the caller's user environment

**Priority: medium; required by this task's isolation convention.** `scripts/tests/test_port_policy.py:21-38,203-215,229,256-266` runs multiple Git commands with `env=None`. `source_env` also starts from `os.environ` at line 210. Although the installer and sync subprocesses have explicit temporary environments, fixture initialization, staging, and local pushes can still read real HOME/XDG Git configuration or inherit caller Git overrides and template/hook settings. The suite is not wholly isolated as claimed.

**Reproduction:** supplied a fresh controlled HOME and an inert temporary Git config pointing to a template directory containing a marker, then called the existing test helper's `git(..., 'init', ...)`. No hooks were created or executed. The resulting fixture inherited the marker:

```text
Test helper inherited caller Git template: True
```

**Smallest repair:** construct a fresh sanitized HOME/XDG/Git environment before every fixture command and pass it explicitly throughout the test helpers. Do not merge the caller's environment. The CI-identity test may explicitly substitute its own temporary Git config to prove invocation-only identity and unchanged fixture config. Add a controlled inherited-template/config regression without reading actual user configuration or credentials.

## Initial review checks that passed

The four requested baseline commands all exited zero:

```text
$ bash -n install.sh scripts/sync-upstream.sh
[exit 0; no output]

$ python3 -m unittest discover -s scripts/tests -p 'test_*.py'
..........
Ran 10 tests in 3.050s
OK

$ python3 scripts/verify-opencode-port.py
verified isolated OpenCode install twice: 51 skills, 3 flat agents,
50 generated wrappers; 164 raw source hashes unchanged; un-pinned manual baseline

$ git diff --check
[exit 0; no output]
```

Additional observed evidence:

- Original metadata adapter subset: `npm test -- --project node test/sandbox.test.ts` passed all 32 tests; `npm run typecheck` exited zero. These are not a substitute for R1's child-environment regression.
- Offline Git tree/content/mode comparison: all 164 raw mirror files exactly match `ccb5507cec1546dc88135c1139c811e6c59115ba:pstack`. `install.sh`, `scripts/opencode-transform.py`, model mapping, workflow, and raw mirror SHA remain unchanged by Phase 1.
- All three local schema files are exact byte copies of the original tool schemas. Actual CLI `loadConfig`/`parseState`, Worker `parsePolicy`, and Ajv Draft 2020-12 validation accepted the current policies and resolved local instruction references.
- Actual normalized checkpoint policy hash is `257e684570980d95172a23c12edaf8882cf6839214e803128d1f7e4c95f8c548`, matching the checked-in state.
- The actual CLI selector selects 122 files at the baseline. A complete full/adopt plan containing both snapshots measured 1,129,122 bytes, below the 2,000,000-byte limit. Arbitrary future diffs are still subject to the tool's complete-context limit; no truncation or future-size guarantee is claimed.
- Real rsync/Git fixture tests passed, preserving the root policy, `.oc-port` checkpoint/ignore/report files, overlay agent, and model map. CI commit identity is invocation-scoped; no new workflow, schedule, model writer, or global Git config command was added.
- The actual installer strict-hit drift regression fails installation, while normal repeated installation is idempotent and preserves the tested unrelated skill/agent, custom-command collision, user config fields, backup, and model-role instruction copies. The verifier's policy/selection/schema hash pins reject the tested scope and instruction drift. These checks do not prove arbitrary transform changes or skill behavior equivalent.
- A future source commit with trusted `hasSelections=false` is accepted without advancing or requiring the raw mirror. A selected future source pin against the older mirror is rejected. The result labels selection state rather than claiming old installed files prove selected future-source parity.

## Current policy and scope assessment

The policies point to `cursor/plugins` branch `main` with the correct `pstack/` prefix and one combined selection. The current seven target entries include the staged installer and native skill/guide trees and remain separate from raw source, root README/AGENTS/bootstrap, policy/schema/verifier/checkpoint, tests, workflows, and user model defaults. Fresh role defaults inherit the parent and existing user-selected roles are preserved; the CLI runner's model is independent. Hosted policy has no executable/model settings. Registration is explicitly a template, not an activation record.

Reviewed original CLI packet/agent-definition and hosted prompt construction: structured `goal`, `adaptation`, and `nonGoals` reach the agent as bounded operator intent; preserved/protected scope remains separately enforced. Source instructions are reference data, not permissions. Metadata originates in `RunnerRequest.plan`, not model responses. Existing snapshot, output-observer, and mutation/inventory report boundaries were not changed by the metadata addition.

OpenCode V2 [tools](https://opencode.ai/v2/docs/tools), [skills](https://opencode.ai/v2/docs/skills), and [CLI commands](https://opencode.ai/v2/docs/cli/commands) confirm the documented subagent/background/session continuation, structured question/multiple-choice, manual-only skill, and session-export mechanics. Cursor-only UI/cloud/scheduling behavior must remain blocked absent separate proof. Existing install-time platform substitutions were not reimplemented or certified as full semantic parity by this review.

## Nonblocking operational caveats

- No independent live App call was made by this review. Planner-reported target access is granted through an **all-repositories** installation, not a target-only selection. No deployed backend, active hosted registration, published tool, or model-run proof was obtained here; the template cannot establish any of these.
- The original tool is local/private. Do not present a public install command or hosted unattended synchronization as usable or active from this configuration alone.
- Human direction/baseline and real-target installation/activation approval remain pending. Neither manual plan checkbox was changed.
- Hosted runtime/image and complete target-snapshot compatibility were not exercised with this repository; no Docker or live backend was run. Preserve existing snapshot/probe protections and review deployment readiness separately. The current hosted service has no initial `--full` adoption support.
- The existing six-hour raw mirror remains separate from semantic verification. Do not advance `.upstream-sha` or the initial checkpoint to make the reproductions pass.

## Publication handoff

The independent review gate for the draft configuration PR is cleared on the reconciled `30a3cbd` base within the bounded current policy/verifier/metadata scope. Planner may proceed with draft-only publication and report the current 29-test/two-agent/189-hash results, not stale prior-base counts. No PR was created by this recheck. Keep incoming user files, the 163 raw source files, current ccb seed/mirror SHA, schemas/policy, model defaults, and schedules unchanged. Human approval, the all-repositories App scope decision, hosted registration/deployment readiness, live runtime compatibility, and semantic behavior proof remain separate gates.
