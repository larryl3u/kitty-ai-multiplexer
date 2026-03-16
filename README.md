# iTerm2 AI Multiplexer

Smart tab management for AI coding assistants (Claude Code, Codex, Gemini, etc.) in iTerm2.

## Features

- **Automatic tab coloring** based on AI session state
  - 🟢 Green: Waiting for your input
  - 🟡 Yellow: Processing/thinking
  - ⚫ Gray: Idle/completed

- **Smart navigation**
  - Jump to next tab waiting for input with a single keypress
  - Works with local and remote (SSH) sessions
  - Provider-agnostic (Claude, Codex, Gemini, etc.)

- **Visual indicators**
  - Tab titles show state: `[waiting]`, `[processing]`, `[idle]`
  - Optional badge icons on tabs
  - At-a-glance status of all AI sessions

## Installation

### 1. Install iTerm2 Python Runtime

```bash
iTerm2 → Scripts → Manage → Install Python Runtime
```

### 2. Install the Script

```bash
# Copy script to iTerm2 AutoLaunch directory
mkdir -p ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch
cp ai_monitor.py config.py ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch/
```

### 3. Restart iTerm2

The script will automatically start monitoring your tabs.

## Setup Keybindings

### Jump to Next Waiting Tab

1. iTerm2 → Settings → Keys → Key Bindings
2. Click `+` to add new keybinding
3. Set keyboard shortcut (e.g., `⌘⇧N`)
4. Action: `Invoke Script Function`
5. Function call: `jump_to_waiting`

### Optional: Jump to Next Processing Tab

Same as above, but use function call: `jump_to_processing`

## Configuration

Edit `config.py` to customize:

### Detection Patterns

Add patterns for your specific AI tools:

```python
WAITING_PATTERNS = [
    r'your-custom-prompt>',
    # Add more patterns
]

PROCESSING_PATTERNS = [
    r'YourAI is thinking',
    # Add more patterns
]
```

### Colors

Customize tab colors:

```python
STATE_COLORS = {
    "waiting": iterm2.Color(0, 255, 0),    # RGB values
    "processing": iterm2.Color(255, 200, 0),
    "idle": iterm2.Color(128, 128, 128),
}
```

### Polling Interval

Adjust how often tabs are checked:

```python
POLL_INTERVAL = 2.0  # seconds
```

## Usage

### Starting AI Sessions

Just start your AI assistant in any tab:

```bash
# Local
claude code

# Remote
ssh myserver -t "claude code"

# Any AI tool
codex
gemini-code
```

The monitor automatically detects and tracks state.

### Navigation

- **⌘⇧N** (or your custom binding): Jump to next tab waiting for input
- Glance at tab bar to see which sessions need attention
- Tab colors update in real-time

## How It Works

1. **Background monitoring**: Script polls all tabs every 2 seconds
2. **Pattern matching**: Analyzes last 10 lines of each tab's output
3. **State detection**: Matches against patterns for "waiting" vs "processing"
4. **Visual updates**: Sets tab colors and titles based on detected state
5. **Smart navigation**: Tracks state and enables "jump to next waiting"

## Troubleshooting

### Script not running

Check if it's loaded:
```bash
iTerm2 → Scripts → (you should see ai_monitor.py listed)
```

View logs:
```bash
tail -f ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch/ai_monitor.log
```

### State detection not working

- Check that your AI tool's prompts match patterns in `config.py`
- Add custom patterns for your specific tool
- Increase `LINES_TO_CHECK` if prompts appear higher up

### Colors not showing

- Ensure iTerm2 → Settings → Appearance → Tabs → "Show tab colors" is enabled
- Check that you're using a recent iTerm2 version (3.4+)

## Architecture

```
ai_monitor.py          # Main monitoring script
├── AITabMonitor       # Core monitoring class
│   ├── detect_state() # Pattern matching for state detection
│   ├── monitor_tabs() # Background polling loop
│   └── jump_to_*()    # Navigation functions
└── main()             # Entry point, RPC registration

config.py              # User-configurable patterns and colors
└── Config             # Configuration class
```

## Extending

### Add Support for New AI Tool

Edit `config.py`:

```python
WAITING_PATTERNS = [
    r'your-ai-tool>',  # Add tool's prompt pattern
]

PROCESSING_PATTERNS = [
    r'YourAI: Thinking',  # Add processing indicators
]
```

### Custom State Logic

Modify `detect_state()` in `ai_monitor.py` for advanced detection:

```python
async def detect_state(self, session: iterm2.Session) -> str:
    # Add custom logic here
    # e.g., check process name, environment variables, etc.
    pass
```

## Limitations

- **Pattern-based detection**: May have false positives/negatives
- **Polling delay**: 2-second delay before state updates
- **iTerm2 only**: Doesn't work with other terminals
- **Local analysis**: Can't detect state from SSH'd AI sessions' internal state (relies on output patterns)

## Future Improvements

- [ ] Escape sequence protocol for AI tools to emit state directly
- [ ] Support for Ghostty, Wezterm, other terminals
- [ ] Machine learning-based state detection
- [ ] Integration with AI tool APIs for accurate state
- [ ] Tmux integration for remote session persistence

## License

MIT

## Contributing

Issues and PRs welcome! Add patterns for new AI tools, improve detection logic, etc.
