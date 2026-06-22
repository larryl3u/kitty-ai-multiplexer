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
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_config import REMOTE_HOST, AGENT_COMMAND  # noqa: E402

SSH_TIMEOUT_SECONDS = 5
LOG_PATH = "/tmp/kitty-ai-multiplexer.log"


@dataclass
class SessionList:
    sessions: list
    error: str = ""


def ssh(*remote_argv, capture=True, check=False, timeout=SSH_TIMEOUT_SECONDS):
    """Fire-and-forget ssh for remote tmux queries."""
    argv = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=5",
        "-o",
        "ConnectionAttempts=1",
        REMOTE_HOST,
        *remote_argv,
    ]
    try:
        if capture:
            return subprocess.run(
                argv,
                capture_output=True,
                text=True,
                check=check,
                timeout=timeout,
            )
        return subprocess.run(argv, check=check, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        return subprocess.CompletedProcess(
            argv,
            124,
            e.stdout or "",
            e.stderr or "ssh timed out",
        )


def list_remote_sessions():
    """Live session names on the remote. Empty list on any error."""
    return list_remote_sessions_result().sessions


def list_remote_sessions_result():
    """Live session names plus a diagnostic when the remote query fails."""
    r = ssh("tmux", "ls", "-F", "#{session_name}")
    if r.returncode == 0:
        return SessionList(
            [line.strip() for line in r.stdout.splitlines() if line.strip()]
        )

    err = ((r.stderr or "") + (r.stdout or "")).strip()
    if "no server running" in err.lower() or "failed to connect to server" in err.lower():
        return SessionList([])
    if not err:
        err = "ssh/tmux query failed with exit code {code}".format(code=r.returncode)
    log_debug("list_remote_sessions failed: " + err)
    return SessionList([], err)


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
    log_debug("kitty @ " + " ".join(argv))
    try:
        result = boss.call_remote_control(None, tuple(argv))
    except Exception as e:
        log_debug("remote-control exception: " + repr(e))
        raise
    log_debug("remote-control result: " + repr(result))
    return result


def launch_agent_tab(boss, name, command=None, create=True):
    """Open a Kitty tab that performs SSH visibly, then attaches tmux."""
    remote_cmd = remote_tmux_command(name, command=command, create=create)
    boss_rc(
        boss,
        "launch",
        "--type=tab",
        "--hold",
        "--tab-title=" + name,
        "kitten",
        "ssh",
        "-t",
        REMOTE_HOST,
        remote_cmd,
    )
    return True


def remote_tmux_command(name, command=None, create=True):
    if not create:
        return "exec tmux attach-session -t {n}".format(n=shquote(name))

    cmd = command if command is not None else AGENT_COMMAND
    new_session = "tmux new-session -d -s {n}".format(n=shquote(name))
    if cmd:
        agent_cmd = (
            "{cmd}; status=$?; "
            "printf '\\n[command exited with status %s; keeping shell open]\\n' "
            "\"$status\"; "
            "exec \"${{SHELL:-sh}}\""
        ).format(cmd=cmd)
        new_session = "tmux new-session -d -s {n} {agent}".format(
            n=shquote(name),
            agent=shquote('exec "${SHELL:-sh}" -lc ' + shquote(agent_cmd)),
        )
    return (
        "tmux has-session -t {n} 2>/dev/null "
        "|| {new_session}; "
        "exec tmux attach-session -t {n}"
    ).format(
        n=shquote(name),
        new_session=new_session,
    )


def shquote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"


def log_debug(message):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write("[{stamp}] {message}\n".format(stamp=stamp, message=message))
    except Exception:
        pass
