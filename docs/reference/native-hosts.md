# Native hosts

Shadow supports `codex`, `claude-code`, and `cursor`. You choose the host
directly: `shadow host run --host <name>` is the complete sealed path. There
is no roster, route, or seat layer in front of it, and Shadow cannot verify
or guarantee the provider model or billing tier inside a host.

Every run requires one exact clean Git worktree, one frozen task file, one task
ID, and one or more exact allowed paths. Scope escape, missing receipt,
non-zero exit, timeout, or missing passing tests fails closed. The returned
claim stays `accepted_by_lead: false` until a person or lead agent reproduces
the proof. Shadow supplies the receipt contract to the host and records
the frozen task's SHA-256, not its prompt or provider output.

Shadow passes no model or account selector and records none. Which provider,
model, or account a host uses is that host CLI's own business, configured in
the host's own config (for example the Codex CLI config file, Claude Code
settings, or Cursor settings).

## Seat maps live outside Shadow

If your fleet wants one human-readable map of which host runs which model,
keep it outside Shadow — next to your other operator configuration, never in
a plan, brief, status output, or receipt. Have an agent author and regenerate
it from the live host configs; treat hand edits as drift. A worked shape is
in [`examples/seats.example.yaml`](../../examples/seats.example.yaml). Shadow
never reads it: the host CLI configs stay authoritative, and the map is a
mirror for people.
