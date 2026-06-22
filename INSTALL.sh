#!/bin/bash
# Installation script for Kitty AI Multiplexer
#
# Installs:
#   ai_monitor.py / ai_jump.py        — status layer (tab colors + jump)
#   agent_*.py + agent_config.py      — lifecycle layer (create/connect/end)
#   keybindings + watcher in kitty.conf
#
# Re-running is safe: managed block in kitty.conf is replaced in place.

set -e

KITTY_CONF_DIR="$HOME/.config/kitty"
KITTY_CONF="$KITTY_CONF_DIR/kitty.conf"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

MARK_BEGIN="# >>> kitty-ai-multiplexer >>>"
MARK_END="# <<< kitty-ai-multiplexer <<<"

if ! command -v kitty &>/dev/null; then
    echo "Error: kitty not found. Install Kitty first." >&2
    exit 1
fi

mkdir -p "$KITTY_CONF_DIR"

for f in ai_monitor.py ai_jump.py \
         agent_config.py agent_common.py \
         agent_create.py agent_connect_all.py \
         agent_pick.py agent_end.py agent_rename.py; do
    cp "$SCRIPT_DIR/$f" "$KITTY_CONF_DIR/"
done
echo "Installed kittens to $KITTY_CONF_DIR"

touch "$KITTY_CONF"

# Strip any previous managed block, then append a fresh one.
if grep -qF "$MARK_BEGIN" "$KITTY_CONF"; then
    awk -v b="$MARK_BEGIN" -v e="$MARK_END" '
        $0 == b { skip = 1 }
        !skip   { print }
        $0 == e { skip = 0 }
    ' "$KITTY_CONF" > "$KITTY_CONF.tmp" && mv "$KITTY_CONF.tmp" "$KITTY_CONF"
fi

cat >> "$KITTY_CONF" <<EOF

$MARK_BEGIN
# Status layer: AI CLI state → tab color
watcher $KITTY_CONF_DIR/ai_monitor.py

# Flat: highest-frequency action — jump to next tab waiting for input.
# kitty_mod is Kitty's cross-platform modifier (ctrl+shift by default,
# remappable per-platform via 'kitty_mod' in kitty.conf).
map kitty_mod+n kitten $KITTY_CONF_DIR/ai_jump.py waiting

# Agent leader chord: every lifecycle verb under one mnemonic root.
#   kitty_mod+a then …
#     c  create   — prompt for name, spawn remote tmux + local tab
#     a  attach   — connect_all: rehydrate one tab per live remote session
#     l  list     — picker over remote sessions, attach selection
#     k  kill     — picker + confirm, force-kill named remote session
#     r  rename   — rename current tab + matching remote session
#     n  next-waiting (alternate access)
#     p  next-running
map kitty_mod+a>c kitten $KITTY_CONF_DIR/agent_create.py
map kitty_mod+a>a kitten $KITTY_CONF_DIR/agent_connect_all.py
map kitty_mod+a>l kitten $KITTY_CONF_DIR/agent_pick.py
map kitty_mod+a>k kitten $KITTY_CONF_DIR/agent_end.py
map kitty_mod+a>r kitten $KITTY_CONF_DIR/agent_rename.py
map kitty_mod+a>n kitten $KITTY_CONF_DIR/ai_jump.py waiting
map kitty_mod+a>p kitten $KITTY_CONF_DIR/ai_jump.py running
$MARK_END
EOF
echo "Updated managed block in $KITTY_CONF"

cat <<EOF

Next steps:
  1. Set the remote host (one of):
       export KITTY_AGENT_REMOTE=devbox      # in your shell rc
       # or edit $KITTY_CONF_DIR/agent_config.py
  2. Restart Kitty (or ctrl+shift+f5 to reload config).
  3. Install AI tool hooks (see hooks/claude-code.json and hooks/codex.json).

Shortcuts:
  kitty_mod+n        jump to next waiting tab
  kitty_mod+a c      create a new agent (prompts for name)
  kitty_mod+a a      connect to all remote sessions (rehydrate)
  kitty_mod+a l      pick a session to attach
  kitty_mod+a k      pick a session to kill (with confirm)
  kitty_mod+a r      rename current tab + remote session

kitty_mod defaults to ctrl+shift on Linux and is whatever you set on macOS.
EOF
