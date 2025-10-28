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
| **AI Anomaly Detection** | ❌ | ✅ Excessive API calls, data exfiltration |

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
curl -sL install.sudodog.com | bash
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
sudodog run python agent.py
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
```

### Pause an agent
```bash
sudodog pause <session-id>
```

### Rollback actions
```bash
sudodog rollback <session-id> --steps 10
```

## Security Policies

SudoDog comes with sensible defaults that block:
- Access to sensitive files (`/etc/shadow`, `/etc/passwd`, `.env` files)
- Destructive database operations (`DROP TABLE`, `DELETE FROM`)
- Excessive file writes
- Suspicious network connections

Customize policies in `~/.sudodog/config.json`

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

## How It Works
```
AI Agent → SudoDog → Your System
           ↓
        ✓ Intercept
        ✓ Analyze Intent
        ✓ Policy Check
        ✓ Log Action
        ✓ Allow/Block
```

SudoDog sits between your AI agent and your system, intercepting every system call, analyzing the intent, and applying security policies before execution.

## Features

- 🔒 **Automatic Sandboxing** - Isolated execution per agent
- 👁️ **Behavioral Monitoring** - Track every file access and network request
- 🛡️ **Granular Permissions** - Define exactly what agents can do
- ⏪ **Instant Rollback** - Undo mistakes with one command
- 📊 **Complete Audit Trail** - Immutable logs of every action
- ⚡ **Zero Code Changes** - Wrap existing agents, no SDK needed

## Requirements

- Linux (Ubuntu, Debian, Arch, Fedora)
- Python 3.8+
- Root access for full sandboxing features

## Development Status

SudoDog is currently in **alpha**. Core features are working but expect breaking changes.

## Roadmap

- [x] Basic CLI interface
- [x] Local logging
- [x] Pattern detection (SQL, shell commands)
- [ ] Process monitoring and sandboxing
- [ ] Security policy engine
- [ ] Rollback functionality
- [ ] Cloud sync (Production tier)
- [ ] Web dashboard (Production tier)
- [ ] Team collaboration features (Enterprise tier)

## Contributing

SudoDog is open source! Contributions welcome.
```bash
git clone https://github.com/SudoDog-official/sudodog
cd sudodog
pip install -e .
```

See [BETA_TESTING.md](BETA_TESTING.md) for testing guidelines.

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
