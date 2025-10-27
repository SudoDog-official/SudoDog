# SudoDog Quick Start Guide

Get started with SudoDog in under 5 minutes.

## Installation (2 minutes)

### One-Line Install (Recommended)
```bash
curl -sL install.sudodog.com | bash
```

### Manual Install
```bash
git clone https://github.com/SudoDog-official/sudodog
cd sudodog
pip3 install -e . --break-system-packages
```

## Test It Out (1 minute)

### 1. Create a test agent
```bash
cat > test_agent.py << 'EOF'
import os
import time

print("🤖 AI Agent running...")
time.sleep(1)

# Try some operations
print("Reading system info...")
os.system("uname -a")

# Try to read sensitive file
print("\nAttempting to read /etc/shadow...")
try:
    with open('/etc/shadow', 'r') as f:
        print("✓ Read shadow file!")
except PermissionError:
    print("✗ Blocked by permissions")

# Simulate dangerous SQL
print("\nSimulating SQL query...")
query = "DROP TABLE users; DELETE FROM customers;"
print(f"Query: {query}")

print("\n✓ Agent completed")
EOF
```

### 2. Run with SudoDog
```bash
sudodog run python test_agent.py
```

You should see:
- ✓ Sandboxed environment created
- ✓ Behavioral monitoring active  
- ⚠️ Detection of dangerous operations
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

### Running Multiple Agents
```bash
# Terminal 1
sudodog run python agent1.py

# Terminal 2  
sudodog run python agent2.py

# Check all running agents
sudodog status
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
Session: 20251025_143022

✓ Process started (PID: 12345)

Output:
🤖 AI Agent running...
Reading system info...
Linux system-name 5.15.0 x86_64

⚠️ Attempting to read /etc/shadow...
✗ Blocked by permissions

⚠️ Simulating SQL query...
Query: DROP TABLE users; DELETE FROM customers;

✓ Agent completed

✓ Process completed
Total actions: 2
Blocked actions: 0
Log file: ~/.sudodog/logs/20251025_143022.jsonl
```

## Key Concepts

### Security Policies

SudoDog monitors dangerous patterns:
- `/etc/shadow`, `/etc/passwd` - System files
- `*.env`, `.aws/credentials` - Files with secrets
- `DROP TABLE`, `DELETE FROM` - Destructive SQL
- `rm -rf`, `curl | bash` - Dangerous shell commands

(Note: Full blocking and custom policies coming in future releases)

### Sessions

Each agent run gets a unique session ID based on timestamp.

### Logs

All actions logged to `~/.sudodog/logs/` in JSONL format:
```json
{"timestamp": "2025-10-25T14:30:22.465327", "session_id": "20251025_143022", "action_type": "start", "details": {"command": "python test_agent.py", "cwd": "/home/user/projects"}}
```

## Next Steps

1. **Read the README**: https://github.com/SudoDog-official/sudodog#readme
2. **Report issues**: https://github.com/SudoDog-official/sudodog/issues
3. **Star on GitHub**: https://github.com/SudoDog-official/sudodog
4. **Join Production waitlist**: https://sudodog.com/#pricing

## Common Issues

### "sudodog: command not found"

The installation should handle this automatically. If not, add to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "externally-managed-environment" error

If pip installation fails, use the flag:
```bash
pip3 install -e . --break-system-packages
```

Or use the one-line installer which handles this automatically.

### Agent behavior looks different

SudoDog wraps your agent but shouldn't change its behavior significantly. Monitoring adds minimal overhead (~1-2%).

## Getting Help

- 🐛 **Report bugs**: https://github.com/SudoDog-official/sudodog/issues
- 💬 **Discussions**: https://github.com/SudoDog-official/sudodog/discussions  
- 🌐 **Website**: https://sudodog.com

---

**Built something cool with SudoDog? Let us know!**

Open a discussion on GitHub or join our Production tier waitlist at sudodog.com
