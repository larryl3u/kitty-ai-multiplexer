"""
Kitten: rename the current tab AND the matching remote tmux session, so the
two stay aligned (tab title is the registry key in this design).

Bound in kitty.conf, e.g.:
    map kitty_mod+a>r kitten agent_rename.py
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

    ensure_config_dir_on_path()
    from agent_common import boss_rc, ssh

    if old_name and old_name != new_name:
        result = ssh("tmux", "rename-session", "-t", old_name, new_name)
        if result.returncode != 0:
            return

    boss_rc(boss, "set-tab-title", new_name)
