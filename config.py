"""
Configuration for iTerm2 AI Tab Monitor
Customize patterns and colors for your AI coding assistants.
"""

import iterm2

class Config:
    """Configuration for AI session detection and visualization"""

    # How often to check tab states (seconds)
    POLL_INTERVAL = 2.0

    # How many lines to check from bottom of screen
    LINES_TO_CHECK = 10

    # Patterns that indicate waiting for user input
    WAITING_PATTERNS = [
        r'❯\s*$',                          # Common shell prompt
        r'>\s*$',                           # Simple prompt
        r'\$\s*$',                          # Bash prompt
        r'Your response:',                  # Claude Code
        r'Continue\?',                      # Continuation prompts
        r'\[Y/n\]',                         # Yes/no prompts
        r'\[y/N\]',
        r'Press any key',                   # Waiting for keypress
        r'Enter your choice:',              # Choice prompts
        r'What would you like to do\?',     # General prompts
        r'^\s*[>\$#%]\s*$',                 # Various shell prompts
        r'claude>',                         # Claude Code prompt
        r'codex>',                          # Codex prompt
        r'gemini>',                         # Gemini prompt
    ]

    # Patterns that indicate processing/thinking
    PROCESSING_PATTERNS = [
        r'●',                               # Spinner dot
        r'⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏',            # Spinner frames
        r'Running',                         # Generic running
        r'Processing',                      # Generic processing
        r'Thinking',                        # AI thinking
        r'Analyzing',                       # AI analyzing
        r'Generating',                      # AI generating
        r'Loading',                         # Loading state
        r'\.\.\.',                          # Ellipsis
        r'Please wait',                     # Wait message
        r'Working on it',                   # Work in progress
        r'█+\s*\d+%',                       # Progress bars
        r'\[\s*[=>]+\s*\]',                 # Progress indicators
    ]

    # Tab colors for each state
    STATE_COLORS = {
        "waiting": iterm2.Color(0, 200, 0),        # Green - needs attention
        "processing": iterm2.Color(255, 180, 0),   # Orange/Yellow - working
        "idle": iterm2.Color(100, 100, 100),       # Gray - inactive
        "unknown": None,                            # No color
    }

    # Badge text for each state (optional)
    STATE_BADGES = {
        "waiting": "⏸",      # Paused/waiting
        "processing": "▶",   # Playing/running
        "idle": "■",         # Stopped
    }

    # Visual options
    SHOW_BADGES = False           # Show badge icons on tabs
    SHOW_STATE_IN_TITLE = True    # Append [state] to tab title

    # Custom patterns for specific tools
    # Add your own patterns here
    CUSTOM_PATTERNS = {
        "waiting": [
            # Add custom waiting patterns
        ],
        "processing": [
            # Add custom processing patterns
        ]
    }

    def __init__(self):
        """Initialize config with custom patterns if any"""
        self.WAITING_PATTERNS.extend(self.CUSTOM_PATTERNS.get("waiting", []))
        self.PROCESSING_PATTERNS.extend(self.CUSTOM_PATTERNS.get("processing", []))
