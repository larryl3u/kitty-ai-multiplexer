"""Kitty watcher for AI CLI state changes.

Loaded by Kitty via kitty.conf:
    watcher ~/.config/kitty/ai_monitor.py

Reacts to Kitty's `SetUserVar` escape sequence support:
    printf '\\033]1337;SetUserVar=%s=%s\\007' ai_cli_state $(echo -n waiting | base64)
"""

# ── Config ──────────────────────────────────────────────────────────────
STATE_COLORS = {
    "waiting": "#00c800",   # Green  - needs input
    "running": "#ffb400",   # Orange - working
}
# ────────────────────────────────────────────────────────────────────────


def on_set_user_var(boss, window, data):
    is_dict = isinstance(data, dict)
    key = data['key'] if is_dict else data.key
    if key != "ai_cli_state":
        return

    state = data['value'] if is_dict else data.value
    window_id = getattr(window, "id", None)
    if window_id is None:
        return

    color = STATE_COLORS.get(state)
    bg = color if color is not None else "NONE"
    boss.call_remote_control(
        window,
        (
            "set-tab-color",
            "--match",
            f"window_id:{window_id}",
            f"active_bg={bg}",
            f"inactive_bg={bg}",
        ),
    )
