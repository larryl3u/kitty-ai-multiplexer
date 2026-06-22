"""
Shared helpers for agent_* kittens.

The remote is the single source of truth (tmux ls). Kitty tabs are projections.
All helpers either query the remote or shape local Kitty state via the boss
object made available to result_handler.
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_config import REMOTE_HOST, AGENT_COMMAND  # noqa: E402


def ssh(*remote_argv, capture=True, check=False):
    """Fire-and-forget ssh for remote tmux queries."""
    argv = ["ssh", "-o", "BatchMode=yes", REMOTE_HOST, *remote_argv]
    if capture:
        return subprocess.run(argv, capture_output=True, text=True, check=check)
    return subprocess.run(argv, check=check)


def list_remote_sessions():
    """Live session names on the remote. Empty list on any error."""
    r = ssh("tmux", "ls", "-F", "#{session_name}")
    if r.returncode != 0:
        return []
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]


def kitty_tabs_by_title(boss):
    """{tab_title: tab} across all OS windows in this Kitty instance."""
    out = {}
    for tm in getattr(boss, "all_tab_managers", ()) or ():
        for tab in tm:
            title = getattr(tab, "name", "") or getattr(tab, "title", "") or ""
            if title:
                out[title] = tab
    return out


def boss_rc(boss, *argv):
    """Dispatch a remote-control command through the running boss. Avoids the
    socket round-trip and works without `allow_remote_control` enabled."""
    return boss.call_remote_control(None, tuple(argv))


def launch_agent_tab(boss, name, command=None):
    """Open a Kitty tab attached to a remote tmux session (creating it if
    needed). Routes through kitten ssh so the existing AI state hooks work."""
    cmd = command or AGENT_COMMAND
    remote_cmd = "tmux new -A -s {n} {c}".format(n=shquote(name), c=cmd)
    boss_rc(
        boss,
        "launch",
        "--type=tab",
        "--tab-title=" + name,
        "kitten",
        "ssh",
        REMOTE_HOST,
        "--",
        "sh",
        "-lc",
        remote_cmd,
    )


def shquote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"
