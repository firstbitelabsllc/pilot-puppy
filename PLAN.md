# Pilot Puppy — Plan

This file is the sole plan, proof, and resume authority for Pilot Puppy.

## Outcome

Give one person a calm chief-of-staff view of what their coding work is trying
to achieve, what is happening now, what proof exists, and which A/B/C decision
matters next—then drive bounded work through native Codex, Claude Code, or
Cursor without taking custody of credentials or conversations.

## Operator Brief

- Outcome ID: prove-pilot-puppy-portability
- Outcome Revision: 4
- Outcome Updated At: 2026-08-03T15:02:37Z
- Outcome State: working
- Outcome: Prove one simple Pilot Puppy product can be cold-started on another computer and safely drive a native coding host without adding a second platform.
- Next: Freeze the target task packet (file/ID, clean revision, allowed paths, proof command), then run public-main clone/install/mount/doctor and one native task. Accept only `status: ok`, exact paths, and lead reproduction. Quota reset is fallback; do not add a platform.
- Proof ID: pilot-puppy-other-computer-unblock
- Proof: .pilot-puppy/evidence/other-computer-unblock.json
- Proof Summary: v2.0.0 is public, the local doctor is 11/11, PR #90 merged after all checks passed, and Claude Code/Cursor sealed tasks pass; the portable task inputs and second-computer receipt are not yet present, while native Codex execution is quota-blocked.
- Proof Delivery: pending

## Product boundary

- One product, repository, package, command, skill, configuration boundary,
  local evidence path, and user-facing name: **Pilot Puppy**.
- `PLAN.md` is durable authority. Receipts are bounded evidence, never a second
  queue or source of truth.
- Native coding hosts execute. Pilot Puppy seals scope, invokes one selected
  host, validates its receipt, and leaves final acceptance to the lead.
- The browser reads the same Outcome and renders one status brief plus one
  A/B/C choice. It does not run a cloud executor or store chat transcripts.
- No aliases, hidden products, daemon, scheduler,
  watcher, credential relay, remote database, or background dispatch loop.

## Platform-unblock boundary

- The new platform effort is portability to a second computer, not a new
  executor, router, queue, daemon, or control plane.
- The handoff source is PR #90 at `06a84b2d798096bcae79a3585d34908a7609ebb3`.
  Its checks were green and it merged to `main` as
  `0c6d8ce19dc5efdf944196c5db7600d1d1a030a4` at
  `2026-08-03T14:56:42Z`. This proves the source is public; it does not prove
  a second computer has installed or read it back.
- The second computer owns its native host authentication. The only required
  local proof is clone/install, `pilot-puppy doctor`, the three skill mounts,
  and one bounded native-host receipt with lead reproduction. `doctor` proves
  host availability only; it is not execution proof.
- The public handoff has bootstrap instructions, not a target-specific task
  packet. The second computer must receive the frozen task file, task ID, clean
  target revision, exact allowed paths, and proof command. Keep private target
  paths, prompts, credentials, and transcripts out of this public repository.

## Unblock map

- **Source and CI: WORKS.** PR #90 at `06a84b2d798096bcae79a3585d34908a7609ebb3`
  passed every required check and merged to `main` as
  `0c6d8ce19dc5efdf944196c5db7600d1d1a030a4`. There is no code or CI failure
  to fix in this handoff.
- **Public landing: DONE.** The handoff is now in the protected public
  `main`; this is a source/release receipt, not proof of another computer.
- **Portable task inputs: OPEN GAP.** The public handoff does not contain a
  target-specific frozen task packet or target revision. Need: those exact
  inputs, carried without private prompts or credentials, before a host receipt
  can be trusted as a cross-computer proof.
- **Second-computer bootstrap: READY.** Once those inputs exist, use the public
  clone for clone/install/mount/doctor and one clean brief readback. If doctor
  fails, fix only the named bootstrap prerequisite.
- **Native Codex proof: BLOCKED UNTIL RESET.** The account quota resets after
  `2026-08-07 23:52 America/New_York`; only then can the same sealed task be
  rerun. A version probe, another provider, or a new platform layer is not a
  substitute.

## Privacy and safety

- Local by default; loopback browser only.
- Evidence is project-bounded, retention-bounded, and free of credentials,
  prompts, transcripts, provider payloads, and absolute private paths.
- Writes are atomic and idempotent. Host work is limited to an exact worktree
  and explicit allowed paths. Scope escape fails closed.
- Git history is preserved with ordinary forward commits.

## Work

- [completed] Establish the canonical package, command, skill, configuration,
  schemas, browser identity, and local state contract.
- [completed] Fold in the smallest proven native-host driver for Codex, Claude
  Code, and Cursor, with a sealed task and validated bounded receipt.
- [completed] Prove restart/resume, chief-of-staff status, A/B/C choice, privacy,
  packaging, installation, documentation, and full test behavior.
- [completed] Replace shared, private, and installed callers, then remove every
  predecessor command, skill, mount, hook, job, configuration, and active file.
- [completed] Rename the existing GitHub repository in place, merge, release,
  fresh-install, and read back the remote, mounts, command, and real UI.
- [completed] Run the final cold review and zero-surface audit; close only when
  all changed repositories are clean, pushed, and remotely verified.
- [in_progress] Close the portable proof gap: freeze the exact task packet and
  target clean revision, run the other-computer clone/install/mount/doctor path,
  execute one bounded native-host task, and reproduce its proof from the lead
  checkout.
- [blocked] Rerun the same sealed native Codex task after its account quota
  resets; require `status: ok`, the exact allowed-path change, and a
  lead-reproduced check. Do not substitute a version probe.

## Mechanical proof required

- Full tests, docs, package, privacy, security, fresh clone, and install pass.
- `pilot-puppy doctor` passes; removed commands fail lookup.
- Codex, Claude Code, and Cursor each complete one sealed task with
  lead-reproduced proof.
- One real Outcome survives restart and renders an accurate brief and A/B/C
  choice.
- Active repositories and installed roots contain no predecessor product
  names, duplicate state, credentials, raw transcripts, or absolute private
  paths.
- The renamed public remote, release artifact, installed skill, command, and UI
  all read back as Pilot Puppy.
- The portable task packet has a stable task ID/hash, target clean revision,
  exact allowed paths, and proof command; it contains no private prompt,
  credential, transcript, provider payload, or absolute private path.
- A fresh second computer can install the exact handoff revision, pass
  `pilot-puppy doctor`, mount the same skill in Claude Code, Codex, and Cursor,
  and render the same Outcome and A/B/C brief.
- The same sealed native Codex task returns `status: ok`, changes only its
  allowed path, and passes lead reproduction after the quota reset.

## Progress

- 2026-08-02: Established one product authority. Outcome, briefing, decision,
  privacy, and native-host behavior stay; unrelated machinery is removed.
- 2026-08-02: Public core gate passes 79 Python tests, 3 JavaScript tests,
  4 desktop/phone browser tests, docs build, privacy fixtures, and a reproducible
  51-file stranger install. Real host, restart, cross-repository, and remote
  release proof remain open.
- 2026-08-03: Public main `6bd03c3f` passes 79 Python, 3 JavaScript, and
  4 Chromium tests, the 81-file public-ready scan, docs build, zero-vulnerability
  install, and a 51-file release package with SHA-256
  `9827381f6570dac1bf5e66611fae4056e18f3a14c6a914d85a099e5d5643b8cb`.
- 2026-08-03: `pilot-puppy doctor` passes 11/11 with one command and the same
  Pilot Puppy skill mounted in native Claude Code, Codex, and Cursor roots.
  Every predecessor command fails lookup; shared main is `c9efb7fe` and private
  main is `958a6163` after caller and runtime removal.
- 2026-08-03: Real sealed Claude Code and Cursor tasks changed only their exact
  allowed file and passed lead-reproduced checks. The real Codex CLI changed
  nothing and failed because its account usage limit resets after
  2026-08-07 23:52 America/New_York.
- 2026-08-03: A real mobile Chromium brief retained the identical
  `a4bf32b072f933ea2d89535097c3dc157a4c02ef3f2bb4ceec9d821d531f0f3f`
  API hash across a full server stop/restart and rendered the same Outcome and
  A/B/C choices.
- 2026-08-03: The final read-only Fable cold-review attempt returned no review
  payload after 12 internal turns and ended `aborted_streaming`; it is recorded
  as an unavailable sidecar, not approval. The lead Thermo audit found no
  duplicate authority, state store, runtime, compatibility surface, or release
  blocker. A stale unrelated health watcher was retargeted to neutral local
  state, stale Claude cleanup hooks were removed, and the retired state root
  was absent after final configuration validation.
- 2026-08-03: PR #88 merged as `6375c84a`; public release `v2.0.0` points to
  that exact commit and is the only visible release. Its attached 51-file
  package has SHA-256
  `9827381f6570dac1bf5e66611fae4056e18f3a14c6a914d85a099e5d5643b8cb`.
  A fresh public tag clone passed a zero-vulnerability install, 3 JavaScript
  tests, 79 Python tests, the 81-file public-ready scan, docs build, stranger
  package install, version readback, and a real new-repository A/B/C brief.
- 2026-08-03: PR #90 (`06a84b2d`) adds the portable other-computer handoff;
  GitHub reported every required check green and it merged to public `main` as
  `0c6d8ce19dc5efdf944196c5db7600d1d1a030a4`. The second computer can now use
  the normal public clone rather than a PR checkout.
- 2026-08-03: The current computer passes `pilot-puppy doctor` **11/11**.
  This proves local readiness only; it is not second-computer portability
  proof. No new platform layer is justified: the existing native-host and
  project-local evidence boundaries are the canonical design.
- 2026-08-03: The goal was narrowed to the real platform unblock. PR #90 is
  public and the local host is ready, but the public handoff has no
  target-specific frozen task packet or second-computer execution receipt. The
  next move is to supply those bounded proof inputs, not to add another
  executor, router, queue, daemon, or control plane.

## Blocked proof

- The source and bootstrap are not code-blocked. The current gap is the
  target-specific frozen task packet and clean target revision. **Need:** a
  task ID/hash plus a second-computer receipt with `status: ok`, exact
  allowed-path change, proof command result, and lead reproduction. The public
  repo intentionally does not carry private target prompts or credentials.
- Native Codex execution is blocked until **2026-08-07 23:52
  America/New_York**. At or after that time, rerun the same sealed task; it
  must return `status: ok`, change only its allowed path, and pass the
  lead-reproduced check. A binary/version probe does not satisfy this gate.
- If the second-computer doctor fails, record the exact failed check and fix
  only that bootstrap prerequisite. Do not respond by adding a router, daemon,
  scheduler, credential relay, transcript store, or second plan.
