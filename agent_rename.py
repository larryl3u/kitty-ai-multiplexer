"""
Kitten: rename the current tab AND the matching remote tmux session, so the
two stay aligned (tab title is the registry key in this design).

Bound in kitty.conf, e.g.:
    map kitty_mod+a>r kitten agent_rename.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main(args):
    try:
        new_name = input("New name: ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""
    return new_name


from kittens.tui.handler import result_handler  # noqa: E402


@result_handler()
def handle_result(args, answer, target_window_id, boss):
    new_name = (answer or "").strip()
    if not new_name:
        return

    tab = boss.active_tab
    if tab is None:
        return
    old_name = getattr(tab, "name", "") or getattr(tab, "title", "") or ""

    from agent_common import boss_rc, ssh

    if old_name and old_name != new_name:
        result = ssh("tmux", "rename-session", "-t", old_name, new_name)
        if result.returncode != 0:
            return

    boss_rc(boss, "set-tab-title", new_name)
