"""
Kitty kitten: jump to next tab whose AI CLI is in a given state.

Usage in kitty.conf:
    map cmd+shift+n kitten ai_jump.py waiting
    map cmd+shift+r kitten ai_jump.py running
"""


def main(args):
    pass


from kittens.tui.handler import result_handler


@result_handler(no_ui=True)
def handle_result(args, answer, target_window_id, boss):
    target_state = args[1] if len(args) > 1 else "waiting"

    tm = boss.active_tab_manager
    if not tm:
        return

    current_tab = boss.active_tab
    tabs = list(tm.tabs)
    current_idx = tabs.index(current_tab) if current_tab in tabs else -1

    for i in range(len(tabs)):
        idx = (current_idx + i + 1) % len(tabs)
        tab = tabs[idx]
        for w in tab:
            if w.user_vars.get("ai_cli_state") == target_state:
                tm.set_active_tab(tab)
                return
