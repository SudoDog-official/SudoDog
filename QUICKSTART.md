# SudoDog Quick Start Guide

## Installation (2 minutes)

### Option 1: One-Line Install
```bash
curl -sL install.sudodog.com | bash
```

### Option 2: Manual Install
```bash
pip3 install sudodog
sudodog init
```

## Test It Out (1 minute)

### 1. Create a test agent
```bash
cat > test_agent.py << 'EOF'
import time
print("AI Agent running...")
time.sleep(2)

# Try to read sensitive file
try:
    with open('/etc/shadow', 'r') as f:
        print("Read shadow file!")
except:
    print("Blocked!")
EOF
```

### 2. Run with SudoDog
```bash
sudodog run python test_agent.py
```

You should see:
- ✓ Sandboxed environment created
- ✓ Behavioral monitoring active  
- Complete logging of all actions

### 3. Check the logs
```bash
sudodog logs
```

## Real-World Usage

### Running a LangChain Agent
```bash
sudodog run python my_langchain_agent.py
```

### Running an AutoGPT Agent
```bash
sudodog run python -m autogpt
```

### Running with Custom Policy
```bash
sudodog run --policy strict python agent.py
```

## Understanding the Output

When you run `sudodog run`, you'll see:

```
🐕 SudoDog AI Agent Security
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Sandboxed environment created
✓ Behavioral monitoring active
Policy: default

🐕 Starting monitored execution
Command: python test_agent.py
Session: 20250120_143022

✓ Process started (PID: 12345)
⚠  Blocked file access: /etc/shadow

✓ Process completed
Logged 5 actions to ~/.sudodog/logs/20250120_143022.jsonl
```

## Key Concepts

### Security Policies
SudoDog blocks dangerous patterns by default:
- `/etc/shadow`, `/etc/passwd` - System files
- `*.env` - Environment files with secrets
- `DROP TABLE`, `DELETE FROM` - Destructive SQL

Customize in `~/.sudodog/config.json`

### Sessions
Each agent run gets a unique session ID. Use it to:
```bash
sudodog pause <session-id>
sudodog rollback <session-id> --steps 10
```

### Logs
All actions logged to `~/.sudodog/logs/` in JSONL format:
```json
{"timestamp": "2025-01-20T14:30:22", "action_type": "file_access", "details": {...}}
```

## Next Steps

1. **Read the full docs**: https://docs.sudodog.com
2. **Join Discord**: https://discord.gg/sudodog  
3. **Star on GitHub**: https://github.com/sudodog/sudodog
4. **Try Pro features**: Free 14-day trial

## Common Issues

### "sudodog: command not found"
Add `~/.local/bin` to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "Permission denied"
Some operations need sudo. Run with:
```bash
sudo -E sudodog run python agent.py
```

### Agent is slow
Monitoring adds ~5-10% overhead. For production, use:
```bash
sudodog run --log-level warn python agent.py
```

## Getting Help

- 📖 Docs: https://docs.sudodog.com
- 💬 Discord: https://discord.gg/sudodog
- 🐛 Issues: https://github.com/sudodog/sudodog/issues
- 📧 Email: support@sudodog.com

---

**Built something cool with SudoDog? Share it!**
Tag us on Twitter: @sudodog