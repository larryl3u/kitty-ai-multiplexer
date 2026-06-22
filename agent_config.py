"""
Shared config for agent lifecycle kittens.

Override via env vars or edit values here. Same file shipped to every Kitty
client; pointing at a different remote = changing one env var.
"""

import os

# SSH target. Anything `kitten ssh` accepts (Host alias from ~/.ssh/config,
# user@host, Tailscale magicDNS name, etc.).
REMOTE_HOST = os.environ.get("KITTY_AGENT_REMOTE", "larry@reverse-proxy")

# Optional command run inside each new tmux session. Empty means start the
# remote user's default shell and let the user choose codex/claude/manually.
AGENT_COMMAND = os.environ.get("KITTY_AGENT_CMD", "")
