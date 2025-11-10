# SudoDog 🐕

**Secure sandbox for AI agents. Blocks dangerous operations, monitors behavior, full audit trail.**

Monitor all your AI agents in one place. Real-time visibility, complete audit trail, framework-agnostic.

## Features

### Core Security
- ✅ **Zero integration** - No code changes, no imports, just prepend a command
- ✅ **Real-time monitoring** - See all agents with live CPU and memory stats
- ✅ **Complete audit trail** - Logs every action with timestamps
- ✅ **Pattern detection** - Detects dangerous SQL and shell commands
- ✅ **Framework-agnostic** - Works with LangChain, AutoGPT, CrewAI, custom agents
- ✅ **Docker isolation** - Run agents in isolated containers with custom images
- ✅ **Resource monitoring** - Track and limit CPU and memory per agent

### Advanced Security Features 🆕
- ✅ **HTTP Traffic Monitoring** - Capture all API calls with automatic provider detection
- ✅ **Rate Limit Protection** - Track API usage and warn before hitting limits
- ✅ **Secret Management** - Securely inject API keys and credentials into agents
- ✅ **AI Decision Tracking** - Log all LLM prompts, responses, and reasoning for audit

## Quick Start

### Installation
```bash
# Quick install
curl -sL https://sudodog.com/install.sh | bash

# Or from source
git clone https://github.com/SudoDog-official/SudoDog
cd SudoDog
pip install -e .
```

### Basic Usage
```bash
# Initialize SudoDog
sudodog init

# Run any agent with monitoring (HTTP tracking is automatic!)
sudodog run python my_agent.py

# Run with Docker isolation
sudodog run --docker python my_agent.py

# Run with custom image
sudodog run --docker --image my-agent:latest python agent.py

# Run with resource limits
sudodog run --docker --cpu-limit 2.0 --memory-limit 1g python my_agent.py
```

## Framework Support

### LangChain
```bash
sudodog run python langchain_agent.py
```

### AutoGPT
```bash
sudodog run python -m autogpt
```

### CrewAI
```bash
sudodog run python crewai_agent.py
```

### Any Framework
```bash
sudodog run node agent.js      # Node.js
sudodog run ruby agent.rb      # Ruby
sudodog run ./agent.sh         # Bash script
```

## New Features

### 🌐 HTTP Traffic Monitoring

**Automatically captures all API calls** made by your agents with zero configuration:
```bash
# View recent HTTP traffic
sudodog http

# Filter by provider
sudodog http --provider openai

# Show last 50 requests
sudodog http --last 50

# Show only errors
sudodog http --errors-only

# View for specific session
sudodog http --session 20251110_123456

# Get statistics
sudodog http-stats
```

**Example output:**
```
🌐 HTTP Traffic Logs
────────────────────────────────────────

[15:18:22] [OPENAI] POST https://api.openai.com/v1/chat/completions
  ↳ 200 1234ms

[15:18:25] [ANTHROPIC] POST https://api.anthropic.com/v1/messages
  ↳ 200 2456ms

[15:18:30] [OPENAI] POST https://api.openai.com/v1/embeddings
  ↳ 429 892ms - Rate limit exceeded
```

**Features:**
- ✅ Automatic provider detection (OpenAI, Anthropic, Google, Cohere, HuggingFace, Replicate)
- ✅ Redacts sensitive data (API keys, tokens, passwords)
- ✅ Tracks request/response timing
- ✅ Logs status codes and errors
- ✅ JSONL format for easy parsing
- ✅ Works with `requests`, `urllib3`, and `httpx` libraries

**Log Location:** `~/.sudodog/logs/{session_id}_http.jsonl`

### 📊 Rate Limit Protection

**Tracks API usage and warns before hitting provider limits:**
```bash
# Check rate limit status for all providers
sudodog http-stats

# Get detailed usage for specific session
sudodog http-stats 20251110_123456
```

**Example output:**
```
📊 HTTP Traffic Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Requests: 145
Errors: 2
Avg Duration: 1234ms

By Provider:
  • openai: 98 requests
  • anthropic: 45 requests
  • google: 2 requests

By Status Code:
  • 200: 143
  • 429: 2
```

**Built-in Rate Limits:**

| Provider | Requests/Min | Tokens/Min | Requests/Day |
|----------|--------------|------------|--------------|
| OpenAI GPT-4 | 500 | 30,000 | 10,000 |
| OpenAI GPT-3.5 | 3,500 | 90,000 | 10,000 |
| Anthropic Claude-3-Opus | 1,000 | 80,000 | 50,000 |
| Anthropic Claude-3-Sonnet | 2,000 | 160,000 | 100,000 |
| Google AI | 60 | 32,000 | 1,500 |
| Cohere | 100 | 40,000 | 10,000 |
| HuggingFace | 30 | 10,000 | 1,000 |

**Programmatic Usage:**
```python
from sudodog.rate_limit_tracker import RateLimitTracker

tracker = RateLimitTracker()

# Check usage for a provider
usage = tracker.analyze_usage('openai', time_window='minute')
print(f"OpenAI: {usage['requests']}/{usage['limit']} requests ({usage['usage_percent']}%)")

# Get warnings
warning = tracker.check_limit_warnings('openai')
if warning:
    print(warning)  # "⚠️ WARNING: OpenAI at 85% of rate limit"

# Set custom limits
tracker.set_custom_limit('openai', 'rpm', 1000)
```

### 🔐 Secret Management

Securely inject API keys and credentials into your agents:
```python
from sudodog.secret_manager import SecretManager

# Initialize
sm = SecretManager()

# Load secrets from JSON file
secrets = sm.load_secrets_from_file('secrets.json')

# Inject into container (returns environment variables)
env_vars = sm.inject_secrets(secrets, container_id='agent123')

# Mask secrets for safe logging
masked = sm.mask_secret('sk-1234567890abcdef', show_chars=4)
# Output: sk-1***************

# Get usage statistics
stats = sm.get_secret_stats()
```

**secrets.json format:**
```json
{
  "OPENAI_API_KEY": "sk-your-key-here",
  "ANTHROPIC_API_KEY": "sk-ant-your-key",
  "DATABASE_URL": "postgresql://user:pass@host:5432/db"
}
```

**Security Features:**
- ✅ Validates secret names and values
- ✅ Masks secrets in logs (never shows full values)
- ✅ Complete audit trail of all secret access
- ✅ Statistics tracking (injection count, last access)
- ✅ Automatic fallback to `~/.sudodog/logs/` if `/var/log/sudodog/` not writable

**Log Location:** `~/.sudodog/logs/secrets.log`

### 📝 AI Decision Tracking

Track all LLM decisions with complete audit trail:
```python
from sudodog.ai_decision_tracker import AIDecisionTracker

# Initialize
tracker = AIDecisionTracker()

# Log an AI decision
decision_id = tracker.log_decision(
    prompt="Should I allow: rm -rf /tmp/test",
    response="Safe - only deleting /tmp",
    model="gpt-4",
    reasoning="Temporary directory deletion is safe",
    command_analyzed="rm -rf /tmp/test",
    risk_level="low",
    action_taken="allowed"
)

# Get statistics
stats = tracker.get_statistics()
# Returns: total_decisions, risk_level_breakdown, action_breakdown, model_usage

# Analyze patterns
patterns = tracker.analyze_patterns()
# Returns: high_risk_commands, blocked_commands, common_reasoning

# Export report
tracker.export_report('/tmp/report.json', format='json')
tracker.export_report('/tmp/report.txt', format='text')
```

**Features:**
- ✅ JSONL-based append-only logging (tamper-evident)
- ✅ Unique decision IDs for each decision
- ✅ Captures prompt, response, reasoning, risk level, action taken
- ✅ Statistical analysis and pattern detection
- ✅ Export reports in JSON or text format
- ✅ Automatic fallback to user home directory

**Log Location:** `~/.sudodog/logs/ai_decisions.jsonl`

## Daemon Mode

Monitor multiple agents in real-time:
```bash
# Start daemon
sudodog daemon start

# Check status with live stats
sudodog daemon status

# Example output:
# ✓ Daemon is running (PID: 95100)
# Active containers: 2
#
# ┌─────────────┬──────────────────┬───────┬──────────┬────────┐
# │ Container   │ Session          │ CPU%  │ Memory%  │ Alerts │
# ├─────────────┼──────────────────┼───────┼──────────┼────────┤
# │ c3b2d252a7e8│ 20251031_164230 │  2.3  │   15.4   │   0    │
# │ a1b3c4d5e6f7│ 20251031_164301 │ 45.8  │   78.2   │   1    │
# └─────────────┴──────────────────┴───────┴──────────┴────────┘
```

## Management Commands
```bash
# View logs
sudodog logs                    # Last 10 actions
sudodog logs --last 50          # Last 50 actions
sudodog logs --session <id>     # Specific session

# HTTP traffic
sudodog http                    # Recent HTTP traffic
sudodog http --provider openai  # Filter by provider
sudodog http-stats              # Usage statistics

# Check status
sudodog status                  # Active sessions
sudodog daemon status           # Daemon + container stats

# Rollback operations
sudodog rollback <session-id>           # Rollback all
sudodog rollback <session-id> --steps 10 # Rollback last 10

# Security policies
sudodog policies                # List policies
sudodog run --policy strict python agent.py
```

## Custom Docker Images

Create custom images with your dependencies:
```dockerfile
FROM python:3.11-slim

# Install dependencies
RUN pip install langchain openai anthropic requests

WORKDIR /app
```
```bash
docker build -t my-agent:latest .
sudodog run --docker --image my-agent:latest python agent.py
```

See `examples/dockerfiles/` for templates.

## Security Policies

SudoDog comes with built-in protection against:
- Access to sensitive files (`/etc/shadow`, `/etc/passwd`, `.env` files, SSH keys)
- Destructive database operations (`DROP TABLE`, `DELETE FROM`, `TRUNCATE`)
- Dangerous file operations (`rm -rf /`, `chmod 777`)
- System-level changes (`mkfs`, fork bombs)
- Dangerous shell patterns (`curl | bash`, `wget | sh`)

Custom policies in `~/.sudodog/config.json`:
```json
{
  "policies": {
    "strict": {
      "block_patterns": [
        "DROP\\s+TABLE",
        "DELETE\\s+FROM",
        "rm\\s+-rf",
        "curl",
        "wget"
      ],
      "allow_network": false,
      "max_file_writes": 10
    }
  }
}
```

## Architecture
```
AI Agent → SudoDog CLI → Docker Container
    ↓           ↓              ↓
HTTP        Secret        Isolated
Intercept   Injection     Execution
    ↓           ↓              ↓
Rate        Decision      Resource
Tracking    Logging       Limits
    ↓           ↓              ↓
Pattern     Audit         Network
Analysis    Trail         Isolation
    ↓
Daemon Monitoring
```

**Security Layers:**
1. HTTP traffic interception with provider detection
2. Rate limit tracking and warnings
3. Pre-execution pattern analysis
4. Container isolation with resource limits
5. Secret management with audit trail
6. Real-time monitoring via daemon
7. AI decision tracking for compliance
8. Behavioral monitoring during execution
9. Rollback support for recovery

## Comparison

| Feature | LangSmith | Helicone | Datadog | SudoDog |
|---------|-----------|----------|---------|---------|
| Framework-Agnostic | ❌ LangChain only | ✅ | ✅ | ✅ |
| Zero Integration | ❌ Code changes | ✅ | ❌ | ✅ |
| HTTP Monitoring | ❌ | ✅ API only | ✅ | ✅ All traffic |
| Rate Limit Tracking | ❌ | ✅ | ❌ | ✅ |
| Security Patterns | ❌ | ❌ | ❌ | ✅ |
| Secret Management | ❌ | ❌ | ❌ | ✅ |
| AI Decision Tracking | ❌ | ❌ | ❌ | ✅ |
| Resource Monitoring | ❌ | ❌ | ✅ | ✅ |
| Real-time Dashboard | ✅ Web | ✅ Web | ✅ Web | ✅ CLI |

## Privacy & Telemetry

SudoDog includes optional anonymous telemetry (disabled by default):
```bash
sudodog telemetry enable    # Opt-in
sudodog telemetry disable   # Opt-out
sudodog telemetry status    # Check status
```

See [TELEMETRY.md](TELEMETRY.md) and [PRIVACY.md](PRIVACY.md) for details.

## Requirements

- Linux (Ubuntu, Debian, Arch, Fedora, etc.)
- Python 3.8+
- Docker 20.10+ (optional, for stronger isolation)

## Documentation

- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Privacy Policy:** [PRIVACY.md](PRIVACY.md)
- **Telemetry:** [TELEMETRY.md](TELEMETRY.md)
- **Examples:** `examples/dockerfiles/`
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- **Issues:** [GitHub Issues](https://github.com/SudoDog-official/SudoDog/issues)
- **Email:** support@sudodog.com
- **Security:** security@sudodog.com

## License

MIT License - see [LICENSE](LICENSE) file.

---

**Built for developers who value security without complexity.**

🐕 [sudodog.com](https://sudodog.com) | [GitHub](https://github.com/SudoDog-official/SudoDog) | v0.2.0
