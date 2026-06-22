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

# Remote host installed into kitty.conf. Keep this independent from the current
# shell's KITTY_AGENT_REMOTE because Kitty exports that env var to child shells;
# reusing it would preserve stale installs forever.
REMOTE_HOST="larry@reverse-proxy"
echo "Using remote: $REMOTE_HOST"

if [ "$(uname -s)" = "Darwin" ]; then
    KAM_MOD="cmd+shift"
else
    KAM_MOD="kitty_mod"
fi
echo "Using shortcut modifier: $KAM_MOD"

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
# Remote host for agent_* kittens. Edit and reload Kitty to change, or
# re-run INSTALL.sh to be prompted again.
env KITTY_AGENT_REMOTE=$REMOTE_HOST

# Status layer: AI CLI state → tab color
watcher $KITTY_CONF_DIR/ai_monitor.py

# Flat: highest-frequency action — jump to next tab waiting for input.
map $KAM_MOD+n kitten $KITTY_CONF_DIR/ai_jump.py waiting

# Agent leader chord: every lifecycle verb under one mnemonic root.
#   $KAM_MOD+a then …
#     c  create   — prompt for name, spawn remote tmux + local tab
#     a  attach   — connect_all: rehydrate one tab per live remote session
#     l  list     — picker over remote sessions, attach selection
#     k  kill     — picker + confirm, force-kill named remote session
#     r  rename   — rename current tab + matching remote session
#     n  next-waiting (alternate access)
#     p  next-running
map $KAM_MOD+a>c kitten $KITTY_CONF_DIR/agent_create.py
map $KAM_MOD+a>a kitten $KITTY_CONF_DIR/agent_connect_all.py
map $KAM_MOD+a>l kitten $KITTY_CONF_DIR/agent_pick.py
map $KAM_MOD+a>k kitten $KITTY_CONF_DIR/agent_end.py
map $KAM_MOD+a>r kitten $KITTY_CONF_DIR/agent_rename.py
map $KAM_MOD+a>n kitten $KITTY_CONF_DIR/ai_jump.py waiting
map $KAM_MOD+a>p kitten $KITTY_CONF_DIR/ai_jump.py running
$MARK_END
EOF
echo "Updated managed block in $KITTY_CONF"

cat <<EOF

Next steps:
  1. Restart Kitty (or ctrl+shift+f5 to reload config).
     Kitty will export KITTY_AGENT_REMOTE=$REMOTE_HOST to all kittens.
  2. Install AI tool hooks (see hooks/claude-code.json and hooks/codex.json).

Shortcuts:
  $KAM_MOD+n        jump to next waiting tab
  $KAM_MOD+a c      create a new agent (prompts for name)
  $KAM_MOD+a a      connect to all remote sessions (rehydrate)
  $KAM_MOD+a l      pick a session to attach
  $KAM_MOD+a k      pick a session to kill (with confirm)
  $KAM_MOD+a r      rename current tab + remote session

On macOS, install uses cmd+shift for this project. Elsewhere, it uses kitty_mod.
EOF
