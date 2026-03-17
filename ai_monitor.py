"""
Kitty watcher for AI CLI state changes.

Loaded by Kitty via kitty.conf:
    watcher ~/.config/kitty/ai_monitor.py

Reacts to Kitty's `SetUserVar` escape sequence support:
    printf '\\033]1337;SetUserVar=%s=%s\\007' ai_cli_state $(echo -n waiting | base64)
"""

from kitty.rgb import to_color

# ── Config ──────────────────────────────────────────────────────────────
STATE_COLORS = {
    "waiting": "#00c800",   # Green  - needs input
    "running": "#ffb400",   # Orange - working
}
# ────────────────────────────────────────────────────────────────────────

def find_tab_by_window_id(boss, target_window_id):
    for tm in getattr(boss, "all_tab_managers", ()) or ():
        for tab in tm:
            for w in tab:
                if getattr(w, "id", None) == target_window_id:
                    return tab
    return None


def on_set_user_var(boss, window, data):
    is_dict = isinstance(data, dict)
    key = data['key'] if is_dict else data.key
    if key != "ai_cli_state":
        return

    state = data['value'] if is_dict else data.value
    tab = find_tab_by_window_id(boss, getattr(window, "id", None))
    if tab is None:
        return

    color = STATE_COLORS.get(state)
    if color is not None:
        value = int(to_color(color))
        tab.active_bg = value
        tab.inactive_bg = value
    else:
        tab.active_bg = None
        tab.inactive_bg = None
    tab.mark_tab_bar_dirty()
