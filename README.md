# Kitty AI Multiplexer

Smart tab management for AI coding assistants (Claude Code, Codex, Gemini, etc.) in Kitty.

No background daemon — runs natively inside Kitty via the watcher API.

## Features

- **Automatic tab coloring** — green for waiting, orange for running, even when the tab is inactive
- **Tab title annotations** — `[waiting]` / `[running]` appended to titles
- **Jump-to-tab keybindings** — hop to the next tab that needs your input

## How It Works

1. AI tool hooks emit an escape sequence: `\033]1337;SetUserVar=ai_cli_state=<base64>\007`
2. Kitty's watcher (`ai_monitor.py`) fires `on_set_user_var` and sets tab color/title
3. A custom kitten (`ai_jump.py`) reads `window.user_vars` to find tabs by state

No polling, no sockets, no separate process.

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

The hooks use Kitty's native `SetUserVar` escape sequence support.

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

If you emit any other value, the watcher clears the tab color and still appends that state to the title.

## Configuration

Edit the top of `~/.config/kitty/ai_monitor.py`:

```python
STATE_COLORS = {
    "waiting": 0x00C800,    # Green
    "running": 0xFFB400,    # Orange
}
SHOW_STATE_IN_TITLE = True
```

## Requirements

- Kitty 0.30.0+ (for `on_set_user_var` watcher support)

## License

MIT
