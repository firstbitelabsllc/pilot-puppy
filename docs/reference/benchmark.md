# Offline benchmark harness

Vidux ships a small, synthetic benchmark for its local plan/proof/resume
contract. It exercises the public browser and checkpoint surfaces against a
temporary fixture root, then checks the telemetry and redaction boundaries.

```bash
npm run benchmark
```

The runner is deliberately offline and provider-neutral. It does not start a
model, contact a remote service, read the home directory or a development
root, compare providers, or make a net-win claim. Its receipt measures only
the local product contract:

- health and plan discovery over sealed synthetic plans;
- deterministic priority and proof-present/missing states;
- `vidux checkpoint` → local Ledger round-trip and resumable handoff;
- secret redaction and path-escape rejection; and
- repeatability of a canonical metric projection.

`elapsed_ms` is informational. The canonical digest excludes temporary paths,
timestamps, claim IDs, and timing so two clean runs must produce the same
receipt. The fixtures contain no credentials; one safe marker is replaced with
a provider-shaped value only inside the temporary root so the redaction check
exercises a real boundary. The fixture manifest seals every file with a
SHA-256 and the receipt carries its content digest. The browser's own
proof-target states are asserted for both an available and a missing proof.

This harness is product-contract evidence, not an agent-driver benchmark. It
does not restore the retired provider/evaluator protocols and does not change
Vidux's dev-root browse model or its redaction battery.
