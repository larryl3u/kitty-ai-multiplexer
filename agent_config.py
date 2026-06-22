"""
Shared config for agent lifecycle kittens.

Override via env vars or edit values here. Same file shipped to every Kitty
client; pointing at a different remote = changing one env var.
"""

import os

# SSH target. Anything `kitten ssh` accepts (Host alias from ~/.ssh/config,
# user@host, Tailscale magicDNS name, etc.).
REMOTE_HOST = os.environ.get("KITTY_AGENT_REMOTE", "devbox")

# Command run inside each new tmux session. Override per-tab by passing a
# different command to agent_create; this is just the default.
AGENT_COMMAND = os.environ.get("KITTY_AGENT_CMD", "claude")
