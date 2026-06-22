"""
Kitten: prompt for a name, spawn a new remote tmux session and a local tab.

Bound in kitty.conf, e.g.:
    map kitty_mod+a>c kitten agent_create.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kittens.tui.handler import result_handler  # noqa: E402


def main(args):
    try:
        name = input("New agent name: ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""
    return name


@result_handler()
def handle_result(args, answer, target_window_id, boss):
    name = (answer or "").strip()
    if not name:
        return
    from agent_common import launch_agent_tab  # local import — boss process
    launch_agent_tab(boss, name)
