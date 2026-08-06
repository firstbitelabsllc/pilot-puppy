# Commands

| Command | Purpose |
|---|---|
| `shadow init --here` | Create `PLAN.md` without overwriting one. |
| `shadow status --root PATH` | Read current plan rows. |
| `shadow browse --root PATH` | Start the loopback briefing UI. |
| `shadow checkpoint … --proof TEXT` | Update one exact row and atomically write one receipt. |
| `shadow roster init\|show\|prefer` | Create, show, or locally prioritize a declared generic work-role slot. |
| `shadow seat init\|show\|set` | Configure one owner-local model/profile selector for an existing native slot. |
| `shadow route …` | Explain one explicit generic role/native-host choice without launching it. |
| `shadow accept --row ~hash --repo PATH` | Rerun one row's `cmd` proof in a clean detached checkout; on success flip the row with its paired PROOF line in one commit — the only code path that flips a row. |
| `shadow host probe --host HOST` | Check a native host without using it. |
| `shadow host run …` | Run one sealed task in one clean worktree. |
| `shadow doctor` | Check installation, skill mounts, and native hosts. |

Run `shadow help <command>` for exact flags.

The roster command is local setup/display only. `route` selects only a declared
generic role and native-host surface, then prints the choice and stops. The
optional `seat` command is a separate owner-local overlay: it can attach one
safe native model selector to an already-declared slot, or a Codex profile to a
Codex slot. It never changes a route and takes effect only with `host run
--use-seat` plus a ready sealed route. These commands do not discover providers,
accounts, quota, prices, or models; start a host automatically; dispatch work;
or create a queue. See [foreground routing](routing.md) and
[native hosts](native-hosts.md).

