"""
Kitten: prompt for a name, spawn a new remote tmux session and a local tab.

Bound in kitty.conf, e.g.:
    map kitty_mod+a>c kitten agent_create.py
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
    ensure_config_dir_on_path()
    from agent_common import launch_agent_tab  # local import — boss process
    launch_agent_tab(boss, name)
