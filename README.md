# Kitty AI Multiplexer

Smart tab management for AI coding assistants (Claude Code, Codex, Gemini, etc.) in Kitty.

No background daemon — runs natively inside Kitty via the watcher API.

## Features

- **Automatic tab coloring** — green for waiting, orange for running, even when the tab is inactive
- **Jump-to-tab keybindings** — hop to the next tab that needs your input
- **Works across transport layers** — local shells, SSH sessions, and tmux over SSH

## How It Works

1. AI tool hooks emit an escape sequence: `\033]1337;SetUserVar=ai_cli_state=<base64>\007`
2. Kitty's watcher (`ai_monitor.py`) fires `on_set_user_var` and sets tab color
3. A custom kitten (`ai_jump.py`) reads `window.user_vars` to find tabs by state

No polling, no sockets, no separate process.

## Supported Setups

The watcher only cares that `ai_cli_state` reaches Kitty. That means the same install works for:

| Environment | Claude Code | Codex | Notes |
|---|---|---|---|
| Local shell in Kitty | Yes | Yes | Run the CLI directly in a Kitty tab |
| SSH session in Kitty | Yes | Yes | Run the CLI on the remote host inside a Kitty SSH session |
| tmux inside SSH inside Kitty | Yes | Yes | Supported by the tmux-aware hook snippets in `hooks/*.json` |

For tmux sessions, the provided hooks detect `TMUX` and emit the escape sequence through tmux passthrough so it still reaches Kitty.

## Install

```bash
./INSTALL.sh
```

This copies the watcher and kitten to `~/.config/kitty/` and appends config to `kitty.conf`.

Then restart Kitty (or press `ctrl+shift+f5` to reload config).

## Hook Setup

Merge the appropriate hook config into your AI tool's settings:

**Claude Code** (`~/.claude/settings.json`) — see `hooks/claude-code.json`

**Codex** (`~/.codex/hooks.json`) — see `hooks/codex.json`

The hooks use Kitty's native `SetUserVar` escape sequence support and already handle both plain terminals and tmux sessions.

## Usage Patterns

Open each assistant in its own Kitty tab. Any of these layouts are supported.

### Local

```bash
# Tab 1
claude

# Tab 2
codex
```

### SSH

```bash
# Tab 1
ssh devbox
claude

# Tab 2
ssh gpu-box
codex
```

### tmux + SSH

```bash
# Tab 1
ssh devbox
tmux new -A -s ai
claude

# Tab 2
ssh gpu-box
tmux new -A -s ai
codex
```

As long as the CLI is attached to the controlling TTY and your hooks are installed on the machine where the CLI runs, Kitty will receive the state updates.

## Keybindings

Added to `kitty.conf` by the installer:

| Shortcut | Action |
|---|---|
| `Cmd+Shift+N` | Jump to next **waiting** tab |
| `Cmd+Shift+R` | Jump to next **running** tab |

## State Model

This project does not inspect terminal output and does not do pattern matching.

It only reacts to explicit `ai_cli_state` values emitted by your hooks:

- `running` — work is in progress
- `waiting` — the tool is blocked on your input

If you emit any other value, the watcher clears the configured tab color.

## Remote Setup Notes

- If you run Claude or Codex over SSH, install the relevant hook config on the remote machine too.
- If you use tmux remotely, no separate tmux config is required for this project; the provided hook commands already branch on `TMUX`.
- If a tab does not update, test the raw escape sequence in that exact shell session and make sure it is writing to `/dev/tty`.

## Configuration

Edit the top of `~/.config/kitty/ai_monitor.py`:

```python
STATE_COLORS = {
    "waiting": "#00c800",   # Green
    "running": "#ffb400",   # Orange
}
```

## Requirements

- Kitty 0.30.0+ (for `on_set_user_var` watcher support)

## License

MIT
