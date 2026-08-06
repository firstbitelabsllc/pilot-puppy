# AGENT.md — the Method, v2

One plan file per repo. One writer at a time. Everything below is checked by
`shadow lint` or it does not count. One chief of staff identity per session:
parallel hands run below it, never beside it.

## The core

1. **The plan file.** `PLAN.md` at the repo root is the only authority —
   markdown, greppable, no second store. One seat writes a plan at a time;
   a second writer is a Contradictions row, not a merge.

2. **The checkpoint row.** A row is a state the world reaches, with a `proof:`
   that can refuse bad work — `cmd <runnable>`, `read <artifact/url +
   expected observation>`, or `gate <owner> resume: <predicate>`. No proof,
   no completed, ever. A checkpoint fits in one cycle; anything larger is a
   milestone. A cycle drives one checkpoint to a recorded result before
   starting the next. A row flips completed only in the same commit as its
   PROOF Progress line; `shadow accept --row` reruns the proof in a clean
   checkout and is the only code path that flips a row.

3. **Two postures.** `Mode: Broad` or `Mode: Close`. Broad is thinking time:
   exploration is boxed up front and ends with a written keep / kill / promote
   verdict — a box past its end with no verdict is a lint finding; questions
   and contradictions get named, and the decision each resolved into gets
   written. Close is finishing time: entered only with a named harness. The
   posture changes only via a paired Progress line landing in the same commit
   as the flip, and the flipping seat re-reads the posture line immediately
   before that commit. A surfaced contradiction demotes Close to Broad in
   writing — never silently; repair the proof there, re-enter Close. The
   closer never rewrites the exam mid-sitting.

4. **Defer is a write, never a state.** One row: what | why-not-now |
   wake: predicate. A row without a wake predicate is deletion in denial.

5. **The gate pair.** Before any row lands: "is this needed, or am I just
   exploring?" and "what does this contradict?" A row that contradicts a
   MUST/NEVER in standing knowledge, or treats a person-gated item as
   agent-completable, blocks until the plan is edited — never the knowledge
   diluted. Contradictions live in `## Contradictions` and leave only via a
   Progress line citing evidence.

6. **Close = the harness defines done.** Closing appends one proof line per
   DoD clause: named check + observed result, re-observed from fresh state
   (commands rerun; artifacts and external verdicts re-read — actually
   looked at, not the caption), or a named owner handoff with a resume
   predicate. A clause unaccounted means the plan does not close. Close's
   commit folds one lesson into standing knowledge (or `LESSON none — why`)
   and moves the milestone's receipts to the archive. When every agent-side
   row is proven and the DoD sits owner-gated with a handoff, the plan
   closes on the agent side and the successor goal is minted — never hang
   waiting on a human click.

7. **The milestone.** A `###` heading over 2–7 rows plus exactly one `(DoD)`
   row, which flips only after every sibling. The current milestone is
   derived at read time — never stamped. Any structural edit lands with a
   paired Progress line naming its trigger.

8. **Entity + board.** Every plan carries `- Entity:` (optionally
   `- Priority: 1-5`). An entity is a grep result, not a file. The board is
   read-only, derives everything at read time, renders the lint verdict on
   every card, and shows an unparseable plan as a red card — never
   best-effort counts.

## Folded behavior — one sentence each

- Steering is one multiple-choice prompt with a default — at session start,
  on a DoD flip, or when asked, never per checkpoint; default-if-silent is
  the highest-Priority entity's ready row, logged as one Progress line.
- Discovered work becomes a new row in the same cycle; its paired Progress
  line names the row it came from.
- Before honoring a posture flip, run `shadow lint`, then ask of the diff:
  does any row duplicate another, and can each proof refuse bad work?
- Transfer the lesson, never the work: a pattern that generalizes becomes a
  skill or one Deferred row in the sibling's own plan.
- The loop skill is `/<entity>-loop` by derivation; write `- Loop:` only
  when the real loop differs.
- Row IDs are four base36 chars, unique in the plan, checked by lint; on
  collision, re-mint.

## Appendix

Same-plan concurrency is unsupported until `shadow accept` is the only flip
path; hash-mint hardening, M-ids, CLAIM bookkeeping, and mass thresholds
sleep as deferred items in the design spec, each with a named wake trigger.
