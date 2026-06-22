"""
Kitten: numbered picker over remote tmux sessions. Pick one → attach in a new
local tab (or focus the existing tab if one already shows that session).

Bound in kitty.conf, e.g.:
    map kitty_mod+a>l kitten agent_pick.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main(args):
    from agent_common import list_remote_sessions

    sessions = list_remote_sessions()
    if not sessions:
        print("No agent sessions on remote.")
        try:
            input("Press Enter to close…")
        except (EOFError, KeyboardInterrupt):
            pass
        return ""

    for i, name in enumerate(sessions, 1):
        print(f"  {i}) {name}")
    try:
        raw = input("Attach to # (or name): ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""
    if not raw:
        return ""
    if raw.isdigit():
        idx = int(raw)
        if 1 <= idx <= len(sessions):
            return sessions[idx - 1]
        return ""
    return raw if raw in sessions else ""


from kittens.tui.handler import result_handler  # noqa: E402


@result_handler()
def handle_result(args, answer, target_window_id, boss):
    name = (answer or "").strip()
    if not name:
        return
    from agent_common import kitty_tabs_by_title, launch_agent_tab

    existing = kitty_tabs_by_title(boss).get(name)
    if existing is not None:
        for tm in getattr(boss, "all_tab_managers", ()) or ():
            if existing in list(tm):
                tm.set_active_tab(existing)
                return
    launch_agent_tab(boss, name)
