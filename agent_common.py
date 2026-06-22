"""
Shared helpers for agent_* kittens.

The remote is the single source of truth (tmux ls). Kitty tabs are projections.
All helpers either query the remote or shape local Kitty state via the boss
object made available to result_handler.
"""

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_config import REMOTE_HOST, AGENT_COMMAND  # noqa: E402

READY_TIMEOUT_SECONDS = 20
POLL_SECONDS = 0.25
STABLE_SESSION_SECONDS = 1.0


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


def wait_for_remote_ready(timeout=READY_TIMEOUT_SECONDS):
    """Wait until the configured SSH target accepts a simple batch command."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ssh("true").returncode == 0:
            return True
        time.sleep(POLL_SECONDS)
    return False


def ensure_agent_session(name, command=None, timeout=READY_TIMEOUT_SECONDS):
    """Create the tmux session if missing, then wait until tmux reports it."""
    cmd = command or AGENT_COMMAND
    script = (
        "tmux has-session -t {n} 2>/dev/null "
        "|| tmux new-session -d -s {n} {c}"
    ).format(n=shquote(name), c=shquote(cmd))
    result = ssh("sh", "-lc", shquote(script))
    if result.returncode != 0:
        return False
    return wait_for_agent_session(name, timeout=timeout)


def wait_for_agent_session(
    name,
    timeout=READY_TIMEOUT_SECONDS,
    stable_for=STABLE_SESSION_SECONDS,
):
    """Wait until a named tmux session is visible and stable on the remote."""
    deadline = time.monotonic() + timeout
    first_seen = None
    while time.monotonic() < deadline:
        result = ssh("tmux", "has-session", "-t", name)
        if result.returncode == 0:
            if first_seen is None:
                first_seen = time.monotonic()
            if time.monotonic() - first_seen >= stable_for:
                return True
        else:
            first_seen = None
        time.sleep(POLL_SECONDS)
    return False


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


def launch_agent_tab(boss, name, command=None, create=True):
    """Open a Kitty tab attached to a ready remote tmux session.

    Creation happens over plain ssh first so callers have a concrete readiness
    point before the visual attachment tab opens.
    """
    if not wait_for_remote_ready():
        return False
    if create and not ensure_agent_session(name, command=command):
        return False
    elif not create and not wait_for_agent_session(name):
        return False

    remote_cmd = "exec tmux attach-session -t {n}".format(n=shquote(name))
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
    return True


def shquote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"
