# SudoDog Dashboard Documentation

Complete guide to using the SudoDog AI Agent Observability & Security Platform.

## Table of Contents

- [Getting Started](#getting-started)
- [Mission Control](#mission-control)
- [Agent Management](#agent-management)
- [Security Center](#security-center)
- [Cost Analytics](#cost-analytics)
- [Performance & Quality](#performance--quality)
- [Agent Orchestration](#agent-orchestration)
- [Enterprise Features](#enterprise-features)
  - [Microsoft 365 Integration](#microsoft-365-integration)
  - [Azure AD SSO](#azure-ad-sso)
  - [Shadow Agent Discovery](#shadow-agent-discovery)
  - [Compliance Reports](#compliance-reports)
  - [Audit Logs](#audit-logs)
  - [Team Management](#team-management)
- [CLI Reference](#cli-reference)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Quick Start

1. **Install SudoDog CLI**
   ```bash
   pip install sudodog
   ```

2. **Configure your API key**
   ```bash
   sudodog configure --api-key "your-api-key"
   ```

3. **Wrap your agent**
   ```bash
   sudodog run python my_agent.py
   ```

4. **View in dashboard**
   - Navigate to the [Dashboard](http://localhost:3000/dashboard)
   - Your agent will appear in Mission Control

### System Requirements

- Python 3.8+ (for CLI)
- Docker & Docker Compose (for self-hosting)
- PostgreSQL 13+ (for self-hosting)
- Redis 6+ (for real-time features)

---

## Mission Control

The Mission Control page is your central hub for monitoring all AI agents.

### Overview Metrics

- **Active Agents**: Number of agents currently running
- **Today's Cost**: Total spending across all agents for the current day
- **Security Alerts**: Unresolved security events requiring attention
- **Health Score**: Overall system health (0-100%)

### Cost Burn Rate Chart

Shows spending over the last 48 hours with hourly granularity. Hover over data points to see exact costs.

### Agent Status Grid

Lists all agents with their current status:
- **Active**: Agent is running and reporting telemetry
- **Idle**: Agent is registered but not currently active
- **Error**: Agent encountered an error
- **Stopped**: Agent has been manually stopped

### Recent Security Alerts

Shows the 5 most recent security events with severity levels:
- **Critical**: Requires immediate attention
- **High**: Should be addressed within 24 hours
- **Medium**: Review when convenient
- **Low**: Informational

### Top Cost Consumers

Lists agents by total cost over the last 7 days to identify expensive operations.

---

## Agent Management

### Viewing Agents

Navigate to **Agents** to see all registered agents. Filter by:
- Status (active, idle, error, stopped)
- Framework (LangChain, AutoGPT, CrewAI, custom)

### Agent Details

Click on an agent to view:
- **Actions Timeline**: All operations performed by the agent
- **Resource Access**: Files, APIs, and systems accessed
- **DNA Comparison**: Behavioral fingerprint vs baseline
- **Cost Breakdown**: Spending by model and operation type

### Action Types

SudoDog tracks three categories of actions:

1. **File Operations**
   - Read/Write/Delete files
   - Directory operations
   - File permissions changes

2. **API Calls**
   - HTTP requests (GET, POST, PUT, DELETE)
   - WebSocket connections
   - External service calls

3. **Shell Commands**
   - System commands executed
   - Script invocations
   - Environment modifications

---

## Security Center

### Security Events

View all detected security threats with:
- Severity level
- Event type (prompt injection, data exfiltration, etc.)
- Agent involved
- Timestamp
- Resolution status

### Event Types

- **Prompt Injection**: Attempt to manipulate agent behavior
- **Data Exfiltration**: Unauthorized data transfer
- **Unauthorized Access**: Accessing restricted resources
- **Anomalous Behavior**: Deviation from normal patterns
- **Rate Limit Violation**: Excessive API calls

### Threat Timeline

Visual representation of security events over time, grouped by severity.

### Security Summary

Aggregated metrics:
- Total events detected
- Events by severity
- Resolution rate
- Average time to resolution

### Resolving Events

1. Click on an event to view details
2. Investigate the cause
3. Take action (block agent, update policies, dismiss)
4. Mark as resolved with notes

---

## Cost Analytics

### Cost Summary

Overview of spending:
- Total cost (selected period)
- Cost by model provider
- Cost trend (up/down from previous period)
- Projected monthly cost

### Cost by Agent

Breakdown of costs per agent:
- Agent name
- Total cost
- Number of operations
- Cost per operation

### Cost Timeline

Spending over time with granularity options:
- Hourly (last 24 hours)
- Daily (last 30 days)
- Weekly (last 12 weeks)

### Budgets

Set spending limits:
- Per agent
- Per model
- Daily/weekly/monthly

Get alerts when approaching or exceeding budgets.

### Cost Optimizations

AI-powered recommendations to reduce costs:
- Model substitution suggestions
- Caching opportunities
- Batching recommendations
- Idle agent identification

---

## Performance & Quality

### Quality Metrics

Track agent reliability:
- **Success Rate**: Percentage of successful operations
- **Error Rate**: Percentage of failed operations
- **P50/P95/P99 Latency**: Response time percentiles

### Anomaly Detection

Automatic detection of:
- Latency spikes
- Error rate increases
- Unusual patterns
- Resource exhaustion

### Agent DNA

Behavioral fingerprint showing:
- Typical operation patterns
- Resource access patterns
- Time-of-day patterns
- Deviation from baseline

### Performance Summary

Aggregate metrics:
- Average latency
- Total operations
- Operations per minute
- Resource utilization

---

## Agent Orchestration

### Agent Graph

Visual representation of multi-agent workflows:
- Agent dependencies
- Communication patterns
- Data flow
- Bottlenecks

### Bottleneck Analysis

Identify coordination issues:
- Slow agents blocking others
- Resource contention
- Circular dependencies
- Communication failures

### Coordination Health

Overall health of agent coordination:
- Message delivery rate
- Average coordination latency
- Failed handoffs
- Queue depths

---

## Enterprise Features

### Microsoft 365 Integration

#### Overview

Export SudoDog telemetry to Microsoft Agent 365 for unified governance and operations visibility.

#### Configuration

1. **Azure Portal Setup**
   - Go to Azure Portal > Azure Active Directory > App registrations
   - Click "New registration"
   - Name: "SudoDog Integration"
   - Copy Application (client) ID and Directory (tenant) ID

2. **Create Client Secret**
   - Under "Certificates & secrets"
   - New client secret
   - Copy the value (shown only once)

3. **API Permissions**
   - Add permission: Microsoft Graph > Application.Read.All
   - Grant admin consent

4. **Dashboard Configuration**
   - Go to Settings > Enterprise > Microsoft 365
   - Enter Tenant ID, Client ID, Client Secret
   - Select data to export (actions, costs, security, performance)
   - Click "Configure Integration"

5. **Test Connection**
   - Click "Test Connection" to verify setup
   - Status should change to "Connected"

#### CLI Configuration

```bash
sudodog configure --export-to-agent365 \
  --tenant-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  --client-id "your-app-id" \
  --client-secret "your-secret"
```

#### Export Settings

Choose what data to sync:
- **Agent Actions**: File, API, shell operations
- **Cost Metrics**: Per agent, model, time period
- **Security Events**: Threats detected and blocked
- **Performance Data**: Latency, error rates, throughput

Export frequency:
- Real-time: Immediate sync
- Hourly: Batch every hour
- Daily: Batch once per day

---

### Azure AD SSO

#### Overview

Enable single sign-on using Azure Active Directory / Microsoft Entra for your organization.

#### Configuration

1. **Prerequisites**
   - Microsoft 365 integration configured
   - Azure AD admin access

2. **Dashboard Setup**
   - Go to Settings > Enterprise > Microsoft 365
   - Under "Azure AD / Entra SSO"
   - Enter SSO domain (e.g., company.onmicrosoft.com)
   - Click "Configure SSO"

3. **User Login**
   - Users visit the SSO login URL
   - Authenticate with Microsoft credentials
   - Automatically provisioned in SudoDog

#### CLI Configuration

```bash
sudodog configure --sso azure-ad \
  --tenant "company.onmicrosoft.com"
```

---

### Shadow Agent Discovery

#### Overview

Detect AI agents running in your environment without SudoDog monitoring.

#### How It Works

1. **Process Scanning**: Identifies processes making AI API calls
2. **Network Analysis**: Detects traffic to AI providers (OpenAI, Anthropic, etc.)
3. **Signature Matching**: Recognizes known agent frameworks

#### Running a Scan

**Dashboard:**
1. Go to Settings > Enterprise > Shadow Agents
2. Click "Scan Now"
3. Review discovered agents

**CLI:**
```bash
sudodog discover
```

#### Scan Results

For each shadow agent:
- Process ID (PID)
- Process name and command line
- Suspected framework (LangChain, AutoGPT, etc.)
- Confidence score
- Estimated cost
- Detection indicators

#### Actions

- **Wrap with SudoDog**: Add monitoring to the agent
- **Quarantine**: Restrict network access
- **Dismiss**: Mark as reviewed/safe

---

### Compliance Reports

#### Supported Standards

1. **SOC 2 Type II**
   - Security controls
   - Availability metrics
   - Confidentiality measures

2. **EU AI Act**
   - Risk assessment
   - Transparency requirements
   - Human oversight documentation

3. **ISO 42001**
   - AI management system
   - Risk management
   - Performance monitoring

4. **GDPR**
   - Data processing records
   - Privacy controls
   - Consent management

#### Generating a Report

**Dashboard:**
1. Go to Settings > Enterprise > Compliance
2. Select standard (SOC 2, EU AI Act, etc.)
3. Choose period (30/90/180/365 days)
4. Click "Generate Report"

**CLI:**
```bash
sudodog compliance report --standard soc2 \
  --period "2025-Q3" \
  --output report.pdf
```

#### Report Contents

- Executive summary
- Total actions audited
- Security incidents (detected, resolved)
- Resolution rate
- Overall compliance score
- Audit trail completeness
- Security posture score
- Actionable recommendations

---

### Audit Logs

#### Overview

Immutable record of all actions for compliance and forensics.

#### Log Contents

Each entry includes:
- Timestamp
- User ID
- Action type
- Resource type and ID
- IP address
- Details (JSON)
- Checksum (tamper detection)

#### Filtering Logs

Filter by:
- Action type
- User
- Time period
- Resource

#### Exporting Logs

**Dashboard:**
1. Go to Settings > Enterprise > Audit Logs
2. Apply filters
3. Click "Export CSV"

**API:**
```bash
curl -X GET "/api/v1/audit/export?format=csv&days=30" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Team Management

#### Roles

1. **Viewer**: Read-only access to all data
2. **Developer**: View + manage agents
3. **Admin**: Full access including settings

#### Inviting Members

1. Go to Settings > Team
2. Click "Invite Team Member"
3. Enter email and select role
4. User receives invitation email

#### Managing Members

- Change roles
- Remove access
- View activity

---

## CLI Reference

### Installation

```bash
pip install sudodog
```

### Configuration

```bash
# Set API key
sudodog configure --api-key "your-key"

# Set dashboard URL (self-hosted)
sudodog configure --dashboard-url "https://your-instance.com"

# Configure Microsoft 365
sudodog configure --export-to-agent365 \
  --tenant-id "tenant" \
  --client-id "client" \
  --client-secret "secret"

# Configure SSO
sudodog configure --sso azure-ad \
  --tenant "company.onmicrosoft.com"
```

### Running Agents

```bash
# Basic usage
sudodog run python agent.py

# With custom agent name
sudodog run --name "my-agent" python agent.py

# With environment variables
sudodog run --env API_KEY=xxx python agent.py
```

### Discovery

```bash
# Scan for shadow agents
sudodog discover

# Scan specific host
sudodog discover --host server1.company.com
```

### Compliance

```bash
# Generate SOC 2 report
sudodog compliance report --standard soc2 \
  --period "2025-Q3" \
  --output report.pdf

# List available standards
sudodog compliance standards
```

### Status

```bash
# Check agent status
sudodog status

# List all agents
sudodog agents list

# Get agent details
sudodog agents get <agent-id>
```

---

## API Reference

### Authentication

All API requests require a Bearer token:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.sudodog.com/api/v1/...
```

### Endpoints

#### Dashboard
- `GET /api/v1/dashboard/overview` - Dashboard overview
- `GET /api/v1/dashboard/agents/status` - Agent statuses
- `GET /api/v1/dashboard/cost-burn-rate` - Cost over time

#### Agents
- `GET /api/v1/agents/` - List agents
- `GET /api/v1/agents/{id}` - Get agent
- `GET /api/v1/agents/{id}/actions` - Agent actions

#### Security
- `GET /api/v1/security/events` - Security events
- `GET /api/v1/security/summary` - Security summary

#### Costs
- `GET /api/v1/costs/summary` - Cost summary
- `GET /api/v1/costs/by-agent` - Costs by agent

#### Microsoft 365
- `GET /api/v1/microsoft365/connection` - Get connection
- `POST /api/v1/microsoft365/connection` - Configure
- `POST /api/v1/microsoft365/shadow-agents/scan` - Scan
- `POST /api/v1/microsoft365/compliance/generate` - Generate report

Full API documentation available at `/api/docs` (Swagger UI).

---

## Troubleshooting

### Common Issues

#### Agent not appearing in dashboard

1. Check CLI is configured correctly
   ```bash
   sudodog configure --show
   ```

2. Verify agent is running with SudoDog wrapper
   ```bash
   sudodog status
   ```

3. Check network connectivity to dashboard

#### Microsoft 365 connection failing

1. Verify credentials in Azure Portal
2. Check API permissions granted
3. Ensure admin consent provided
4. Test with Azure AD PowerShell

#### High latency warnings

1. Check agent's network connectivity
2. Review cost optimization recommendations
3. Consider batching operations
4. Check for resource contention

#### Security events false positives

1. Review event details
2. Update security policies
3. Whitelist known-good patterns
4. Contact support for tuning

### Getting Help

- **Documentation**: This file
- **GitHub Issues**: https://github.com/SudoDog-official/sudodog-platform/issues
- **Community**: GitHub Discussions

---

## Changelog

### v1.0.0 (Current - Free Beta)

- Initial release
- Microsoft 365 integration
- Azure AD SSO
- Shadow Agent Discovery
- Compliance Reports (SOC 2, EU AI Act, ISO 42001, GDPR)
- Real-time monitoring
- Cost analytics
- Security threat detection
- Audit logging
- Team management

---

*SudoDog - AI Agent Observability & Security Platform*

*Free during beta. All features included.*
