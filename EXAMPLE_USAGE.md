# Example Usage

## Typical Workflow

### Scenario: Working across multiple AI tabs

**Tab 1 - Claude Code**
```bash
# Claude emits:
printf '\033]1337;SetUserVar=%s=%s\007' ai_cli_state $(echo -n running | base64)

# Kitty shows:
# - tab color: orange
# - tab title suffix: [running]

# Claude later needs input and emits:
printf '\033]1337;SetUserVar=%s=%s\007' ai_cli_state $(echo -n waiting | base64)

# Kitty shows:
# - tab color: green
# - tab title suffix: [waiting]
```

**Tab 2 - Codex**
```bash
# SessionStart hook emits running
# Stop hook emits waiting
```

### Using Smart Navigation

1. Claude switches its tab to `waiting`
2. You stay in another tab
3. The Claude tab remains green because both active and inactive tab backgrounds are updated
4. Press `Cmd+Shift+N`
5. Kitty jumps to the next tab whose `ai_cli_state` is `waiting`

## Custom Tool Integration

Any tool can integrate as long as it writes Kitty's `SetUserVar` escape sequence to the controlling TTY.

### Mark a tab as running

```bash
printf '\033]1337;SetUserVar=%s=%s\007' ai_cli_state $(echo -n running | base64) > /dev/tty
```

### Mark a tab as waiting

```bash
printf '\033]1337;SetUserVar=%s=%s\007' ai_cli_state $(echo -n waiting | base64) > /dev/tty
```

### Clear the color with another state

```bash
printf '\033]1337;SetUserVar=%s=%s\007' ai_cli_state $(echo -n done | base64) > /dev/tty
```

The watcher only assigns colors to `running` and `waiting`. Other values keep the title annotation but clear the configured tab color.
