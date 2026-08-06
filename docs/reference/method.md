# The Method — file contract (grammar v2)

Machine-readable grammar for `AGENT.md`. Every construct is a heading, list
line, or grep over `PLAN.md`. Nothing requires a registry, database, daemon,
queue, or writable board. `scripts/shadow-lint.py` is the enforcer: it runs
in the test gate and before any posture flip is honored.

## Sections, in order

```markdown
## Operator Brief
- Entity: <name>              required; the entity is the grep across plans
- Mode: Broad | Close         required; the only legal values
- Priority: 1-5               optional; steering-default rank
- Loop: /<skill>              only when it differs from /<entity>-loop

## Checkpoints
### <milestone heading>       2-7 rows + exactly one (DoD)
- [pending] <state the world reaches> ~ab12 | proof: cmd <runnable> | needs: ~cd34
- [pending] <...> ~ef56 (DoD) | proof: read <artifact/url> -> <observation>

## Deferred
- <what> | <why not now> | wake: <predicate>

## Contradictions
- <what contradicts what> | provisional winner | opened <ts>

## Progress                    append-only, newest at bottom
- <ts> ~ab12 PROOF <check> -> <observed result>
- <ts> POSTURE Broad->Close | harness: <name>
- <ts> BOX ~ab12 <exploration question> | ends: <YYYY-MM-DD>
- <ts> VERDICT ~ab12 keep|kill|promote -> <one line>
- <ts> STRUCT <edit> | trigger: <why>
- <ts> STEER auto <option> | <reason>
```

## Brief law

`Entity:` values match `^[a-z][a-z0-9-]{1,31}$` — lowercase slug, no spaces,
no paths. Multi-repo entities repeat the same line in each member plan; the
entity view is the grep across them.

## Row law

- State ∈ `pending | in_progress | blocked | completed`.
- IDs are four base36 chars (`~ab12`), unique per plan, stable across
  reordering; on a mint collision, re-mint. References always use the hash.
- Proof classes: `cmd <runnable>` (machine-rerunnable), `read <artifact/url
  -> expected observation>` (a human or agent re-reads the real surface), or
  `gate <owner> resume: <predicate>` (person-gated; closes agent-side with a
  handoff). Bare prose proof is a lint finding. No proof, no completed.
- `needs: ~hash[, ~hash]` is the only readiness gate: a row is ready when it
  is pending and every needs-target is completed. A discovered row's paired
  Progress line names its origin row.
- A row flips completed only in the same commit as its PROOF line;
  `shadow accept --row` reruns a `cmd` proof in a clean detached checkout
  and is the only code path that flips a row.

## Milestone law

`###` heading over 2-7 rows plus exactly one `(DoD)` row, which flips only
after every sibling. Milestone status is derived at read time, never stored.
Structural edits land with a paired `STRUCT` Progress line naming the
trigger.

## Posture law

`Mode: Broad` is exploration and interrogation: boxes are opened with
`BOX ~hash ... | ends: <date>` and must end in a `VERDICT ~hash
keep|kill|promote` line — an expired box with no verdict blocks, and
entering or holding `Mode: Close` over one is refused
(`CLOSE-OVER-OPEN-BOX`). `Mode: Close` is entered only with a named harness,
via a `POSTURE` Progress line in the same commit as the mode edit. A
surfaced contradiction demotes to Broad in writing.

## Close law

Closing appends one proof line per DoD clause — named check plus observed
result, re-observed from fresh state — or a named owner handoff with a
resume predicate. The closing commit folds one lesson into standing
knowledge or writes `LESSON none — <why>`.

## ARCHIVE

The closing commit moves the milestone's `###` block, its Close proof
lines, and its Progress lines to `docs/plan-archive/<slug>.md`, leaving one
tombstone row. Moves only; deletion and regeneration are banned.

## LINT

`scripts/shadow-lint.py`, exit non-zero on blocking findings; deterministic
across reruns. Checks: row shape; ID-DUP; NEEDS-DANGLE; PROOF-MISSING /
PROOF-CLASS / PROOF-SECRET; DOD-COUNT; DOD-EARLY; DEFER-NO-WAKE;
MODE-ILLEGAL (legacy `Spike|Defer|Challenge` values included); TS-ORDER;
READ-FIT (warning, lines over 2,000 chars); BOX-NO-END;
BOX-EXPIRED-NO-VERDICT; CLOSE-OVER-OPEN-BOX; ORPHAN-VERDICT (warning).

## BOARD

Read-only projection of `- Entity:` greps. A card renders counts, the lint
verdict chip, the Contradictions count, and the current milestone — derived
at read time. An unparseable plan renders as a red card, never best-effort
counts. The moment any surface lets a viewer write a row or schedule work,
it is a banned second store.
