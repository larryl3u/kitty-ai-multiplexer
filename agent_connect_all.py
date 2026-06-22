"""
Kitten: open a Kitty tab for every remote tmux session not already attached.

Cold-start rehydrate. Idempotent — running it twice does not duplicate tabs.

Bound in kitty.conf, e.g.:
    map kitty_mod+a>a kitten agent_connect_all.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kittens.tui.handler import result_handler  # noqa: E402


def main(args):
    pass


@result_handler(no_ui=True)
def handle_result(args, answer, target_window_id, boss):
    from agent_common import (  # local import — boss process
        kitty_tabs_by_title,
        launch_agent_tab,
        list_remote_sessions,
    )

    have = set(kitty_tabs_by_title(boss).keys())
    for name in list_remote_sessions():
        if name in have:
            continue
        launch_agent_tab(boss, name)
