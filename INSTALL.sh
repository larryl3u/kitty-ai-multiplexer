#!/bin/bash
# Installation script for Kitty AI CLI Monitor

set -e

KITTY_CONF_DIR="$HOME/.config/kitty"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing Kitty AI CLI Monitor..."

if ! command -v kitty &>/dev/null; then
    echo "Error: kitty not found. Please install Kitty terminal first."
    exit 1
fi

mkdir -p "$KITTY_CONF_DIR"

cp "$SCRIPT_DIR/ai_monitor.py" "$KITTY_CONF_DIR/"
cp "$SCRIPT_DIR/ai_jump.py" "$KITTY_CONF_DIR/"

echo "Files installed to $KITTY_CONF_DIR"
echo ""

# Check if kitty.conf already has the watcher line
if grep -q "ai_monitor.py" "$KITTY_CONF_DIR/kitty.conf" 2>/dev/null; then
    echo "kitty.conf already references ai_monitor.py — skipping config update."
else
    echo "" >> "$KITTY_CONF_DIR/kitty.conf"
    echo "# AI CLI Monitor - watcher and keybindings" >> "$KITTY_CONF_DIR/kitty.conf"
    echo "watcher $KITTY_CONF_DIR/ai_monitor.py" >> "$KITTY_CONF_DIR/kitty.conf"
    echo "map cmd+shift+n kitten $KITTY_CONF_DIR/ai_jump.py waiting" >> "$KITTY_CONF_DIR/kitty.conf"
    echo "map cmd+shift+r kitten $KITTY_CONF_DIR/ai_jump.py running" >> "$KITTY_CONF_DIR/kitty.conf"
    echo "Added watcher and keybindings to kitty.conf"
fi

echo ""
echo "Next steps:"
echo ""
echo "1. Restart Kitty (or reload config with ctrl+shift+f5)"
echo ""
echo "2. Configure hooks on your AI tools."
echo ""
echo "   Claude Code (~/.claude/settings.json):"
echo "   Merge the contents of hooks/claude-code.json"
echo ""
echo "   Codex (~/.codex/hooks.json):"
echo "   Use hooks/codex.json"
echo ""
echo "3. Keybindings (already added to kitty.conf):"
echo "   Cmd+Shift+N  →  jump to next 'waiting' tab"
echo "   Cmd+Shift+R  →  jump to next 'running' tab"
