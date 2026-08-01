# Durable synthetic plan

## Purpose

Exercise durable plan state without a provider or a remote service.

## Operator Brief

- Outcome: Preserve a resumable local plan state.
- Status: active
- Priority: 50

## Tasks

- [in_progress] capture the durable checkpoint
- [pending] inspect the next local move

## Progress

- [2026-08-01] Seeded durable state for an offline benchmark.

## Proof

The benchmark inserts a synthetic provider token marker at runtime. The
browser must redact it before it crosses the JSON or file boundary.

API_TOKEN=__BENCHMARK_SECRET__
