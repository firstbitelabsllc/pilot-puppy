# Installation

Requirements: Git, Bash, Python 3.10+, and one supported native coding host.

```bash
git clone https://github.com/firstbitelabsllc/shadow.git
cd shadow
npm install -g .
shadow doctor
```

Optional skill mounts:

```bash
ln -sfn "$(pwd)" "$HOME/.claude/skills/shadow"
ln -sfn "$(pwd)" "$HOME/.agents/skills/shadow"
ln -sfn "$(pwd)" "$HOME/.cursor/skills/shadow"
```

The mount points at the same repository; it does not copy state or credentials.
