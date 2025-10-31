# SudoDog 🐕

**Secure sandbox for AI agents. Docker isolation, real-time monitoring, complete audit trail.**

Deploy agents safely with automatic sandboxing, behavioral monitoring, resource limits, and rollback capabilities.

## The Problem

AI agents can delete databases, leak customer data, and rack up massive API bills in seconds. Traditional security tools treat agents like users—but agents aren't users. They're unpredictable, fast, and need purpose-built protection.

## The Solution

SudoDog wraps your AI agents in a secure sandbox that:
- ✅ **Docker container isolation** - Strong sandboxing with resource limits
- ✅ **Real-time monitoring** - Background daemon tracks all agents
- ✅ **Pattern detection** - Blocks dangerous SQL and shell commands
- ✅ **Complete audit trail** - Logs every action with timestamps
- ✅ **Instant rollback** - Undo file operations by session
- ✅ **Resource limits** - CPU and memory caps per agent

## How is SudoDog Different?

Unlike general-purpose sandboxing tools (Sandboxie, Firejail, Docker), SudoDog is **purpose-built for AI agents** with intelligence that understands agent behavior:

### AI-Native Security Features

| Feature | General Sandboxes | SudoDog |
|---------|------------------|---------|
| **SQL Injection Detection** | ❌ | ✅ Detects `DROP TABLE`, `DELETE FROM`, etc. |
| **Shell Command Analysis** | ❌ | ✅ Flags `rm -rf`, `curl \| bash`, etc. |
| **Real-time Monitoring** | ❌ | ✅ Background daemon tracks CPU/memory |
| **Resource Limits** | ⚠️ Manual | ✅ Automatic per-agent (CPU, memory) |
| **Session-Based Audit** | ❌ | ✅ Links conversations → actions |
| **Semantic Rollback** | ❌ | ✅ Undo by logical operation |
| **Multi-Container Management** | ❌ | ✅ Monitor all agents from one dashboard |

### The Key Difference

**Traditional sandboxes** isolate processes at the system level—they're like putting code in a locked room.

**SudoDog** understands *agent intent*—it's like having a security guard who reads what the agent is trying to do and makes intelligent decisions.

### Example: SQL Query
```python
# Traditional sandbox
agent.run("DROP TABLE users")  # ❌ Blocked: no database access

# SudoDog  
agent.run("DROP TABLE users")  # ✅ Intercepted, analyzed, blocked
                               # 📝 Logged: "Agent attempted DROP TABLE"
                               # 🚨 Alert: "Destructive SQL detected"
                               # 📊 Daemon: Real-time stats tracked
```

SudoDog doesn't just block—it **understands and explains** what happened.

## Installation

### Quick Install
```bash
curl -sL https://sudodog.com/install.sh | bash
```

### With Docker Support (Recommended for Production)
```bash
# Install SudoDog
curl -sL https://sudodog.com/install.sh | bash

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Log out and log back in

# Initialize SudoDog
sudodog init
```

### From Source
```bash
git clone https://github.com/SudoDog-official/sudodog
cd sudodog
pip3 install -e . --break-system-packages
```

## Quick Start

### 1. Initialize SudoDog
```bash
sudodog init
```

### 2. Run your AI agent

**Basic (namespace isolation):**
```bash
sudodog run python my_agent.py
```

**Docker (stronger isolation + resource limits):**
```bash
sudodog run --docker python my_agent.py
```

**With resource limits:**
```bash
sudodog run --docker --cpu-limit 2.0 --memory-limit 1g python my_agent.py
```

### 3. Start background monitoring
```bash
# Start daemon in foreground (see logs)
sudodog daemon start --foreground

# Or start in background
sudodog daemon start

# Check status
sudodog daemon status
```

That's it! SudoDog will monitor and protect your agents automatically.

## Usage

### Run an agent
```bash
# Run with default security (namespace)
sudodog run python agent.py

# Run with Docker (stronger isolation)
sudodog run --docker python agent.py

# Run with resource limits
sudodog run --docker --cpu-limit 2.0 --memory-limit 1g python agent.py

# Run with custom policy
sudodog run --policy strict python agent.py

# Run any command
sudodog run node agent.js
sudodog run ./agent.sh
```

### Background monitoring
```bash
# Start daemon
sudodog daemon start                  # Background
sudodog daemon start --foreground     # Foreground (see logs)

# Check status (shows all running containers with stats)
sudodog daemon status

# Stop daemon
sudodog daemon stop
```

### Check status
```bash
sudodog status        # Active sessions
sudodog daemon status # Daemon + container stats
```

### View logs
```bash
sudodog logs                      # Last 10 actions
sudodog logs --last 50            # Last 50 actions
sudodog logs --session <id>       # Specific session
```

### List security policies
```bash
sudodog policies
```

### Rollback actions
```bash
# Rollback all operations in a session
sudodog rollback <session-id>

# Rollback last N operations
sudodog rollback <session-id> --steps 10
```

### Telemetry
```bash
# Enable anonymous analytics
sudodog telemetry enable

# Disable analytics
sudodog telemetry disable

# Check status
sudodog telemetry status

# See what's collected
sudodog telemetry info
```

## 📊 Telemetry & Privacy

SudoDog includes **optional anonymous telemetry** to help improve the software.

### What We Collect (When You Opt In)

- ✅ Which commands you use (e.g., `run`, `logs`, `daemon`)
- ✅ Error messages (sanitized, no file paths or personal data)
- ✅ Performance metrics (execution time)
- ✅ Threat patterns detected (helps improve detection)

### What We NEVER Collect

- ❌ Your agent code or file contents
- ❌ File paths or directory structures
- ❌ Command arguments or outputs
- ❌ API keys, credentials, or secrets
- ❌ Personally identifiable information

### Privacy-First Design

- **Opt-in only**: Disabled by default, you choose to enable it
- **Anonymous**: Uses anonymous ID only (e.g., `anon-a1b2c3d4...`)
- **Transparent**: See exactly what's collected in [TELEMETRY.md](TELEMETRY.md)
- **Respectful**: Easy to disable at any time with `sudodog telemetry disable`

**Full Privacy Policy**: [PRIVACY.md](PRIVACY.md)  
**Technical Details**: [TELEMETRY.md](TELEMETRY.md)

### Why We Collect Data

Anonymous telemetry helps us:
1. **Improve threat detection** - See what patterns users encounter
2. **Fix bugs faster** - Know which errors affect users most
3. **Prioritize features** - Build what users actually need
4. **Understand usage** - Make better product decisions

All data is anonymous and helps the entire community by improving security for everyone.

## Docker vs Namespace Isolation

| Feature | Namespace (default) | Docker (--docker) |
|---------|-------------------|-------------------|
| Isolation strength | Basic | Strong |
| Resource limits | ❌ | ✅ CPU & Memory |
| Network isolation | ⚠️ Basic | ✅ Configurable |
| Escape prevention | ⚠️ Possible | ✅ Very difficult |
| Setup required | None | Docker install |
| Speed | Fast | Slightly slower (first run) |
| Real-time monitoring | ❌ | ✅ Via daemon |

**Recommendation:** Use `--docker` for production agents, namespace for quick testing.

## Real-Time Monitoring with Daemon

The SudoDog daemon monitors all Docker containers in real-time:
```bash
# Start daemon
$ sudodog daemon start

# In another terminal, run agents
$ sudodog run --docker python agent1.py
$ sudodog run --docker python agent2.py

# Check status - see live stats!
$ sudodog daemon status

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

Features:
- **Real-time stats** - CPU and memory usage per container
- **Alert system** - Triggers when thresholds exceeded (80% CPU/memory)
- **Multi-container tracking** - See all agents at once
- **Alert history** - Logged to `~/.sudodog/alerts.jsonl`

## Security Policies

SudoDog comes with sensible defaults that detect:
- Access to sensitive files (`/etc/shadow`, `/etc/passwd`, `.env` files, SSH keys)
- Destructive database operations (`DROP TABLE`, `DELETE FROM`, `TRUNCATE`)
- Dangerous file operations (`rm -rf /`, `chmod 777`)
- System-level changes (`mkfs`, fork bombs)
- Dangerous shell patterns (`curl | bash`, `wget | sh`)

### Custom Policies

Create custom policies in `~/.sudodog/config.json`:
```json
{
  "policies": {
    "strict": {
      "block_patterns": [
        "DROP\\s+TABLE",
        "DELETE\\s+FROM",
        "rm\\s+-rf",
        "curl",
        "wget",
        "eval"
      ],
      "allow_network": false,
      "max_file_writes": 10
    },
    "permissive": {
      "block_patterns": [
        "DROP\\s+TABLE",
        "rm\\s+-rf\\s+/"
      ],
      "allow_network": true,
      "max_file_writes": 1000
    }
  }
}
```

Then use your custom policy:
```bash
sudodog run --policy strict python agent.py
```

## How It Works

### Architecture
```
AI Agent → SudoDog CLI → Docker Container
              ↓              ↓
        Pattern Analysis   Isolated Execution
        Policy Check       Resource Limits
        Daemon Monitoring  Network Isolation
        Audit Logging      
              ↓
        Allow/Block Decision
```

SudoDog provides multiple layers of protection:

1. **Pre-execution Analysis** - Scans commands for dangerous patterns before execution
2. **Container Isolation** - Runs agents in isolated Docker containers with resource limits
3. **Real-time Monitoring** - Background daemon tracks CPU, memory, and alerts on thresholds
4. **Behavioral Monitoring** - Tracks file access and system calls during execution
5. **Audit Logging** - Records all actions with timestamps to `~/.sudodog/logs/`
6. **Rollback Support** - Creates backups of modified files for instant recovery

### System Architecture
```
┌─────────────────────────────────────────────────┐
│            SudoDog Daemon (Background)          │
│  - Real-time container monitoring               │
│  - CPU/Memory tracking                          │
│  - Alert system                                 │
│  - Multi-container management                   │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│              SudoDog CLI                        │
├─────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────┐        │
│  │   Monitor    │  │  Policy Engine   │        │
│  │              │  │                  │        │
│  │ • Logging    │  │ • Pattern Match  │        │
│  │ • Tracking   │  │ • File Checks    │        │
│  │ • Sessions   │  │ • Load Configs   │        │
│  └──────────────┘  └──────────────────┘        │
│                                                 │
│  ┌──────────────┐  ┌──────────────────┐        │
│  │Docker Sandbox│  │    Rollback      │        │
│  │              │  │                  │        │
│  │ • Containers │  │ • File Backup    │        │
│  │ • Isolation  │  │ • Restore        │        │
│  │ • Resources  │  │ • Operations     │        │
│  └──────────────┘  └──────────────────┘        │
└─────────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   Docker Containers   │
        │  Agent 1 | Agent 2    │
        │  (isolated, limited)  │
        └───────────────────────┘
```

## Features

### ✅ Production Ready

- 🐳 **Docker Container Isolation** - Strong isolation with full filesystem separation
- 💪 **Resource Limits** - CPU and memory caps per agent
- 👁️ **Background Daemon** - Real-time monitoring of all containers
- 📊 **Real-time Stats** - Live CPU/Memory tracking with alerts
- 🛡️ **Pattern-based Detection** - SQL injection, dangerous commands, file operations
- 👁️ **Behavioral Monitoring** - Track every file access and system call
- 📋 **Complete Audit Trail** - Immutable logs with timestamps in JSONL format
- ⏪ **File Rollback** - Automatic backups and instant recovery
- 🎯 **Security Policy Engine** - Customizable policies loaded from config
- 💻 **Rich CLI** - Beautiful colored output with multiple commands
- 📝 **Session Management** - Track and manage multiple agent sessions
- 🔒 **Namespace Sandboxing** - Lightweight alternative to Docker
- 📊 **Anonymous Telemetry** - Optional usage analytics (opt-in, privacy-first)

## Use Cases

### For Developers
"Deploy AI agents without fear. We'll catch the mistakes."

Test agents safely in development with automatic sandboxing that catches dangerous operations before they reach production.

### For CTOs
"AI agents with an undo button and full audit trail."

Deploy agents in production with confidence. Docker isolation, resource limits, and real-time monitoring. Rollback capabilities for when things go wrong.

### For Compliance
"Prove exactly what your AI did (and didn't do)."

Meet regulatory requirements with immutable logs of all agent actions. Demonstrate due diligence for auditors.

## Examples

### Block Dangerous Commands
```bash
$ sudodog run echo "DROP TABLE users"

🐕 SudoDog AI Agent Security
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Checking command for dangerous patterns...
🚨 BLOCKED: Command contains dangerous patterns
   Command: echo DROP TABLE users
   Matched patterns: DROP TABLE

Total actions: 2
Blocked actions: 1
```

### Docker Sandbox with Resource Limits
```bash
$ sudodog run --docker --cpu-limit 2.0 --memory-limit 1g python agent.py

🐕 SudoDog AI Agent Security
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐳 Using Docker sandbox
🐳 Creating Docker container...
   Network: enabled
   CPU limit: 2.0 cores
   Memory limit: 1g
✓ Container created: d2dcfb3e93d6
▶ Starting container d2dcfb3e93d6...
✓ Container running

[Agent output...]

✓ Container exited with code 0
CPU: 15.3% | Memory: 245.8MB
```

### Real-Time Monitoring
```bash
$ sudodog daemon start --foreground

✓ SudoDog daemon started (PID: 95100)
Monitoring interval: 5s

[Monitoring containers in real-time...]

$ sudodog daemon status

✓ Daemon is running (PID: 95100)
Last check: 2025-10-30T16:42:40.984222
Active containers: 1

┌─────────────┬──────────────────┬───────┬──────────┬────────┐
│ Container   │ Session          │ CPU%  │ Memory%  │ Alerts │
├─────────────┼──────────────────┼───────┼──────────┼────────┤
│ c3b2d252a7e8│ 20251030_164230  │ 2.3   │ 15.4     │ 0      │
└─────────────┴──────────────────┴───────┴──────────┴────────┘
```

### Rollback File Changes
```bash
$ sudodog run ./modify_files.sh
# ... agent modifies files ...

$ sudodog rollback 20251030_133048
⏪ Rolling back actions...
✓ Successfully rolled back 3 file operation(s)
```

## Requirements

### Basic Requirements
- Linux (Ubuntu, Debian, Arch, Fedora, etc.)
- Python 3.8+

### For Docker Support (Recommended)
- Docker 20.10+
- User added to `docker` group

### For Namespace Mode
- `unshare` command (part of util-linux, pre-installed on most Linux systems)
- User namespace support (enabled by default on modern Linux)

## Development Status

SudoDog is currently in **production beta**. Core features are working and stable:

- ✅ Docker container isolation
- ✅ Real-time monitoring daemon
- ✅ Resource limits (CPU, memory)
- ✅ Pattern-based detection
- ✅ Namespace sandboxing  
- ✅ Behavioral monitoring
- ✅ Audit logging
- ✅ File rollback
- ✅ Policy engine
- ✅ Anonymous telemetry (opt-in)

## Contributing

SudoDog is open source! Contributions welcome.
```bash
git clone https://github.com/SudoDog-official/sudodog
cd sudodog
pip3 install -e . --break-system-packages

# Test the CLI
sudodog init
sudodog run --docker python -c "print('Hello from Docker!')"
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Documentation

- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for a 5-minute guide
- **Privacy Policy**: [PRIVACY.md](PRIVACY.md)
- **Telemetry Details**: [TELEMETRY.md](TELEMETRY.md)
- **Examples**: See `examples/` directory for sample agents
- **Website**: [sudodog.com](https://sudodog.com)

## License

MIT License with Telemetry Addendum - see [LICENSE](LICENSE) file for details.

TL;DR: Fully open source, but forks must maintain the same privacy transparency if they keep telemetry.

## Support

- 🐛 [Report Issues](https://github.com/SudoDog-official/sudodog/issues)
- 💬 [Discussions](https://github.com/SudoDog-official/sudodog/discussions)
- 🌐 [Website](https://sudodog.com)

## Contact

- **Support**: support@sudodog.com
- **Security Issues**: security@sudodog.com  
- **General Inquiries**: contact@sudodog.com
- **GitHub Issues**: https://github.com/SudoDog-official/sudodog/issues

---

**Built for developers who value security without complexity.**

🐕 [sudodog.com](https://sudodog.com) | [GitHub](https://github.com/SudoDog-official/sudodog) | [Docs](https://sudodog.com/docs)
