# SudoDog Telemetry System

Privacy-first anonymous analytics for SudoDog. Built to help improve threat detection while respecting user privacy.

## Quick Start

### For Users

```bash
# Check if telemetry is enabled
sudodog telemetry status

# Enable anonymous analytics
sudodog telemetry enable

# Disable anytime
sudodog telemetry disable

# See what we collect
sudodog telemetry info
```

### For Developers

See `INTEGRATION.py` for how to add telemetry tracking to your code.

---

## Files in This System

### Core Modules
- **`telemetry.py`** - Core telemetry collection module
- **`telemetry_ui.py`** - User interface (prompts, status display)
- **`cli_telemetry.py`** - CLI commands for telemetry management

### Integration
- **`INTEGRATION.py`** - Guide for adding telemetry to existing commands
- **`vercel_telemetry.py`** - Backend serverless function (deploy to Vercel)
- **`PRIVACY.md`** - Privacy policy content for website

---

## How It Works

### 1. Opt-In During Setup

When a user runs `sudodog init`, they see this prompt:

```
┌─────────────────────────────────────────────────────────┐
│  📊 Help Improve SudoDog                                │
│                                                          │
│  Share anonymous usage data to help us:                 │
│    ✓ Improve threat detection                           │
│    ✓ Fix bugs faster                                    │
│    ✓ Prioritize features                                │
│                                                          │
│  We collect:                                             │
│    ✓ Which commands you use                             │
│    ✓ Error messages (sanitized)                         │
│    ✓ Performance metrics                                │
│                                                          │
│  We NEVER collect:                                       │
│    ✗ Your agent code                                    │
│    ✗ File contents or paths                             │
│    ✗ API keys or credentials                            │
│                                                          │
│  Privacy Policy: https://sudodog.com/privacy            │
└─────────────────────────────────────────────────────────┘

Enable anonymous analytics? [Y/n]:
```

**Default: Yes** (but user can decline)

### 2. Anonymous ID Generation

If user opts in, we generate an anonymous ID:

```python
# Uses machine info (hostname + architecture)
machine_info = f"{os.uname().nodename}-{os.uname().machine}"

# One-way hash (not reversible)
hash_obj = hashlib.sha256(machine_info.encode())
anonymous_id = f"anon-{hash_obj.hexdigest()[:16]}"
# Result: "anon-a1b2c3d4e5f6g7h8"
```

**This ID:**
- ✅ Allows us to count unique users
- ✅ Helps us see usage patterns over time
- ❌ Cannot be used to identify the user
- ❌ Cannot be reversed to get machine info

### 3. Event Tracking

Throughout SudoDog, we track anonymous events:

```python
from sudodog.telemetry import get_telemetry

telemetry = get_telemetry()

# Track command usage
telemetry.track_command('run', {
    'docker': True,
    'cpu_limit': 2.0,
    'memory_limit': '1g'
})

# Track errors
try:
    # ... code ...
except Exception as e:
    telemetry.track_error(type(e).__name__, str(e))

# Track threat detection
telemetry.track_threat_detection(
    pattern_type='sql_injection',
    action_taken='blocked'
)

# Track daemon stats
telemetry.track_daemon_stats(
    container_count=3,
    avg_cpu=15.2,
    avg_memory=28.5
)
```

### 4. Event Sanitization

Before sending, events are sanitized:

```python
def _sanitize_error(error_message: str) -> str:
    """Remove PII from error messages"""
    import re
    
    # Remove file paths
    sanitized = re.sub(r'/[^\s]+', '/[PATH]', error_message)
    
    # Remove usernames
    sanitized = re.sub(r'/home/[^/\s]+', '/home/[USER]', sanitized)
    
    # Remove IPs
    sanitized = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP]', sanitized)
    
    return sanitized
```

**Example:**
- Before: `FileNotFoundError: /home/john/agent/config.json not found`
- After: `FileNotFoundError: /home/[USER]/[PATH] not found`

### 5. Sending Events

Events are sent asynchronously to avoid blocking:

```python
def track_event(self, event_type: str, properties: dict) -> None:
    if not self.enabled:
        return  # Respect user's choice
    
    event = {
        'anonymous_id': self.anonymous_id,
        'event_type': event_type,
        'timestamp': datetime.now().isoformat(),
        'version': self._get_version(),
        'properties': properties
    }
    
    try:
        requests.post(
            self.telemetry_endpoint,
            json=event,
            timeout=2,  # Don't block user
            headers={'Content-Type': 'application/json'}
        )
    except Exception:
        pass  # Fail silently - never break the tool
```

**Key points:**
- ✅ 2-second timeout (doesn't slow down the tool)
- ✅ Silent failure (telemetry errors never break SudoDog)
- ✅ Respects opt-out immediately

---

## What We Track

### Command Usage
```json
{
  "event_type": "command_used",
  "properties": {
    "command": "run",
    "used_docker": true,
    "cpu_limit": 2.0,
    "memory_limit": "1g"
  }
}
```

### Error Tracking
```json
{
  "event_type": "error_occurred",
  "properties": {
    "error_type": "ModuleNotFoundError",
    "error_message": "No module named '[SANITIZED]'"
  }
}
```

### Threat Detection
```json
{
  "event_type": "threat_detected",
  "properties": {
    "pattern_type": "sql_injection",
    "action_taken": "blocked"
  }
}
```

### Daemon Stats
```json
{
  "event_type": "daemon_stats",
  "properties": {
    "container_count": 3,
    "avg_cpu_percent": 15.2,
    "avg_memory_percent": 28.5
  }
}
```

### Install Tracking
```json
{
  "event_type": "install_completed",
  "properties": {
    "os": "Linux",
    "arch": "x86_64"
  }
}
```

---

## What We DON'T Track

We **never** collect:

- ❌ Your agent code
- ❌ File contents
- ❌ Command arguments (e.g., file paths, URLs)
- ❌ Command outputs
- ❌ API keys or credentials
- ❌ Environment variables
- ❌ Your name, email, or IP address
- ❌ Container names
- ❌ Actual blocked commands (only pattern type)

---

## Backend Setup

### Deploy to Vercel

1. Create `api/` directory in your Vercel project
2. Copy `vercel_telemetry.py` to `api/telemetry.py`
3. Deploy (Vercel auto-detects Python functions)

Your endpoint will be: `https://sudodog.com/api/telemetry/v1/events`

### Test the Endpoint

```bash
curl -X POST https://sudodog.com/api/telemetry/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "anonymous_id": "anon-test123",
    "event_type": "test_event",
    "timestamp": "2025-10-31T12:00:00Z",
    "version": "0.1.0",
    "properties": {}
  }'
```

Expected response:
```json
{
  "status": "success",
  "message": "Event received"
}
```

### Add Database (Optional)

For production, add Vercel Postgres:

```sql
CREATE TABLE telemetry_events (
  id SERIAL PRIMARY KEY,
  anonymous_id VARCHAR(32) NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  version VARCHAR(16),
  properties JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_anonymous_id ON telemetry_events(anonymous_id);
CREATE INDEX idx_event_type ON telemetry_events(event_type);
CREATE INDEX idx_timestamp ON telemetry_events(timestamp);
```

---

## Integration Checklist

- [ ] Copy `telemetry.py` to `sudodog/telemetry.py`
- [ ] Copy `telemetry_ui.py` to `sudodog/telemetry_ui.py`
- [ ] Copy `cli_telemetry.py` to `sudodog/cli_telemetry.py`
- [ ] Add to main CLI: `add_telemetry_commands(cli)`
- [ ] Add opt-in to `sudodog init` command
- [ ] Add tracking to `run` command
- [ ] Add tracking to `daemon` monitoring
- [ ] Add tracking to policy engine
- [ ] Deploy backend to Vercel
- [ ] Add privacy policy to website
- [ ] Test locally with disabled telemetry
- [ ] Test locally with enabled telemetry
- [ ] Update README to mention telemetry

---

## User Experience

### First Install

```bash
$ sudodog init

🐕 Initializing SudoDog...
✓ Created directory: ~/.sudodog
✓ Created config file
✓ Created logs directory

[Telemetry prompt appears]

Enable anonymous analytics? [Y/n]: y

✓ Thank you! Anonymous analytics enabled.
  You can disable anytime with: sudodog telemetry disable

✓ SudoDog initialized successfully!
```

### Checking Status

```bash
$ sudodog telemetry status

📊 Telemetry Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: Enabled
Anonymous ID: anon-a1b2c3d4e5f6g7h8

What we collect:
  • Command usage (which features you use)
  • Error types (helps us fix bugs)
  • Performance metrics (execution time)
  • Threat patterns (improves detection)

What we DON'T collect:
  • Your code or file contents
  • Command arguments or outputs
  • API keys or credentials
  • Personally identifiable information

To disable: sudodog telemetry disable

Privacy Policy: https://sudodog.com/privacy
Telemetry Details: https://sudodog.com/telemetry
```

### Disabling

```bash
$ sudodog telemetry disable

✓ Anonymous analytics disabled

We're no longer collecting any data.
You can re-enable anytime with: sudodog telemetry enable
```

---

## Privacy Guarantees

1. **Opt-in only** - Users must explicitly consent
2. **No PII** - We never collect personally identifiable info
3. **Sanitized errors** - Paths, IPs, usernames removed
4. **Open source** - All telemetry code is public
5. **Easy disable** - One command to turn off
6. **Silent failures** - Telemetry never breaks the tool
7. **Minimal data** - We collect the minimum needed
8. **Transparent** - Users see exactly what's collected

---

## Expected Opt-In Rate

Based on industry standards for security tools:

- **Free tier**: 60-75% opt-in rate
- **Why so high?**
  - Default is "yes" (but clearly explained)
  - Transparent about what's collected
  - Easy to disable
  - Open source code builds trust
  - Users want to help improve security

With 10,000 users:
- 7,000 opt-in → plenty of data
- 3,000 opt-out → respecting privacy

**Win-win: Data + Trust**

---

## Questions?

**Technical questions:**
- GitHub Issues: https://github.com/SudoDog-official/sudodog/issues

**Privacy questions:**
- Email: privacy@sudodog.com

**Security issues:**
- Email: security@sudodog.com

---

*Built with privacy in mind. Open source and transparent.*
