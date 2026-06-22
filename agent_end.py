"""
Kitten: pick a remote session, confirm, force-kill it on the remote. Any
local tab attached to it will see its ssh drop naturally.

Reserved for the rare forced case — the normal end-of-life path is to exit
the agent (Ctrl+D / `exit`) inside its own session.

Bound in kitty.conf, e.g.:
    map kitty_mod+a>k kitten agent_end.py
"""

import os
import sys

try:
    from kitty.constants import config_dir as KITTY_CONFIG_DIR
except Exception:
    KITTY_CONFIG_DIR = os.environ.get("KITTY_CONFIG_DIRECTORY", "")


def ensure_config_dir_on_path():
    if KITTY_CONFIG_DIR and KITTY_CONFIG_DIR not in sys.path:
        sys.path.insert(0, KITTY_CONFIG_DIR)


def main(args):
    ensure_config_dir_on_path()
    from agent_common import list_remote_sessions_result

    result = list_remote_sessions_result()
    sessions = result.sessions
    if not sessions:
        if result.error:
            print("Could not list remote tmux sessions:")
            print(result.error)
        else:
            print("No tmux sessions on remote.")
        return ""

    for i, name in enumerate(sessions, 1):
        print(f"  {i}) {name}")
    try:
        raw = input("Kill # (or name): ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""
    if not raw:
        return ""
    target = ""
    if raw.isdigit():
        idx = int(raw)
        if 1 <= idx <= len(sessions):
            target = sessions[idx - 1]
    elif raw in sessions:
        target = raw
    if not target:
        return ""
    try:
        confirm = input(f"Kill '{target}'? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return ""
    return target if confirm in ("y", "yes") else ""


from kittens.tui.handler import result_handler  # noqa: E402


@result_handler()
def handle_result(args, answer, target_window_id, boss):
    name = (answer or "").strip()
    if not name:
        return
    ensure_config_dir_on_path()
    from agent_common import ssh

    ssh("tmux", "kill-session", "-t", name)
