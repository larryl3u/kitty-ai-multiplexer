#!/bin/bash
# Installation script for iTerm2 AI Multiplexer

set -e

ITERM2_SCRIPTS_DIR="$HOME/Library/Application Support/iTerm2/Scripts/AutoLaunch"

echo "🚀 Installing iTerm2 AI Multiplexer..."

# Check if on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script only works on macOS with iTerm2"
    exit 1
fi

# Check if iTerm2 is installed
if ! [ -d "/Applications/iTerm.app" ]; then
    echo "❌ Error: iTerm2 not found. Please install iTerm2 first."
    echo "   Download from: https://iterm2.com"
    exit 1
fi

# Create scripts directory if it doesn't exist
mkdir -p "$ITERM2_SCRIPTS_DIR"

# Copy files
echo "📦 Copying files to $ITERM2_SCRIPTS_DIR..."
cp ai_monitor.py "$ITERM2_SCRIPTS_DIR/"
cp config.py "$ITERM2_SCRIPTS_DIR/"

echo "✅ Files installed successfully!"
echo ""
echo "Next steps:"
echo "1. Open iTerm2"
echo "2. Go to Scripts → Manage → Install Python Runtime (if not already installed)"
echo "3. Restart iTerm2"
echo "4. Set up keybinding:"
echo "   - Settings → Keys → Key Bindings → +"
echo "   - Keyboard shortcut: ⌘⇧N (or your choice)"
echo "   - Action: Invoke Script Function"
echo "   - Function call: jump_to_waiting"
echo ""
echo "5. Start using AI tools in different tabs and watch them auto-color!"
echo ""
echo "📖 See README.md for full documentation"
