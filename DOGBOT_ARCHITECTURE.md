# DogBot: Architecture & Product Vision

**Date:** February 2026
**Status:** Planning

---

## One-Line Pitch

DogBot is a security-first AI agent platform where every agent runs in an isolated sandbox, deploys to any cloud (starting with Cloudflare), and is managed from a single dashboard — no Mac Mini required.

---

## The Three Big Ideas

### 1. Seamless Agent Spawning
A user clicks "New Agent" in the dashboard, picks a task template (email assistant, research bot, scheduler, etc.), connects their accounts, and a new isolated worker spins up devoted to that task. Each agent is sandboxed from every other agent. One agent getting prompt-injected cannot compromise the others.

### 2. Cloud-Portable (Not Cloudflare-Locked)
SudoDog becomes the management layer that can deploy agents to Cloudflare, AWS, GCP, or self-hosted Docker. If Cloudflare builds a competing product, users migrate with one command. The dashboard is the product — the cloud is interchangeable.

### 3. iMessage Without a Mac Mini (Sort Of)
An honest approach: a lightweight companion app on the user's iPhone that relays iMessages to DogBot via a secure WebSocket. Not an Apple protocol hack — an app the user installs and authorizes.

---

## Architecture Overview

```
+----------------------------------------------------------+
|                   DogBot Dashboard                        |
|              (Web UI — Next.js on CF Pages)               |
|                                                           |
|  +----------+ +----------+ +----------+ +----------+     |
|  | Agent 1  | | Agent 2  | | Agent 3  | | Agent N  |     |
|  | Email    | | Research | | Slack    | | Custom   |     |
|  +----+-----+ +----+-----+ +----+-----+ +----+-----+     |
+-------|-------------|-------------|-------------|----------+
        |             |             |             |
+-------v-------------v-------------v-------------v---------+
|                 Orchestration API                          |
|           (Durable Object / Rivet Actor)                  |
|                                                           |
|  - Agent registry & lifecycle                             |
|  - Routing & auth                                         |
|  - Security policy engine (from SudoDog)                  |
|  - Audit trail                                            |
|  - Billing metering                                       |
+-------------------------+---------------------------------+
                          |
          +---------------+----------------+
          |               |                |
+---------v--+  +---------v--+  +----------v-+
| Cloudflare |  | AWS ECS /  |  | Self-hosted|
| Container  |  | Fargate    |  | Docker     |
+------------+  +------------+  +------------+
     |               |                |
     +-------+-------+-------+-------+
             |               |
      +------v------+  +----v------+
      | S3-compat   |  | Postgres  |
      | Storage     |  | / SQLite  |
      | (R2/S3/     |  | (state)   |
      |  MinIO)     |  |           |
      +-------------+  +-----------+
```

---

## Component Breakdown

### 1. Dashboard (the product users see)

**Tech:** Next.js deployed on Cloudflare Pages (or Vercel, or self-hosted)

**What it does:**
- User signup/login (Clerk or Lucia auth)
- "New Agent" wizard — pick template, connect accounts, configure permissions
- Per-agent controls: start/stop/restart, view logs, audit trail
- Security policy editor: what each agent can and cannot do
- Fleet view: all agents at a glance, resource usage, alerts
- Billing: usage-based metering per agent
- **Migration wizard**: one-click export agent configs + state to another provider

**Key design principle:** The dashboard is provider-agnostic. It talks to agents via a standard HTTP/WebSocket API regardless of where they run. Switching clouds means changing the deployment target, not the dashboard.

### 2. Orchestration Layer (the brain)

**Tech:** TypeScript, runs as a Durable Object on Cloudflare OR as a Rivet Actor on any cloud OR as a plain Express server on Docker

**What it does:**
- Maintains agent registry (name, provider, endpoint, status, health)
- Routes messages from integrations to the correct agent
- Enforces security policies BEFORE tool calls execute
- Logs every LLM decision and tool invocation to audit trail
- Handles agent lifecycle: create, start, stop, destroy, migrate
- Rate limiting per agent (API calls, cost caps)

**Portability strategy:** Use [Rivet Actors](https://rivet.dev/) as the stateful primitive. Rivet provides the same actor model as Cloudflare Durable Objects but runs on any infrastructure (Kubernetes, AWS, VPS, Rivet Cloud, or Cloudflare Workers). This means the orchestration layer is genuinely portable — same TypeScript code, different deployment target.

**Security policy engine (ported from SudoDog):**
```
Before every tool call:
  1. Check command against blocked patterns (rm -rf, DROP TABLE, etc.)
  2. Check file paths against read/write allowlists
  3. Check HTTP destination against domain allowlist
  4. Check rate limits (per-agent, per-provider)
  5. Mask secrets in all logs
  6. Log the decision (allowed/blocked + reasoning)
  7. If blocked: notify user via dashboard, do NOT execute
```

### 3. Agent Runtime (where agents actually execute)

**Tech:** Docker container running a TypeScript agent process

**Why Docker (not raw Workers):**
- AI agents need filesystem access (workspace for generated files)
- Agents need shell execution (running code, scripts)
- Agents may need browser automation (headless Chrome)
- Docker images are portable across ALL cloud providers
- 128MB Worker memory limit is too tight for complex agent tasks

**Container contents:**
```dockerfile
FROM node:22-slim

# Headless Chrome for browser automation
RUN apt-get update && apt-get install -y chromium

# Agent runtime
COPY agent-runtime/ /app/
WORKDIR /app

# SudoDog security policies (baked in)
COPY security-policies/ /app/policies/

# No root, no host access, no privilege escalation
USER node
ENTRYPOINT ["node", "agent.js"]
```

**Per-agent isolation:**
- Each agent runs in its own container
- No shared filesystem between agents
- Network egress controlled by security policies
- API keys injected as environment variables (never visible to the agent logic)
- Container has no access to dashboard secrets or other agents' state

**Deployment targets:**

| Target | How | Scale-to-Zero | Cost/Agent |
|--------|-----|---------------|------------|
| Cloudflare Containers | Wrangler deploy via Workers | Yes | ~$10-20/mo active |
| AWS Fargate | ECS task definition via Pulumi | No (min 1 task) | ~$15-30/mo |
| GCP Cloud Run | Container image via Pulumi | Yes | ~$8-25/mo |
| Self-hosted Docker | docker-compose or K8s | N/A | VPS cost only |
| Coolify (self-hosted PaaS) | Git push deploy | N/A | ~$5/mo VPS |

### 4. Integration Layer (how agents talk to the world)

**Start with 5 integrations, not 50:**

| Integration | Method | Complexity |
|-------------|--------|------------|
| **Email (Gmail/Outlook)** | OAuth + webhook push notifications | Medium |
| **Slack** | Slack app with webhook events | Low |
| **Telegram** | Bot API with webhooks | Low |
| **Web browsing** | Headless Chrome in container | Medium |
| **Calendar (Google)** | OAuth + REST API | Low |

**Protocol:** Each integration is an MCP (Model Context Protocol) server. The agent connects to integrations via MCP, which means:
- Standard protocol — any MCP-compatible tool works
- Users can add custom MCP servers for their own APIs
- Integrations are swappable without changing agent code

### 5. iMessage Bridge (the honest approach)

**The reality:** There is NO way to access iMessage without Apple hardware. Every hack (pypush, Beeper Mini, jailbreak bridges) has been killed by Apple. The only reliable options require a Mac.

**DogBot's approach: a two-tier strategy**

**Tier 1: "DogBot Relay" iOS App (no Mac needed)**
```
iPhone                          DogBot Cloud
+------------------+            +------------------+
| DogBot Relay App |<---------->| Agent Container  |
|                  |  Secure    |                  |
| - Monitors       |  WebSocket | - Sends message  |
|   notification   |            |   instructions   |
|   center         |            |   to the app     |
| - Uses iOS       |            | - Receives       |
|   Shortcuts      |            |   notification   |
|   automation     |            |   content        |
| - Relays message |            |                  |
|   metadata       |            |                  |
+------------------+            +------------------+
```

**What it CAN do (without jailbreak):**
- Detect incoming message notifications (sender, preview text if enabled)
- Trigger iOS Shortcuts automations based on message arrival
- Send user-approved responses via Shortcuts "Send Message" action
- Relay notification metadata to DogBot via webhook

**What it CANNOT do:**
- Read full message history
- Send messages silently without user confirmation (iOS requires tap-to-confirm)
- Access message attachments
- Work when the phone is off or has no internet

**Honest marketing:** "DogBot can monitor your iMessages and suggest responses — but you tap to send. Full automation requires a Mac."

**Tier 2: Mac Relay (for users who want full automation)**
- If the user has ANY Mac (even a $50 used Mac Mini), DogBot installs a lightweight relay daemon
- Uses OpenBubbles (open source) as the iMessage bridge
- Full read/write iMessage access, group chats, reactions, attachments
- The Mac can be remote — DogBot connects via WebSocket
- OpenBubbles has a one-time Mac setup; after registration, the Mac can go offline and OpenBubbles maintains the iMessage connection from DogBot's cloud

**Tier 3: RCS Fallback (for Android users messaging iPhone users)**
- iOS 18+ supports RCS with read receipts, typing indicators, high-res media
- If the recipient is on Android, DogBot can use RCS via the messaging API
- No blue bubbles, but functional rich messaging
- End-to-end encrypted RCS expected in iOS 26.4 (mid-2026)

---

## Seamless Agent Creation Flow

```
User clicks "New Agent"
        |
        v
Pick template:
  - Email Assistant
  - Research Bot
  - Slack Responder
  - Calendar Manager
  - Custom (blank)
        |
        v
Connect accounts:
  - OAuth flow for Gmail, Slack, Google Calendar
  - API key input for LLM provider (OpenAI, Anthropic, etc.)
  - Optional: iMessage via DogBot Relay app
        |
        v
Set security policy:
  - What can this agent access? (email read, email send, web browse, etc.)
  - Cost cap per month ($5, $20, $50, unlimited)
  - Approval mode: auto-execute vs. ask-before-acting
        |
        v
Choose deployment:
  - Cloudflare (recommended — fastest, cheapest)
  - AWS
  - Self-hosted
        |
        v
DogBot provisions:
  1. New Docker container (isolated agent runtime)
  2. New state store (per-agent SQLite or Postgres row)
  3. New R2/S3 bucket partition (per-agent file storage)
  4. New MCP connections to selected integrations
  5. Security policy applied to orchestration layer
  6. Agent appears in dashboard, status: running
        |
        v
Agent is live. User interacts via:
  - Dashboard chat interface
  - Telegram bot
  - Slack DM
  - Email
  - iMessage (via Relay app)
```

**Each new agent = a new isolated container.** No shared state, no shared secrets, no shared network. If agent 3 gets prompt-injected via a malicious email, it cannot access agent 1's Slack credentials or agent 2's calendar.

---

## Migration Strategy (the anti-lock-in play)

This is the key differentiator against Cloudflare just building this themselves.

### What "migration" means:

```
sudodog migrate --from cloudflare --to aws

What happens:
  1. Export all agent configs (JSON)
  2. Export all agent state (SQLite dumps)
  3. Export all agent files (R2 → S3 sync)
  4. Provision equivalent infrastructure on AWS via Pulumi
  5. Deploy same Docker images to ECS/Fargate
  6. Update DNS / routing to point to new endpoints
  7. Verify agents are healthy on new provider
  8. Tear down Cloudflare resources
```

### How this is technically possible:

| Component | Cloudflare | AWS | Self-hosted | Abstraction |
|-----------|-----------|-----|-------------|-------------|
| Compute | CF Containers | ECS Fargate | Docker | Standard Docker images |
| State | Durable Objects | DynamoDB | PostgreSQL | Rivet Actors (portable) |
| Files | R2 | S3 | MinIO | S3-compatible API |
| Routing | CF Workers | API Gateway | Nginx/Caddy | HTTP API standard |
| Auth | CF Zero Trust | Cognito | Lucia/Clerk | OAuth standard |
| IaC | Pulumi CF provider | Pulumi AWS provider | Pulumi Docker provider | Pulumi (all providers) |

### The sales pitch:
> "Other platforms lock you into their cloud. DogBot runs on Cloudflare today because it's the best value. But if Cloudflare raises prices, builds a competitor, or you need to move to AWS for compliance — `sudodog migrate` moves everything in minutes. Your agents, your data, your rules."

---

## Monetization Model

### Free Tier
- 1 agent
- Cloudflare deployment only
- 100 LLM calls/day (BYOK — user's own API keys)
- Community support
- Full security policies and audit trail

### Pro ($29/month)
- 5 agents
- Any cloud deployment
- Unlimited LLM calls (BYOK)
- Priority support
- Migration tools
- iMessage Relay app access

### Team ($79/month)
- 20 agents
- Multi-user dashboard
- Shared agent templates
- SSO / SAML
- API access for custom integrations

### Enterprise (custom)
- Unlimited agents
- Self-hosted option
- Dedicated support
- Custom security policies
- Compliance reporting (SOC 2, GDPR)
- SLA

### Why this works:
- Users bring their own LLM API keys — DogBot doesn't eat API costs
- Cloudflare's scale-to-zero means idle agents cost DogBot almost nothing
- The margin is on orchestration, security, and convenience — not compute
- Migration tools create genuine switching cost moat (users stay because DogBot makes it easy, not because they're locked in)

---

## What To Build First (MVP)

### Phase 1: Single-agent, Cloudflare-only (4-6 weeks)
- Dashboard: signup, create one agent, view logs
- Agent runtime: Docker container on Cloudflare Containers
- Integrations: Telegram bot + web browsing only
- Security: command blocking, audit trail, secret injection
- LLM: Claude or GPT via user's API key

### Phase 2: Multi-agent + more integrations (4-6 weeks)
- Multiple agents per account
- Add Email (Gmail) and Slack integrations
- Per-agent security policies in dashboard
- Cost tracking per agent

### Phase 3: Cloud portability (4-6 weeks)
- Pulumi-based deployment to AWS and self-hosted Docker
- `sudodog migrate` CLI command
- Rivet Actors for portable state

### Phase 4: iMessage + polish (4-6 weeks)
- DogBot Relay iOS app (TestFlight)
- Mac relay daemon (OpenBubbles-based)
- Agent templates marketplace
- Team features

---

## Competitive Positioning

| | OpenClaw | Moltworker | DigitalOcean 1-Click | DogBot |
|---|---|---|---|---|
| Security-first | No | No | No | **Yes** |
| Multi-agent | No (1 agent) | No (1 agent) | No (1 agent) | **Yes** |
| Cloud-portable | Self-hosted only | Cloudflare only | DO only | **Any cloud** |
| Per-agent isolation | No | No | No | **Yes** |
| Migration tools | N/A | No | No | **Yes** |
| iMessage | Mac only | No | No | **iOS app + Mac** |
| Dashboard | Basic web UI | Minimal | None | **Full management** |
| Security audit trail | No | No | No | **Yes** |
| Agent cost caps | No | No | No | **Yes** |

---

## Key Risks and Honest Assessment

### This is a big build.
The MVP described above is probably 3-4 months of focused work for a small team. The full vision is 6-12 months. This is not a weekend project.

### The multi-agent angle is the real differentiator.
Nobody is doing "isolated agent per task" well. OpenClaw runs everything in one process. If DogBot nails per-agent isolation with seamless spawning, that's genuinely new.

### Cloud portability is a moat if you actually ship migration tools.
Everyone says "portable." Almost nobody ships a working `migrate` command. If DogBot actually does this, it's a real competitive advantage.

### iMessage is a nice-to-have, not a must-have.
The iOS Relay app will be limited (no silent sending). The Mac relay is better but requires hardware. Don't let iMessage block the launch — ship without it and add it in Phase 4.

### The name matters.
"DogBot" positions against "ClawdBot" in a way people will remember. "SudoDog" stays as the security engine / CLI brand. DogBot is the consumer-facing agent.
