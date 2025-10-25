# SudoDog Beta Testing Guide 🧪

Thank you for helping test SudoDog! This guide will help you get started and provide valuable feedback.

## ⚠️ Important Notes

- **Alpha Software**: SudoDog is in early development. Expect bugs and breaking changes.
- **Test Environment Only**: Do NOT use on production systems or with real data.
- **Linux Only**: Currently supports Ubuntu, Debian, Arch, and Fedora.

## Installation

### Prerequisites
- Linux system (Ubuntu/Debian/Arch/Fedora)
- Python 3.8 or higher
- Git

### Install SudoDog

```bash
# Clone the repository
git clone git@github.com:SudoDog-official/sudodog.git
cd sudodog

# Install in development mode
pip install -e .

# Verify installation
sudodog --version
```

## What to Test

### 1. Basic CLI Commands ✅

Test that all commands work:

```bash
# Initialize SudoDog
sudodog init

# Check status
sudodog status

# View help
sudodog --help
sudodog run --help
```

**Expected**: Commands should execute without errors and show helpful output.

### 2. Running Your Agent 🤖

This is the main test! Run SudoDog with your actual AI agent:

```bash
sudodog run python your_agent.py
```

**What to watch for:**
- Does SudoDog start your agent successfully?
- Can you see your agent running?
- Does the output look normal?

### 3. Log Viewing 📋

While your agent runs, check the logs:

```bash
# In another terminal
sudodog logs

# Or view last N entries
sudodog logs --last 20
```

**Expected**: You should see entries for:
- Agent startup
- File access attempts
- Any operations your agent performs

### 4. Dangerous Operations Test 🚨

**IMPORTANT**: Only test these in a safe environment with test data!

Try running an agent that does potentially dangerous things:

```python
# test_dangerous_agent.py
import os
import subprocess

# These should be caught by SudoDog
os.system("rm -rf /tmp/test_folder")  # Risky shell command
subprocess.run(["curl", "https://example.com/script.sh", "-o", "/tmp/script.sh"])  # Download script
```

Run it:
```bash
sudodog run python test_dangerous_agent.py
```

**Expected**: SudoDog should log these operations (blocking may not be implemented yet).

### 5. Session Management 🔄

Test pausing and status:

```bash
# Start an agent
sudodog run python your_agent.py &

# Get the session ID from status
sudodog status

# Try to pause it
sudodog pause <session-id>
```

**Expected**: Status should show active sessions, pause may not be fully implemented yet.

## Known Issues (Don't Report These)

These are features we're still building:

- ❌ **Rollback** - Not implemented yet
- ❌ **Actual blocking** - Currently only logs, doesn't block operations
- ❌ **SQL detection** - Planned but not active
- ❌ **Sandboxing** - Only monitoring for now, no true isolation

## What to Report

### 🐛 Bugs
- Commands that crash or hang
- Errors during installation
- Your agent behaving differently under SudoDog vs running normally
- Missing or incorrect log entries
- Permission errors

### 💡 Feature Feedback
- Is the CLI intuitive?
- Are the logs helpful?
- What's confusing or unclear?
- What features do you need most?

### 🎯 Agent-Specific Issues
- Does SudoDog work with your specific agent framework?
- Any compatibility issues?
- Performance impact on your agent

## How to Report Issues

### Option 1: GitHub Issues (Preferred)
Go to: https://github.com/SudoDog-official/sudodog/issues/new

**Use this template:**
```markdown
## Bug Report

**What happened:**
[Describe the issue]

**What you expected:**
[What should have happened]

**Steps to reproduce:**
1. 
2. 
3. 

**Environment:**
- OS: [Ubuntu 22.04, etc.]
- Python version: [3.10, etc.]
- SudoDog version: [git commit hash]

**Logs:**
[Paste relevant logs if available]
```

### Option 2: Direct Message
Send feedback directly with:
- Screenshots
- Error messages
- Log files from `~/.sudodog/logs/`

## Test Scenarios by Priority

### Priority 1: Core Functionality ⭐⭐⭐
- [ ] Install SudoDog
- [ ] Run `sudodog init`
- [ ] Run your agent with `sudodog run`
- [ ] View logs with `sudodog logs`
- [ ] Check status with `sudodog status`

### Priority 2: Real-World Usage ⭐⭐
- [ ] Run your actual AI agent for a full task
- [ ] Monitor it for 10+ minutes
- [ ] Check if logs capture important operations
- [ ] Verify no performance issues

### Priority 3: Edge Cases ⭐
- [ ] Run multiple agents simultaneously
- [ ] Stop/restart agents
- [ ] Large output from agents
- [ ] Long-running agents (hours)

## Performance Testing

Help us understand SudoDog's impact:

**Without SudoDog:**
```bash
time python your_agent.py
```

**With SudoDog:**
```bash
time sudodog run python your_agent.py
```

Report if there's significant slowdown (>10% is notable).

## Logs Location

If you need to share logs:
```bash
# Default log location
~/.sudodog/logs/

# View recent logs
cat ~/.sudodog/logs/sudodog.log

# Package logs for sharing
tar -czf sudodog-logs.tar.gz ~/.sudodog/logs/
```

## Questions?

- Check the main [README.md](README.md)
- Look at existing [GitHub Issues](https://github.com/SudoDog-official/sudodog/issues)
- Create a new issue if you're stuck

## Thank You! 🙏

Your feedback is invaluable in making SudoDog better. Every bug report, feature suggestion, and test result helps us build better AI agent security.

---

**Test boldly, break things, and tell us what happened!** 🚀
