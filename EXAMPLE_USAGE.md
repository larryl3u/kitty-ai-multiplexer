# Example Usage

## Typical Workflow

### Scenario: Working on a new feature across multiple AI assistants

**Tab 1 - Claude Code (local)**
```bash
claude code
# State: [waiting] - Tab color: 🟢 Green
> "Add user authentication to the API"
# State: [processing] - Tab color: 🟡 Yellow
# ... Claude is working ...
# State: [waiting] - Tab color: 🟢 Green
> Continue? [Y/n]
```

**Tab 2 - Remote server running tests**
```bash
ssh prod-server -t "codex"
# State: [processing] - Tab color: 🟡 Yellow
# Running tests...
# ... Tests complete ...
# State: [waiting] - Tab color: 🟢 Green
> Tests failed. Fix? [Y/n]
```

**Tab 3 - Gemini for documentation**
```bash
gemini-code
# State: [idle] - Tab color: ⚫ Gray
# Completed earlier task
```

### Using Smart Navigation

1. You're in Tab 1, Claude asks for confirmation
2. You switch to Tab 3 to check something
3. Meanwhile, Tab 2 finishes tests and needs input
4. Press **⌘⇧N** → Instantly jumps to Tab 2 (next waiting)
5. Handle Tab 2, press **⌘⇧N** again → Jumps back to Tab 1 (still waiting)

### Visual Overview

Just glance at your tab bar:

```
[Tab 1: Claude]     [Tab 2: Tests]      [Tab 3: Docs]
🟢 waiting          🟡 processing       ⚫ idle
```

You immediately know:
- Tab 1 needs your attention
- Tab 2 is still working
- Tab 3 is done

## Advanced Patterns

### Multi-stage Pipeline

Run parallel tasks, jump between them as they need input:

```bash
# Tab 1: Frontend build
npm run build:watch
# 🟡 processing

# Tab 2: Backend tests
pytest --watch
# 🟡 processing

# Tab 3: Claude Code - implementing feature
claude code
# 🟢 waiting - needs your input

# Tab 4: Remote deployment
ssh deploy-server -t "deploy-script"
# 🟡 processing
```

Press **⌘⇧N** repeatedly to cycle through all tabs needing input, skipping the ones still processing.

### Remote Development

All tabs are remote SSH sessions to different servers:

```bash
# Tab 1: Dev server - Claude Code
ssh dev -t "claude code"

# Tab 2: Staging server - Running tests
ssh staging -t "pytest"

# Tab 3: Prod server - Monitoring
ssh prod -t "watch -n 1 'kubectl get pods'"
```

The monitor works identically - it doesn't care if the process is local or remote.

## Customizing for Your Tools

### Example: Custom AI Tool

You have a custom AI assistant called `myai` with prompts like:

```
MyAI> Your command?
```

Add to `config.py`:

```python
WAITING_PATTERNS = [
    r'MyAI>\s*$',  # Your custom prompt
    # ... other patterns
]
```

### Example: Build Tool Integration

You want to track build status:

```python
PROCESSING_PATTERNS = [
    r'Building\.\.\.',
    r'Compiling \d+/\d+',
    # ... other patterns
]

WAITING_PATTERNS = [
    r'Build failed\. Retry\?',
    r'Build complete\. Deploy\?',
    # ... other patterns
]
```

## Tips

1. **Start AI sessions in background**: Open multiple tabs, start your AI tools, let them all work in parallel

2. **Use descriptive tab names**: Right-click tab → Edit Session → Set title manually (or let the script append state)

3. **Combine with tmux for remote persistence**:
   ```bash
   ssh server -t "tmux new -A -s ai 'claude code'"
   ```
   Session persists even if connection drops

4. **Monitor long-running tasks**: Start a task, switch away, get notified (via color) when it needs you

5. **Batch operations**: Start 5 different AI tasks in 5 tabs, handle them as they complete rather than waiting serially
