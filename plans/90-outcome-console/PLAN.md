# 90 — Outcome Contract Plan

**Parent authority:** [`../../PLAN.md`](../../PLAN.md)
**Status:** contract retained; live-loop reuse is active elsewhere; no
standalone GUI implementation leaf is active
**Internal name:** “Outcome Console” names this research and contract. It is not
a second product, a public feature name, or a Vidux rename.

## Outcome

Tell 90 what outcome you want once. It keeps that outcome alive across
conversations and workers, handles routine choices, asks only when you are
genuinely needed, and shows proof—or honest non-delivery—at the end.

That is the user-facing narrative. “Vidux,” “Outcome Console,” “true vibe code,”
plans, providers, recipes, and workers are architecture or internal vocabulary,
not concepts the person must learn.

## Reuse Decision

Reuse the proved Outcome / Ask / Steer contract inside 90's live request loop.
Do not start a standalone Vidux console or project-management surface.

The opportunity is not “chat that can write software”; capable products already
offer that. The wedge is one durable Outcome that survives chats and workers,
ordinary execution without approval theater, a Steer that replaces stale
direction in place, and an Ask only for a genuine fork. The person sees proof
without managing the machinery.

Conversation is the first surface. A visual Current Outcome view becomes
eligible only after live-loop dogfood identifies a concrete comprehension or
recovery problem that conversation cannot solve. If built, it is a read-only
projection of the same authority, not another state store.

Stop this direction if dogfood shows that people primarily want a code editor,
agent selector, editable prompt queue, project manager, or plan-approval screen.
Those are crowded products and would pull Vidux away from its
plan/proof/resume strength.

## Market Evidence

This is an initial official-documentation snapshot, not a market-size claim.

- [Lovable Agent mode](https://docs.lovable.dev/features/agent-mode) makes
  agent steps, files, diffs, queued messages, stop, and undo visible.
- [Lovable Plan mode](https://docs.lovable.dev/features/plan-mode) asks the user
  to review and approve an editable plan before implementation.
- [Replit Agent](https://docs.replit.com/features/agent/overview) already
  promises plain-language app creation with no coding required, while
  [Plan mode](https://docs.replit.com/features/agent/plan-mode) and the
  [task board](https://docs.replit.com/features/agent/task-board) expose plan
  review and task management.
- [Replit checkpoints](https://docs.replit.com/features/version-control/checkpoints-and-rollbacks)
  expose change history and rollback as explicit controls.
- [OpenHands conversation goals](https://docs.openhands.dev/sdk/guides/agent-server/conversation-goals)
  keep a goal on the same conversation and support progress plus stop/resume.
- [OpenHands security](https://docs.openhands.dev/sdk/guides/security) exposes
  confirmation policy and risk analysis as execution controls.

These products validate goals, progress, interruption, and safety controls.
They do not by themselves validate 90’s proposed differentiation. The testable
bet is that a non-coder values less operational interface: one Outcome, one
exceptional Ask, one way to Steer, and proof when finished.

## Product Contract

### What enters

- A plain-language **Outcome**, **question**, or **Steer** by text today and by
  voice when the same contract has a safe typed fallback.
- Optional current project or plan context. The person should not need to name
  a repository when the active context already makes it clear.

### What comes back

- A short, grounded brief: what is happening, what is blocked, what happens
  next, and the one decision that genuinely needs the person.
- An explicit Steer lifecycle: **received**, **applied**, **working**,
  **blocked**, **finished with proof**, or **not delivered**.
- An openable proof or plan reference when someone wants detail; never a forced
  code, terminal, provider, or fleet dashboard.

### What stays underneath

- 90 owns the conversational product experience and semantic policy.
- The native coding host or Pilot owns execution, provider selection, worker
  routing, foldback, and lead acceptance.
- Vidux persists plan authority, lifecycle projections, proof references, and
  resume pointers. It does not execute or decide acceptance.
- Ledger carries bounded append-only receipts; it is evidence, not authority.
- A conversation is a reference to an independent context, never a claim that
  every chat shares memory or that raw transcripts are the source of truth.
- One Outcome may coordinate many project and worker threads, but those threads
  remain independently owned and do not become competing user-visible queues.

## Smallest Useful Surface

The default response—spoken, typed, or eventually visual—contains one calm
Current Outcome:

1. **Outcome** — one plain sentence naming the result.
2. **State** — **working now**, **needs you**, or **finished with proof**.
3. **Current move** — one sentence describing what is actually happening next.
4. **Steer** — one natural-language way to update this same Outcome.
5. **Ask** — absent by default; when present, one real fork with concise options
   and consequences.
6. **Proof** — a compact receipt or link, opened only when wanted.

There is no default project picker, project list, mode switch, prompt queue,
routine approval button, model picker, worker list, terminal, file tree, or
token dashboard. Project identity appears only when ambiguity requires it.
Stop and resume are lifecycle actions, not an invitation to manage a fleet.

An Ask is a decision interrupt, never a disguised “run” button. A Steer is not
another queued prompt: once applied, stale direction is visibly superseded and
must not continue executing.

## Semantic Contract

The provider-neutral boundary is deliberately small:

- **Outcome:** stable identity, plain-language result, current state, current
  move, optional open Ask, and zero or more proof references.
- **Steer:** stable identity, Outcome identity, bounded instruction summary,
  lifecycle state, and acknowledgment/proof reference.
- **Ask:** stable identity, one allowed fork category, one concise question,
  bounded options with consequences, and open/answered/superseded state.
- **Proof reference:** truthful type, location, verification summary, and
  delivered/not-delivered state. It is evidence, not a second plan.

Raw transcripts, provider prompts, secrets, and untrusted retrieved text never
become this state. The coding host may derive a bounded semantic summary, but
the durable plan and audit receipt remain the authority.

## Deferred Vidux Kernel Work

Recipe registries and plan-tree/worktree hygiene remain plausible Vidux kernel
work, but they are not part of the active 90 product slice and do not gate it.
Each needs its own parent-plan row and proof boundary before implementation.
Do not smuggle either into a Current Outcome view.

## Dogfood Gate

First dogfood the reused contract in 90's real request loop across one build,
one bug-fix, and one release scenario. A scenario passes only when the person
can:

- state the Outcome without naming a repository, provider, or implementation;
- explain the current state and whether the system needs them;
- submit one Steer and see stale direction stop;
- receive zero Asks for routine work and exactly one Ask for a deliberately
  seeded genuine fork; and
- identify the final proof or honest non-delivery state without opening code,
  a terminal, a plan editor, or a worker dashboard.

Record confusion and recovery, not only task completion. A visual projection is
triggered only if the lifecycle works but the person still cannot reliably
understand state, the outstanding Ask, or final proof. The hypothesis is
falsified if a human translator is repeatedly needed, Steers behave like queued
prompts, routine work produces approval theater, or proof is not trusted.

## Ordered Work

- [completed] Record the outcome-first direction, product boundary, market
  evidence, smallest useful surface, and bounded falsification gate.
- [completed] Reconcile this feature with the proved 90 semantic engine and
  assign execution, persistence, acceptance, and evidence to one layer each.
- [in_progress] Reuse the existing `outcome` / `ask` / `steer` engine in 90's
  live request loop. This repo records the public contract; it does not claim
  that downstream implementation or its proof.
- [pending] Dogfood the live loop and record the exact places where status,
  steering, Ask frequency, recovery, or proof trust fails.
- [pending] Only if dogfood proves a visual comprehension gap, open one bounded
  leaf for a read-only Current Outcome projection. Do not add project, agent,
  model, prompt-queue, file, terminal, or second-state-store controls.

## Current Proof

- Official Lovable, Replit, and OpenHands documentation was indexed and
  reviewed through Nia; the links above point to the primary pages used.
- Taste reports zero findings; the Vidux public-ready gate passes; all 22
  JavaScript and 369 Python tests pass.
- Publish packet `evt_55d002e0` records this two-file, docs-only product-plan
  handoff. No GUI, live execution loop, microphone path, or product-name change
  is claimed.
- The downstream typed lifecycle has local deterministic proof, but that does
  not prove a live request loop or justify a separate GUI.

## Non-goals

- A marketplace for models, tools, or agent personalities.
- A configurable clone of a coding-agent harness.
- A second ledger, raw-transcript archive, or false shared-memory system.
- Voice-only operation without a typed, inspectable fallback.
- Automatic destructive cleanup, publishing, spending, or external messaging.

## Resume Here

Resume the existing 90 implementation authority at its live request-loop
boundary. Return here only after dogfood supplies a concrete status, recovery,
or proof-comprehension failure. Keep routing and execution in the coding host;
do not rename Vidux, start a standalone console, or expand into an IDE.
