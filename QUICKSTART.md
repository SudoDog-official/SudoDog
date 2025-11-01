# SudoDog Quick Start Guide

Get started with SudoDog in under 5 minutes.

## Zero Integration - Just Prepend One Command

Already have an AI agent? **No code changes needed.**

```bash
# Before: Your existing agent
python my_langchain_agent.py

# After: Secured with SudoDog (that's it!)
sudodog run python my_langchain_agent.py
```

Works with LangChain, AutoGPT, CrewAI, or any framework. Any language.

**What you'll get:**
- ✅ SudoDog CLI installed
- ✅ Sample agents in `~/sudodog-examples/` (for verification)
- ✅ Configuration in `~/.sudodog/`

## Installation (2 minutes)

### One-Line Install (Recommended)
```bash
curl -sL https://sudodog.com/install.sh | bash
```

This installs SudoDog and creates sample agents you can run immediately!

### Manual Install
```bash
git clone https://github.com/SudoDog-official/sudodog
cd sudodog
pip3 install -e . --break-system-packages
```

### Docker Setup (Optional - for stronger isolation)
```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Log out and log back in for changes to take effect
```

## Initialize SudoDog

```bash
sudodog init
```

This creates:
- `~/.sudodog/config.json` - Configuration
- `~/.sudodog/logs/` - Activity logs
- `~/.sudodog/backups/` - File rollback backups

## Quick Test (1 minute)

The install script automatically created sample agents in `~/sudodog-examples/`.

### 1. Run your first agent (Basic isolation)
```bash
sudodog run python ~/sudodog-examples/hello_agent.py
```

You should see:
```
🤖 Hello from your AI agent!
✓ SudoDog is protecting this execution
...
```

### 2. Run with Docker (stronger isolation)
```bash
sudodog run --docker python ~/sudodog-examples/demo_agent.py
```

This shows SudoDog detecting dangerous operations like:
- Attempts to read `/etc/shadow`
- SQL injection patterns (`DROP TABLE`)

### 3. Run with resource limits
```bash
sudodog run --docker --cpu-limit 2.0 --memory-limit 1g python ~/sudodog-examples/demo_agent.py
```

### 4. Check the logs
```bash
sudodog logs --last 20
```

## Run YOUR OWN Agent (The Real Use Case!)

Now that you've verified SudoDog works, secure your existing agents:

### LangChain
```bash
sudodog run python my_langchain_agent.py
```

### AutoGPT
```bash
sudodog run python -m autogpt
```

### CrewAI
```bash
sudodog run python my_crewai_agent.py
```

### Any Framework, Any Language
```bash
sudodog run node my_agent.js       # Node.js
sudodog run ruby my_agent.rb        # Ruby
sudodog run ./my_agent.sh           # Bash
sudodog run <your-command-here>     # Anything!
```

**That's it!** No code changes, no imports, no configuration. Just prepend `sudodog run`.

## Background Monitoring (New!)

Start the daemon to monitor all containers in real-time:

```bash
# Start daemon in foreground (see logs)
sudodog daemon start --foreground

# Or start in background
sudodog daemon start

# Check status
sudodog daemon status

# Stop daemon
sudodog daemon stop
```

## Real-World Usage

### Running a LangChain Agent
```bash
sudodog run --docker python my_langchain_agent.py
```

### Running an AutoGPT Agent
```bash
sudodog run --docker python -m autogpt
```

### Running Multiple Agents with Monitoring
```bash
# Terminal 1: Start daemon
sudodog daemon start --foreground

# Terminal 2: Run agent 1
sudodog run --docker python agent1.py

# Terminal 3: Run agent 2
sudodog run --docker python agent2.py

# Terminal 4: Check status
sudodog daemon status
```

## Docker vs Namespace Isolation

| Feature | Namespace (default) | Docker (--docker) |
|---------|-------------------|-------------------|
| Isolation strength | Basic | Strong |
| Resource limits | ❌ | ✅ CPU & Memory |
| Network isolation | ❌ | ✅ Configurable |
| Escape prevention | ⚠️ Possible | ✅ Very difficult |
| Setup required | None | Docker install |
| Speed | Fast | Slightly slower (first run) |

**Recommendation:** Use `--docker` for production agents, namespace for quick testing.

## Understanding the Output

### Basic Run
```
🐕 SudoDog AI Agent Security
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Sandboxed environment created
✓ Behavioral monitoring active
Policy: default

✓ Process completed
Total actions: 5
Blocked actions: 2
Log file: ~/.sudodog/logs/20251030_143022.jsonl
```

### Docker Run
```
🐕 SudoDog AI Agent Security
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐳 Using Docker sandbox
🐳 Creating Docker container...
   Network: enabled
   CPU limit: 1.0 cores
   Memory limit: 512m
✓ Container created: d2dcfb3e93d6
▶ Starting container d2dcfb3e93d6...
✓ Container running

[Agent output appears here]

✓ Container exited with code 0
CPU: 0.5% | Memory: 45.2MB
⏹ Stopping container d2dcfb3e93d6...
✓ Container stopped
🗑 Cleaning up container d2dcfb3e93d6...
✓ Container removed
```

### Daemon Status
```
✓ Daemon is running (PID: 95100)
Last check: 2025-10-30T16:42:40.984222
Active containers: 2

┌─────────────┬──────────────────┬───────┬──────────┬────────┐
│ Container   │ Session          │ CPU%  │ Memory%  │ Alerts │
├─────────────┼──────────────────┼───────┼──────────┼────────┤
│ c3b2d252a7e8│ 20251030_164230  │ 2.3   │ 15.4     │ 0      │
│ a1b3c4d5e6f7│ 20251030_164301  │ 45.8  │ 78.2     │ 1      │
└─────────────┴──────────────────┴───────┴──────────┴────────┘
```

## Key Features

### 🔒 Security Monitoring

SudoDog detects dangerous patterns:
- `/etc/shadow`, `/etc/passwd` - System files
- `*.env`, `.aws/credentials` - Files with secrets
- `DROP TABLE`, `DELETE FROM` - Destructive SQL
- `rm -rf`, `curl | bash` - Dangerous shell commands

### 📊 Real-Time Monitoring (Daemon)

- CPU usage tracking
- Memory usage tracking
- Alert on threshold breaches
- Multi-container management

### ⏪ File Rollback

```bash
# Rollback changes from a session
sudodog rollback <session_id>

# Rollback last N operations
sudodog rollback <session_id> --steps 5
```

### 📋 Complete Audit Trail

All actions logged to `~/.sudodog/logs/` in JSONL format:
```json
{"timestamp": "2025-10-30T14:30:22.465327", "session_id": "20251030_143022", "action_type": "start", "details": {"command": "python test_agent.py"}}
```

## Commands Reference

```bash
# Initialize
sudodog init

# Run agent (basic)
sudodog run python agent.py

# Run agent (Docker)
sudodog run --docker python agent.py

# Run with limits
sudodog run --docker --cpu-limit 2.0 --memory-limit 1g python agent.py

# Daemon management
sudodog daemon start            # Background
sudodog daemon start --foreground  # Foreground (see logs)
sudodog daemon status           # Check status
sudodog daemon stop             # Stop daemon

# View logs
sudodog logs                    # Last 10 actions
sudodog logs --last 50          # Last 50 actions
sudodog logs --session <id>     # Specific session

# Check active agents
sudodog status

# Rollback operations
sudodog rollback <session_id>

# List policies
sudodog policies

# Version info
sudodog version
```

## Next Steps

1. **Read the full README**: https://github.com/SudoDog-official/sudodog#readme
2. **Check INSTALL_GUIDE.md**: For Docker + Daemon setup details
3. **Join Production waitlist**: https://sudodog.com/#pricing (web dashboard, alerts, multi-server)
4. **Star on GitHub**: https://github.com/SudoDog-official/sudodog

## Common Issues

### "sudodog: command not found"

Add to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "externally-managed-environment" error

Use the flag:
```bash
pip3 install -e . --break-system-packages
```

### "Docker is not running"

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### "Permission denied" (Docker)

```bash
sudo usermod -aG docker $USER
# Then log out and log back in
```

## Getting Help

- 🐛 **Report bugs**: https://github.com/SudoDog-official/sudodog/issues
- 💬 **Discussions**: https://github.com/SudoDog-official/sudodog/discussions  
- 📧 **Email**: support@sudodog.com
- 🌐 **Website**: https://sudodog.com

---

**Built with SudoDog? Share your experience!**

Open a discussion on GitHub or tag us on social media.
