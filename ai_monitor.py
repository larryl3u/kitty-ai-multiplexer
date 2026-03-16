#!/usr/bin/env python3
"""
iTerm2 AI Session Multiplexer
Monitors tabs for AI coding assistant state and provides smart navigation.
"""

import iterm2
import asyncio
import re
from typing import Optional, List
from config import Config

class TabState:
    """Represents the state of a tab running an AI assistant"""
    WAITING = "waiting"      # Waiting for user input
    PROCESSING = "processing"  # Processing/thinking
    IDLE = "idle"            # Idle or completed
    UNKNOWN = "unknown"      # Can't determine state

class AITabMonitor:
    """Monitors iTerm2 tabs for AI session state"""

    def __init__(self, app: iterm2.App, config: Config):
        self.app = app
        self.config = config
        self.tab_states = {}  # tab_id -> state

    async def detect_state(self, session: iterm2.Session) -> str:
        """Detect the current state of a session"""
        if not session:
            return TabState.UNKNOWN

        try:
            # Get screen content
            screen = await session.async_get_screen_contents()
            if not screen:
                return TabState.UNKNOWN

            # Get last N lines
            lines = screen.lines[-self.config.LINES_TO_CHECK:]
            text = "\n".join(line.string for line in lines)

            # Check for waiting patterns (highest priority)
            for pattern in self.config.WAITING_PATTERNS:
                if re.search(pattern, text, re.MULTILINE):
                    return TabState.WAITING

            # Check for processing patterns
            for pattern in self.config.PROCESSING_PATTERNS:
                if re.search(pattern, text, re.MULTILINE):
                    return TabState.PROCESSING

            # Check if process is active (not blocking on input)
            # If last line is empty or hasn't changed, likely idle
            return TabState.IDLE

        except Exception as e:
            print(f"Error detecting state: {e}")
            return TabState.UNKNOWN

    async def set_tab_color(self, tab: iterm2.Tab, state: str):
        """Set tab color based on state"""
        color = self.config.STATE_COLORS.get(state)
        if color:
            await tab.async_set_tab_color(color)

    async def set_tab_badge(self, tab: iterm2.Tab, state: str):
        """Set tab badge/annotation based on state"""
        if not self.config.SHOW_BADGES:
            return

        badge = self.config.STATE_BADGES.get(state, "")
        session = tab.current_session
        if session and badge:
            await session.async_set_variable("user.badge", badge)

    async def monitor_tabs(self):
        """Continuously monitor all tabs and update their appearance"""
        print("🤖 AI Tab Monitor started")
        print(f"   Monitoring every {self.config.POLL_INTERVAL}s")
        print(f"   Colors: {TabState.WAITING}=green, {TabState.PROCESSING}=yellow, {TabState.IDLE}=gray")

        while True:
            try:
                for window in self.app.windows:
                    for tab in window.tabs:
                        session = tab.current_session
                        if session:
                            state = await self.detect_state(session)
                            self.tab_states[tab.tab_id] = state

                            # Update visual indicators
                            await self.set_tab_color(tab, state)
                            await self.set_tab_badge(tab, state)

                            # Optionally update title
                            if self.config.SHOW_STATE_IN_TITLE:
                                title = f"{session.name or 'Tab'} [{state}]"
                                await tab.async_set_title(title)

                await asyncio.sleep(self.config.POLL_INTERVAL)

            except Exception as e:
                print(f"Error in monitor loop: {e}")
                await asyncio.sleep(self.config.POLL_INTERVAL)

    async def jump_to_next_waiting(self):
        """Jump to the next tab that's waiting for input"""
        window = self.app.current_terminal_window
        if not window:
            print("No active window")
            return

        tabs = window.tabs
        if not tabs:
            return

        current_tab = window.current_tab
        current_idx = tabs.index(current_tab) if current_tab in tabs else -1

        # Search forward from current position, then wrap around
        for i in range(len(tabs)):
            idx = (current_idx + i + 1) % len(tabs)
            tab = tabs[idx]

            state = self.tab_states.get(tab.tab_id, TabState.UNKNOWN)

            if state == TabState.WAITING:
                await tab.async_select()
                print(f"✓ Jumped to waiting tab: {tab.title or 'Untitled'}")
                return

        print("No tabs waiting for input")

    async def jump_to_next_by_state(self, target_state: str):
        """Jump to next tab with specific state"""
        window = self.app.current_terminal_window
        if not window:
            return

        tabs = window.tabs
        if not tabs:
            return

        current_tab = window.current_tab
        current_idx = tabs.index(current_tab) if current_tab in tabs else -1

        for i in range(len(tabs)):
            idx = (current_idx + i + 1) % len(tabs)
            tab = tabs[idx]

            state = self.tab_states.get(tab.tab_id, TabState.UNKNOWN)

            if state == target_state:
                await tab.async_select()
                return

async def main(connection):
    """Main entry point"""
    app = await iterm2.async_get_app(connection)
    config = Config()
    monitor = AITabMonitor(app, config)

    # Start background monitoring task
    asyncio.create_task(monitor.monitor_tabs())

    # Register RPC functions for keybindings
    async def jump_to_waiting_rpc(connection):
        await monitor.jump_to_next_waiting()

    async def jump_to_processing_rpc(connection):
        await monitor.jump_to_next_by_state(TabState.PROCESSING)

    await iterm2.RPC.async_register(
        connection,
        "jump_to_waiting",
        jump_to_waiting_rpc,
        timeout=1.0
    )

    await iterm2.RPC.async_register(
        connection,
        "jump_to_processing",
        jump_to_processing_rpc,
        timeout=1.0
    )

    print("✓ RPC functions registered:")
    print("  - jump_to_waiting")
    print("  - jump_to_processing")

    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    iterm2.run_forever(main)
