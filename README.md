# Kitty AI Multiplexer

Two complementary layers, both 100% client-side in Kitty:

- **Status layer** — AI tools (Claude Code, Codex, …) emit state via hooks; Kitty colors the tab and lets you jump to whichever tab needs your attention.
- **Lifecycle layer** — `create / connect_all / pick / end / rename` kittens that manage isolated agent workspaces as remote tmux sessions. The remote is a dumb session store; every Kitty client brings the smarts.

No daemon, no protocol, no orchestrator process. Just Kitty + tmux + ssh.

## Architecture

```
┌────────────────────────────┐         ┌────────────────────────────┐
│  Local Kitty (each client) │         │  Remote machine            │
│  ──────────────────────────│         │  ──────────────────────────│
│  ai_monitor.py  (watcher)  │         │                            │
│  ai_jump.py     (kitten)   │         │   tmux session "planner"   │
│  agent_*.py     (kittens)  │  ssh ── │     ↳ claude               │
│                            │         │   tmux session "refactor"  │
│  Tab title = session name  │         │     ↳ claude               │
└────────────────────────────┘         └────────────────────────────┘
```

- Agent sessions live in tmux on the remote (per-agent session). Their survival is independent of any client.
- Every Kitty client is a thin viewer that maps `tmux ls` ↔ Kitty tabs.
- Recoverability: lose a client → next client runs the connect_all shortcut and is back where you were. Agents never noticed.
- Cross-platform: install chooses the platform-appropriate shortcut modifier.

## Install

```bash
./INSTALL.sh
```

Sets your remote (optional but typical):

```bash
export KITTY_AGENT_REMOTE=larry@reverse-proxy   # in your shell rc
# or edit ~/.config/kitty/agent_config.py
```

Restart Kitty (or `ctrl+shift+f5`).

For per-tool AI hooks, see `hooks/claude-code.json` and `hooks/codex.json`.

## Shortcuts

On macOS, install maps this project to `cmd+shift`. Elsewhere, install uses
`kitty_mod` (Kitty's configurable modifier, usually `ctrl+shift`).

### Flat — highest frequency

| Shortcut | Action |
|---|---|
| `cmd+shift+n` on macOS, `kitty_mod+n` elsewhere | Jump to next tab in `waiting` state |

### Leader chord — `cmd+shift+a` on macOS, `kitty_mod+a` elsewhere, then…

| Key | Verb | Behavior |
|---|---|---|
| `c` | **create** | Prompt for name, spawn remote `tmux new -A -s <name> claude`, open a Kitty tab attached to it |
| `a` | **connect_all** | For every live remote session not already a tab, open a tab attached to it |
| `l` | **list / pick** | Numbered picker over `tmux ls`; selecting attaches in a new tab (or focuses an existing one) |
| `k` | **kill** | Picker + confirm → `tmux kill-session -t <name>` on the remote |
| `r` | **rename** | Rename the current tab and the matching remote session together |
| `n` | jump waiting | Alternate access to next waiting |
| `p` | jump running | Jump to next tab in `running` state |

### Ending an agent (normal path)

Just exit it from inside — type `exit` or `Ctrl+D` in the agent's tab. The tmux session dies, the ssh drops, the tab closes. No shortcut needed; the kill shortcut is reserved for the forced case when you can't get into the session.

## Status Layer (existing)

`ai_monitor.py` reacts to Kitty's `SetUserVar` escape sequence support:

```
\033]1337;SetUserVar=ai_cli_state=<base64>\007
```

The provided hooks emit this for `running` / `waiting` / `done` and detect `TMUX` so the sequence passes through tmux to Kitty. Colors:

```python
STATE_COLORS = {
    "waiting": "#00c800",   # Green  — needs input
    "running": "#ffb400",   # Orange — working
}
```

Edit at the top of `~/.config/kitty/ai_monitor.py`.

## Lifecycle Layer Files

| File | Role |
|---|---|
| `agent_config.py` | `REMOTE_HOST`, default agent command. Env-var overridable. |
| `agent_common.py` | Shared helpers: ssh, tmux ls, tab→session mapping, tab launcher. |
| `agent_create.py` | Prompt → spawn + tab. |
| `agent_connect_all.py` | Diff `tmux ls` against current tabs, open the missing ones. |
| `agent_pick.py` | Picker → attach. |
| `agent_end.py` | Picker + confirm → kill. |
| `agent_rename.py` | Rename tab + remote session in lockstep. |

## Scope

This is a **personal workspace manager**, not a multi-agent runtime:

- Each agent is isolated. No cross-session reads, writes, or messaging built in.
- The human is the coordinator. If you want agents to talk to each other autonomously, build that on the Claude Agent SDK; this layer is just where you watch it run.

## Requirements

- Kitty 0.30.0+ (`on_set_user_var` watcher + `kitty @` remote control).
- `tmux` on the remote.
- SSH key auth to the remote.

## License

MIT
