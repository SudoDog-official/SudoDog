# SudoDog 🐕

**Secure sandbox for AI agents. Blocks dangerous operations, monitors behavior, full audit trail.**

Deploy agents safely with automatic sandboxing, behavioral monitoring, and rollback capabilities.

## The Problem

AI agents can delete databases, leak customer data, and rack up massive API bills in seconds. Traditional security tools treat agents like users—but agents aren't users. They're unpredictable, fast, and need purpose-built protection.

## The Solution

SudoDog wraps your AI agents in a secure sandbox that:
- ✅ Intercepts all system calls
- ✅ Applies security policies automatically  
- ✅ Logs every action with full audit trail
- ✅ Blocks dangerous operations before they execute
- ✅ Provides instant rollback capabilities

## How is SudoDog Different?

Unlike general-purpose sandboxing tools (Sandboxie, Firejail, Docker), SudoDog is **purpose-built for AI agents** with intelligence that understands agent behavior:

### AI-Native Security Features

| Feature | General Sandboxes | SudoDog |
|---------|------------------|---------|
| **SQL Injection Detection** | ❌ | ✅ Detects `DROP TABLE`, `DELETE FROM`, etc. |
| **Shell Command Analysis** | ❌ | ✅ Flags `rm -rf`, `curl \| bash`, etc. |
| **Behavioral Monitoring** | ❌ | ✅ Tracks patterns over time |
| **Session-Based Audit** | ❌ | ✅ Links conversations → actions |
| **Semantic Rollback** | ❌ | ✅ Undo by logical operation |
| **Network Isolation** | ⚠️ Manual | ✅ Automatic per-agent |

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
```

SudoDog doesn't just block—it **understands and explains** what happened.

## Installation
```bash
curl -sL https://sudodog.com/install.sh | bash
```

Or install from source:
```bash
git clone https://github.com/SudoDog-official/sudodog
cd sudodog
pip install -e .
```

## Quick Start

### 1. Initialize SudoDog
```bash
sudodog init
```

### 2. Run your AI agent
```bash
sudodog run python my_agent.py
```

That's it! SudoDog will monitor and protect your agent automatically.

## Usage

### Run an agent
```bash
# Run with default policy
sudodog run python agent.py

# Run with custom policy
sudodog run --policy strict python agent.py

# Run any command
sudodog run node agent.js
sudodog run ./agent.sh
```

### Check status
```bash
sudodog status
```

### View logs
```bash
sudodog logs
sudodog logs --last 20
sudodog logs --session 20251030_133048
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

## Security Policies

SudoDog comes with sensible defaults that block:
- Access to sensitive files (`/etc/shadow`, `/etc/passwd`, `.env` files, SSH keys)
- Destructive database operations (`DROP TABLE`, `DELETE FROM`, `TRUNCATE`)
- Dangerous file operations (`rm -rf /`, `chmod 777`)
- System-level changes (`mkfs`, fork bombs)
- Network exfiltration attempts

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
```
AI Agent → SudoDog → Your System
           ↓
        ✓ Pattern Analysis
        ✓ Policy Check
        ✓ Sandbox Isolation
        ✓ Log Action
        ✓ Allow/Block
```

SudoDog provides multiple layers of protection:

1. **Pre-execution Analysis** - Scans commands for dangerous patterns before execution
2. **Namespace Isolation** - Runs agents in isolated Linux namespaces (network, PID, IPC)
3. **Behavioral Monitoring** - Tracks file access and system calls during execution
4. **Audit Logging** - Records all actions with timestamps to `~/.sudodog/logs/`
5. **Rollback Support** - Creates backups of modified files for instant recovery

## Features

### ✅ Implemented

- 🔒 **Linux Namespace Sandboxing** - Network isolation, PID isolation, user namespaces
- 🛡️ **Pattern-based Blocking** - SQL injection, dangerous commands, file operations
- 👁️ **Behavioral Monitoring** - Track every file access and system call
- 📊 **Complete Audit Trail** - Immutable logs with timestamps in JSONL format
- ⏪ **File Rollback** - Automatic backups and instant recovery
- 🎯 **Security Policy Engine** - Customizable policies loaded from config
- 💻 **Rich CLI** - Beautiful colored output with multiple commands
- 📋 **Session Management** - Track and manage multiple agent sessions

### 🚧 Roadmap

- [ ] Resource limits (CPU, memory, disk I/O)
- [ ] Docker container support as alternative to namespaces
- [ ] Real-time process monitoring with psutil
- [ ] Advanced anomaly detection (excessive API calls, unusual patterns)
- [ ] Web dashboard for monitoring
- [ ] Team collaboration features
- [ ] Cloud sync for logs
- [ ] Integration with LLM providers (OpenAI, Anthropic, etc.)

## Architecture
```
┌─────────────────────────────────────────────┐
│              SudoDog CLI                    │
├─────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────┐    │
│  │   Monitor    │  │  Policy Engine   │    │
│  │              │  │                  │    │
│  │ • Logging    │  │ • Pattern Match  │    │
│  │ • Tracking   │  │ • File Checks    │    │
│  │ • Sessions   │  │ • Load Configs   │    │
│  └──────────────┘  └──────────────────┘    │
│                                             │
│  ┌──────────────┐  ┌──────────────────┐    │
│  │   Sandbox    │  │    Rollback      │    │
│  │              │  │                  │    │
│  │ • Namespaces │  │ • File Backup    │    │
│  │ • Isolation  │  │ • Restore        │    │
│  │ • unshare    │  │ • Operations     │    │
│  └──────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │    User's Command     │
        │  (Python, Node, etc)  │
        └───────────────────────┘
```

## Use Cases

### For Developers
"Deploy AI agents without fear. We'll catch the mistakes."

Test agents safely in development with automatic sandboxing that catches dangerous operations before they reach production.

### For CTOs
"AI agents with an undo button and full audit trail."

Deploy agents in production with confidence. Rollback capabilities for when things go wrong. Complete audit trail of every action.

### For Compliance
"Prove exactly what your AI did (and didn't do)."

Meet regulatory requirements with immutable logs of all agent actions. Demonstrate due diligence for auditors.

## Examples

### Block SQL Injection
```bash
$ sudodog run echo "DROP TABLE users"

🚨 BLOCKED: Command contains dangerous patterns: DROP\s+TABLE
   Command: echo DROP TABLE users
   Matched patterns: DROP\s+TABLE
```

### Sandbox with Network Isolation
```bash
$ sudodog run python agent.py

🔒 Creating sandbox environment...
Isolated: network, PID
✓ Sandboxed process started (PID: 12345)
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

- Linux (Ubuntu, Debian, Arch, Fedora, etc.)
- Python 3.8+
- `unshare` command (part of util-linux, pre-installed on most Linux systems)
- User namespace support (enabled by default on modern Linux)

## Development Status

SudoDog is currently in **beta**. Core features are working and stable:

- ✅ Pattern-based blocking
- ✅ Linux namespace sandboxing  
- ✅ Behavioral monitoring
- ✅ Audit logging
- ✅ File rollback
- ✅ Policy engine

## Contributing

SudoDog is open source! Contributions welcome.
```bash
git clone https://github.com/SudoDog-official/sudodog
cd sudodog
pip install -e .

# Run tests
python -m pytest tests/

# Test the CLI
sudodog run echo "test"
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details

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

🐕 [sudodog.com](https://sudodog.com) | [GitHub](https://github.com/SudoDog-official/sudodog)
