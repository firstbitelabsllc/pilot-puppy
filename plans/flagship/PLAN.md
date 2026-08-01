# Vidux flagship convergence plan

**Status:** in progress

**Parent authority:** [`../../PLAN.md`](../../PLAN.md)

This plan defines the future flagship product. It does not change the current
1.2.0 release contract until the ordered gates below are green.

## The decision

Keep **Vidux** as the public name and make it the calm local work conductor:

> State the outcome once. Vidux keeps the plan and proof. Pilot Puppy drives the
> work. Native Codex, Claude, or Cursor executes it. 90 lets you choose the
> next move from your phone or voice without staring at the machinery.

Do not create a new repository, rewrite the Vidux history, or replace the name
before a working successor exists. The name search found Wayline in live
navigation, communications, and property-management products, including active
marks; it is not a clean open-source identity. A later rename remains possible,
but it is not the product strategy.

The shipping shape is **one installable product with strict internal modules**,
not one fused mega-runtime and not a collection of competing products.

### Friendly product naming and distribution

The user-facing driver is now **Pilot Puppy**: a small, approachable right-hand
helper for people who want decisions and progress without learning agent
machinery. The public skill/command is `/pilot-puppy`; `/pilot` remains a
compatibility alias, and the existing `pilot.*` schemas and environment names
remain stable. This is a brand migration, not a history rewrite or a second
runtime.

The same product may later ship through three thin distribution surfaces:

1. a local skill/CLI for developers who want full custody;
2. optional ChatGPT, Claude, or Cursor wrappers that call the typed semantic
   API; and
3. a native iOS/iPad client for the same tailnet-only API.

Those wrappers are interfaces, not cloud executors. They never receive source,
credentials, raw transcripts, or a second plan store. A non-technical user can
discover Pilot Puppy through a hosted or marketplace surface without a GitHub
or npm workflow, while the Mac remains the execution and credential boundary.

## Roles (one sentence each)

| Surface | Owns | Must not own |
|---|---|---|
| **Vidux core** | `PLAN.md`, Outcome / Ask / Steer, proof references, resume, worktree and ownership contracts | provider choice, worker execution, credentials, cloud orchestration |
| **Pilot Puppy** | Leo's main right-hand driver: plan, split, dispatch, supervise, accept, and fold receipts start-to-finish | a second plan store, raw chat memory, silent provider decisions, user-facing fleet clutter |
| **Native host adapters** | The concrete Codex, Claude Code, and Cursor invocation and host-native lifecycle | changing the canonical plan without a receipt, exposing credentials to a remote client |
| **90** | Car/on-the-go UX: read concise status, speak one next move, present A/B/C, forward the selected Steer, round-robin ready outcomes | coding, provider routing, background observation, transcript storage, a second driver loop |
| **Ledger** | Append-only bounded activity and handoff evidence | priority, routing, acceptance, or a second authority |
| **Sidekick patterns** | Checkpoint, watchdog, retry, refutation, cold-review behaviors inside Pilot Puppy | a separate runtime or install choice |
| **Swarm patterns** | Task-shape recipes for solo, batched, or parallel bounded work inside Pilot Puppy | a universal cross-provider control plane |
| **MCO** | Optional transport or experiment behind a Pilot Puppy adapter if it proves useful | planner, router, authority, or product identity |
| **Telemetry** | Redacted completion/quality signals | raw prompts, transcripts, secrets, personal paths, or activity theater |
| **Native iOS/iPad app** | A typed remote client over the local semantic API | an execution host, credential vault, or cloud copy of the codebase |

Pilot Puppy is therefore the main coder/driver. 90 is the steering wheel and
dashboard. Vidux is the durable road map and evidence. They can ship together,
but their contracts stay testable independently.

## Why this survives vendor catch-up

The hosts are rapidly absorbing generic orchestration. Cursor now packages MCP,
skills, subagents, rules, and hooks; Codex is a command center for parallel
agents, worktrees, skills, and automations; and Claude is adding subagents,
background tasks, plugins, and long-running sessions. The flagship must not
compete with those execution surfaces.

The durable wedge is the part those vendor surfaces do not share:

1. **Cross-host continuity:** one provider-neutral Outcome and plan survives a
   move between Codex, Claude, and Cursor.
2. **Trustful completion:** a task is not finished because an agent spoke; the
   same outcome receives a terminal proof/acceptance receipt or an explicit
   non-delivery state.
3. **Local custody:** code, credentials, and execution remain on the user's
   Mac; remote clients see typed semantic state, not a cloud mirror of the
   machine.
4. **Human-scale control:** a non-coder sees one current move and one real
   choice, not a model picker, prompt queue, or worker dashboard.
5. **Long-running hygiene:** bounded child plans, ownership, retries, context
   compaction, stale-work detection, and cleanup are observable and reversible.

If dogfood shows that native hosts already deliver these five properties across
all three providers, Vidux should shrink rather than add an agent platform.

## Architecture

```text
                         typed Outcome / Ask / Steer
                                      ^
                                      |
        iPhone / iPad / Codex Voice  90 (A/B/C + concise status)
                                      |
                       local semantic API (tailnet only)
                                      |
       PLAN.md + proof + ownership  Vidux core
                                      ^
                                      |
         Pilot Puppy driver (one lifecycle, one acceptance owner)
                    /             |                \
          Codex adapter     Claude adapter      Cursor adapter
             native host       native host         native host
```

### Core state

Keep the existing provider-neutral Outcome / Ask / Steer schema and pair it
with the separate lifecycle receipt needed to prove:

`planned → dispatched → working → needs-you → proving → finished-with-proof`

Every transition carries an outcome id, plan revision, actor, timestamp, and
proof or honest failure reference. Raw provider messages never become durable
state. One execution leaf owns one worktree; parent progress derives from
terminal child receipts. The public receipt deliberately omits provider/model
fields; private adapters may retain those details in their own bounded evidence.

### Pilot Puppy lifecycle

Pilot Puppy's first flagship gate is one real, boring lifecycle:

`start → freeze packet/context → invoke one native host → resume or Steer →
prove → lead acceptance → fold back to PLAN.md → close or hand off`

The lifecycle must work through Codex, Claude Code, and Cursor adapters with the
same packet/receipt contract. A projection, model list, or empty provider
response is never a run receipt.

### Host adapters

Support exactly three first-party host adapters: Codex, Claude Code, and Cursor.
Each adapter is a thin translation layer for the host's current native hooks,
subagents, or task APIs. It reports capabilities and proof; it does not move
private credentials into Vidux or invent a shared provider API that the hosts do
not actually implement.

### 90 and mobile

90 consumes the same typed semantic API as the browser cockpit. Its first
multiple-choice loop is deliberately small:

1. read the current outcomes and readiness;
2. speak a concise status and offer at most three meaningful choices;
3. send the chosen Steer to Pilot Puppy;
4. confirm `received`, then later `applied`, `blocked`, or `finished-with-proof`;
5. move to the next ready outcome only after the current handoff is durable.

The native iOS/iPad app is a future client of this API, not a second runtime.
The Mac remains the executor and credential boundary. The app must work over a
tailnet-only connection using Tailscale Serve or an equivalent private route;
Funnel/public exposure is out of scope for the core product.

### Telemetry

Use OpenTelemetry as the vendor-neutral event shape. Langfuse is an optional,
self-hosted sink, not a runtime dependency. The default event contains only
bounded metadata such as outcome id, plan revision, provider/host, model label,
attempt, state, proof status, failure class, time-to-first-progress,
time-to-terminal, interventions, retries, and compactions. It excludes raw
prompts, transcripts, file contents, credentials, absolute paths, and personal
identifiers. Telemetry is off or local-only until a collector health check and a
redaction regression prove otherwise.

## Non-goals (keep the product simple)

- no new universal router or model marketplace;
- no cloud executor, hosted project database, or credential relay;
- no second plan/queue hidden behind 90, Ledger, MCO, or a mobile app;
- no support matrix beyond Codex, Claude, and Cursor in the first release;
- no background screen reading or raw transcript archive;
- no automatic merge, publish, payment, destructive action, or external message;
- no four-level recursive planning tree without an independent proof/revert
  boundary;
- no rebrand, repo split, or history rewrite before the successor is proven.

## Ordered work and gates

- [completed] **F0 — Contract freeze.** Re-read this plan from `origin/main`; pin the
  role map, state machine, public/private boundary, and compatibility aliases.
  Gate: `vidux.lifecycle.v1` schema, fixtures, deterministic validator, and
  negative privacy/transition tests describe the new lifecycle. The contract
  is additive; the existing `vidux.outcome.v1` document remains compatible.
- [ ] **F1 — Pilot Puppy driver.** Implement the truthful start-to-finish lifecycle
  behind `/pilot-puppy`, preserving `/pilot` and `/leo-flow` compatibility.
  Gate: the same small task produces a provider receipt, proof reference, acceptance, and PLAN
  foldback in Codex, Claude Code, and Cursor; projection-only runs fail closed.
- [ ] **F2 — Host adapters.** Add only the three adapters and capability
  probes. Gate: no adapter writes outside its assigned worktree; missing host,
  auth, or proof is an explicit blocked/non-delivery result.
- [ ] **F3 — 90 semantic client.** Remove the duplicate driver-loop contract
  from the 90 plan/skill and implement A/B/C status/Steer against the typed
  boundary. Gate: 90 cannot execute code or route providers; stale Steers are
  visibly superseded; no raw screen/chat text is persisted.
- [ ] **F4 — Local transport.** Serve the semantic API on loopback and a
  tailnet-only endpoint. Gate: local integration passes; a non-tailnet request
  is rejected; no Funnel/public listener or credential endpoint exists.
- [ ] **F5 — Telemetry.** Add redacted OpenTelemetry events and an optional
  Langfuse exporter. Gate: a local collector receives completion/failure spans,
  the redaction suite rejects content/path/secret leakage, and disabling the
  exporter leaves the product fully functional.
- [ ] **F6 — Native iOS/iPad client.** Build the smallest read/status/Ask/Steer
  client after F3/F4, not before. Gate: it can reconnect, show stale/offline
  state, send one typed Steer, and never needs source or provider credentials.
- [ ] **F7 — Stranger dogfood and release.** Run build, bug-fix, and release
  scenarios with a non-coder; verify current-state comprehension, one real Ask,
  superseding Steer, and trusted proof. Then run the existing package, browser,
  privacy, and exact-release gates. A rename is considered only after this row.

## Five questions we must answer before adding surface area

1. Does cross-host continuity materially beat simply using Codex, Claude, or
   Cursor alone for a non-coder?
2. Can one receipt contract survive the real differences among the three hosts,
   or are we hiding a permanently lossy abstraction?
3. Does a user trust a concise semantic brief when proof is one tap away, or do
   they need code/log detail on the default screen?
4. Is tailnet onboarding low-friction enough for iPhone/iPad use without making
   Vidux a networking product?
5. Do completion and failure metrics change product decisions, or are we merely
   measuring agent activity?

## Evidence to keep current

Keep these primary sources in the research receipt for each implementation row:

- Cursor changelog: plugins, subagents, hooks, and background-agent custody.
- OpenAI Codex app announcement and Codex plugin help: native parallel work,
  worktrees, skills, and packaged workflows.
- Anthropic Claude Code documentation: local host setup and provider boundary.
- Tailscale Serve and iOS installation documentation: tailnet-only local
  access and iPhone/iPad support.
- OpenTelemetry GenAI semantic conventions: provider/model event attributes.
- Langfuse observability and self-hosting documentation: optional local sink
  and masking behavior.

The public plan keeps source names rather than absolute URLs because the
repository's public-ready gate rejects unapproved external hosts. The research
receipt and release notes may carry the reviewed links separately.

## Progress

- 2026-08-01: Froze the additive `vidux.lifecycle.v1` receipt contract. It
  validates ordered state transitions and terminal proof references without
  embedding provider, model, prompt, transcript, credential, or machine-path
  data. F1 now owns the first real Pilot Puppy lifecycle.
- 2026-08-01: Chose **Pilot Puppy** as the approachable user-facing driver
  name. `/pilot` and `pilot.*` remain compatibility aliases; optional hosted
  wrappers are interface-only and do not move execution or credentials off the
  user's Mac.
