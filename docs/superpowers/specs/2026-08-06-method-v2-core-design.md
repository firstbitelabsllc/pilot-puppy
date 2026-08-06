# The Method v2 — core design (tribunal spec, awaiting operator review)

Status: **DESIGN — not yet law.** Produced by a three-round adversarial debate
(2026-08-05→06): ten Round 1 seats across /thermo /ponytail /brand-resplit
/shadow lenses, a five-judge simplification tribunal plus chief judge in
Round 2, and Round 3 cross-examination (one of four examiners completed
before an API session limit; three remain — see Open Items). Full records:
`2026-08-06-method-v2-debate/`. Binding operator steer: *"this method
shouldn't bake TOO many concepts."*

Nothing in this spec changes shipped behavior until the operator approves it
and an implementation plan lands. One Round 1 finding was urgent enough to
ship immediately and already did: AGENT.md was missing from the npm package
(v3.0.1, PR #252).

## Verdict

The shipped Method carries ~28 named concepts. The tribunal ruling, adopted
from the chair's Approach A: **8 core concepts + 12 folded behavior
sentences + 3 deferred items; everything else deleted** (~2,500 lines of
coordination code). One binding condition from the gates ruling: **no
deletion of prose law lands without `scripts/shadow-lint.py` landing in the
same commit** — prose enforcement is proven aspirational (the flagship plan
violated its own lint on day one).

### The core eight

1. **The plan file** — one markdown authority per repo, one writer at a time.
2. **The checkpoint row** — verifiable state + typed `proof:` (`cmd` |
   `read` | `gate <owner> resume:`), addressed by `~hash4`, ordered by
   `needs:`, flipped only in the same commit as its PROOF line.
3. **Two postures** — `Mode: Broad | Close`; flips are written, paired,
   same-commit ("broad vs closing time" was the operator's original phrase).
4. **Defer is a write** — row + wake predicate, never a state.
5. **The gate pair** — "why vs just exploring" + "what does this
   contradict," landing in `## Contradictions`.
6. **Close** — the harness defines done: proof line per DoD clause,
   re-observed from fresh state; lesson folded or `LESSON none`; receipts
   archived; owner-gated DoD closes agent-side with a handoff.
7. **The milestone** — `###` heading, 2–7 rows, exactly one `(DoD)` row that
   flips last; status derived, never stored.
8. **Entity line + read-only board** — entity is a grep result; the board
   derives at read time, renders the lint verdict per card, and shows
   unparseable plans as red cards, never best-effort counts.

The full per-concept verdict table, the complete AGENT.md v2 draft, and the
grammar v2 file contract are in
`2026-08-06-method-v2-debate/r2-ruling-06.md` (chief judge). Cluster
rationale: r2-ruling-01 (verification), -02 (modes), -03 (surfaces),
-04 (structure), -05 (row tokens).

### Notable deletions (with their reactivation triggers)

- **CLAIM/DONE bookkeeping** — deleted; git merges identical edits silently,
  so CLAIM cannot detect the collision it exists for. Reactivates on the
  first verified double-work incident; the fix is `shadow accept --row` as
  the only flip path, never prose.
- **Four-mode vocabulary + 4×4 transition law** — collapsed to the two
  postures; Spike/Challenge survive as folded sentences (boxed exploration
  with a forced keep/kill/promote verdict; written demotion).
- **Drive packet/lane vocabulary** (#33/#34) — fold to `shadow accept
  --row` keeping the clean-checkout mechanical acceptance. *Contested;
  cross-exam unfinished — see Open Items.*
- **roster/route/seat (1,777 lines)** (#35) — DELETE **as amended by the
  completed Round 3 cross-exam** (`r3-crossexam-roster.md`): the deletion is
  affirmed but must land in the same commit as the Drive change with the
  full excision manifest (bin dispatch, release manifest, host.py route
  plumbing); bare `shadow host run --host <name>` is already the shipped
  roster-free sealed path, so zero new code is required.
- **Langfuse seam** (#38) — deleted by the tribunal (cannot attribute any
  real failure class). *Directly conflicts with an operator request the same
  night; cross-exam unfinished — operator decision, see below.*
- **`size:` tokens, sha256 mint recipe, M-id machinery, mass thresholds,
  stored `- Milestone:` line, `- Loop:` line (when derivable)** — deleted,
  folded, or deferred per the table.

## Operator decisions (default-if-silent stated)

- **D-1 Account pinning:** A (default) — no account/profile surface in
  Shadow; provider/model/account selection lives in delegate/routing.json/
  env. B — keep one dumb `--profile` passthrough (~15 lines). Flip to B only
  when a sealed run needs a pin env config cannot express.
- **D-2 Langfuse:** A — accept the deletion; stress-test observability =
  git history + `shadow lint` trends + the deterministic stress rig
  (`tests/test_method_stress.py`, proposed by the Round 1 stress seat).
  B — keep the seam for Drive-fever dashboards. Default pends the unfinished
  cross-exam; no default is claimed here.
- **D-3 Two postures vs four modes:** tribunal ruled two; dissent D3
  (exploration/interrogation blur) reactivates the explicit exploration box
  after two consecutive Closes with no written Broad verdict. Cross-exam
  unfinished; the ruling stands as the proposal.

## Open items — exact resume predicate

Session limit hit 2026-08-06 ~02:10 ET (resets 04:10 ET). Resume move:

1. Re-run Round 3: `Workflow({scriptPath: ".../shadow-crossexam-r3-wf_1cbfdc76-3f3.js", resumeFromRunId: "wf_1cbfdc76-3f3"})` — the roster seat replays from cache; drive, langfuse, postures run live.
2. Fold the three verdicts into this spec; resolve D-2's default.
3. Operator reviews this spec (the brainstorming user-review gate).
4. On approval: superpowers:writing-plans → implementation plan for the v2
   rewrite (AGENT.md v2 + grammar v2 + shadow-lint.py + the amended
   deletions), executed as Method-shaped checkpoints under `Mode: Close`.
