"""
Kitten: open a Kitty tab for every remote tmux session not already attached.

Cold-start rehydrate. Idempotent — running it twice does not duplicate tabs.

Bound in kitty.conf, e.g.:
    map kitty_mod+a>a kitten agent_connect_all.py
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
    pass


@result_handler(no_ui=True)
def handle_result(args, answer, target_window_id, boss):
    ensure_config_dir_on_path()
    from agent_common import (  # local import — boss process
        kitty_tabs_by_title,
        launch_agent_tab,
        list_remote_sessions_result,
        log_debug,
    )

    result = list_remote_sessions_result()
    if result.error:
        log_debug("connect_all skipped: " + result.error)
        return

    have = set(kitty_tabs_by_title(boss).keys())
    for name in result.sessions:
        if name in have:
            continue
        launch_agent_tab(boss, name, create=False)
