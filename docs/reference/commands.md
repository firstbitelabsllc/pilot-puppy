# Commands

| Command | Purpose |
|---|---|
| `pilot-puppy init --here` | Create `PLAN.md` without overwriting one. |
| `pilot-puppy status --root PATH` | Read current plan rows. |
| `pilot-puppy browse --root PATH` | Start the loopback briefing UI. |
| `pilot-puppy checkpoint … --proof TEXT` | Update one exact row and atomically write one receipt. |
| `pilot-puppy roster init\|show` | Create or show a local generic work-role roster. |
| `pilot-puppy host probe --host HOST` | Check a native host without using it. |
| `pilot-puppy host run …` | Run one sealed task in one clean worktree. |
| `pilot-puppy doctor` | Check installation, skill mounts, and native hosts. |

Run `pilot-puppy help <command>` for exact flags.

The roster command is local setup/display only. It does not select a provider
or model, start a coding host, dispatch work, or write project evidence. There
is no `route` command yet.
