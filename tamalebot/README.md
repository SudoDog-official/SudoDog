# TamaleBot

Security-first AI agent platform. Isolated agents, any cloud, full audit trail.

## What is TamaleBot?

TamaleBot is an open-core AI agent platform where:
- Every agent runs in its own isolated Docker container
- Every tool call passes through a security policy engine before execution
- Every action is logged to an append-only audit trail
- Agents deploy to Cloudflare, AWS, GCP, or self-hosted Docker
- You can migrate between clouds with one command

## Quick Start

```bash
# Install
npm install -g tamalebot

# Initialize config
tamalebot init

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run any command with security policies applied
tamalebot run python my_agent.py

# Check what would be blocked (without executing)
tamalebot run --dry-run "rm -rf /"
# => BLOCKED: Command contains dangerous patterns: rm\s+-rf\s+/
```

## Security Engine

TamaleBot intercepts every tool call before execution:

```
Agent wants to run: rm -rf /tmp/workspace
                    |
                    v
          +-------------------+
          | Policy Engine     |
          |                   |
          | 1. Check command  | --> "rm -rf /" pattern? No, /tmp is OK
          | 2. Check paths    | --> /tmp is not a system directory
          | 3. Check domain   | --> N/A (not an HTTP request)
          | 4. Log decision   | --> audit trail entry written
          +-------------------+
                    |
                    v
          Command executes (ALLOWED)
```

What gets blocked by default:
- Destructive commands: `rm -rf /`, `DROP TABLE`, `chmod 777`
- Sensitive file reads: `~/.ssh/id_rsa`, `~/.aws/credentials`, `.env`
- System directory writes: `/etc/`, `/usr/bin/`, `/boot/`
- Data exfiltration: `curl pastebin`, `wget ngrok`

## Architecture

```
CLI (tamalebot run)
  |
  v
Security Policy Engine ──> Audit Trail (JSONL)
  |
  v
Agent Runtime (Docker container)
  |
  +── LLM Connection (Anthropic, OpenAI, Google)
  +── Integrations (Telegram, Slack, Email via MCP)
  +── Storage (R2/S3/MinIO — S3-compatible API)
```

## Open Core Licensing

| Open Source (Apache 2.0) | Proprietary (Dashboard) |
|---|---|
| Security policy engine | Web dashboard UI |
| Audit trail | Multi-agent orchestration |
| Secret manager | Fleet management |
| CLI tools | Billing & metering |
| Agent runtime | Advanced analytics |
| All integrations | SSO / SAML |
| Migration tools | |

Every line of code that processes your messages, API calls, and files is open source. The closed-source parts are the management UI — they never see your data.

## Project Status

TamaleBot is in early development. See the [architecture doc](./docs/ARCHITECTURE.md) for the full vision.

**Phase 1** (current): Single-agent CLI with security engine, Telegram integration, Cloudflare deployment.

## License

Apache 2.0 — see [LICENSE](./LICENSE).
