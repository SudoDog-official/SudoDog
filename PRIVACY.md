# SudoDog Privacy Policy

**Last Updated: October 31, 2025**

## Our Commitment to Privacy

SudoDog is built by developers, for developers. We understand that security tools must be trustworthy, especially when it comes to data collection. This privacy policy explains exactly what data we collect, why, and how you control it.

**Key Principles:**
- ✅ **Opt-in only** - Analytics are disabled by default
- ✅ **Anonymous by design** - No personally identifiable information
- ✅ **Transparent** - Open source telemetry code
- ✅ **User control** - Disable anytime with one command

---

## What We Collect (Free Tier)

When you **opt in** to anonymous analytics during setup, SudoDog collects:

### ✅ Usage Data
- **Which commands you run** (e.g., `run`, `daemon`, `logs`)
- **Feature usage** (e.g., Docker enabled, resource limits set)
- **Performance metrics** (e.g., execution time, CPU/memory usage)

### ✅ Error Data
- **Error types** (e.g., `ModuleNotFoundError`, `PermissionError`)
- **Sanitized error messages** (paths, usernames, and IPs removed)

### ✅ Threat Detection Data
- **Pattern types detected** (e.g., `sql_injection`, `file_deletion`)
- **Actions taken** (e.g., `blocked`, `warned`, `allowed`)

### ✅ System Context
- **Operating system** (e.g., `Linux`, `macOS`)
- **SudoDog version** (e.g., `0.1.0`)
- **Anonymous machine ID** (one-way hash, not reversible)

---

## What We NEVER Collect

We **never** collect:

- ❌ Your agent code or scripts
- ❌ File contents or paths
- ❌ Command arguments or outputs
- ❌ API keys, tokens, or credentials
- ❌ Environment variables
- ❌ Your name, email, or IP address
- ❌ Any personally identifiable information

---

## Example: What Gets Sent

Here's an actual example of a telemetry event:

```json
{
  "anonymous_id": "anon-a1b2c3d4e5f6",
  "event_type": "command_used",
  "timestamp": "2025-10-31T12:34:56Z",
  "version": "0.1.0",
  "properties": {
    "command": "run",
    "used_docker": true,
    "cpu_limit": 2.0,
    "memory_limit": "1g"
  }
}
```

**What this tells us:**
- Someone used the `run` command with Docker
- They set CPU and memory limits
- This helps us prioritize Docker features

**What this DOESN'T tell us:**
- Who you are
- What agent you ran
- What your agent did
- Any of your data

---

## How We Use This Data

We use anonymous telemetry to:

1. **Improve threat detection** - Identify common attack patterns
2. **Fix bugs faster** - See which errors occur most frequently
3. **Prioritize features** - Focus on what users actually use
4. **Optimize performance** - Understand typical resource usage
5. **Publish research** - Share anonymized security insights with the community

We **never**:
- Sell your data
- Share individual user data
- Use data for advertising
- Track you across websites

---

## Paid Tier (Coming Soon)

When you upgrade to the Production tier, you'll get cloud features that **require** data sharing:

### Required Data Collection
- **Full logs** - Stored in the cloud for the dashboard
- **Real-time metrics** - CPU, memory, network usage
- **Alert history** - When and why alerts were triggered
- **Multi-server data** - Aggregate stats across your infrastructure

**Why is this required?**
Because these features **are** the product. The cloud dashboard, alerts, and analytics only work if we can store and process your data.

**You control retention:**
- Choose how long to keep logs (7, 30, 90 days, or 1 year)
- Delete your data anytime
- Export your data anytime

---

## Data Storage and Security

### Free Tier
- **Storage**: Events stored for 90 days, then deleted
- **Aggregation**: Anonymous stats kept indefinitely for research
- **Transport**: HTTPS encryption in transit
- **No database**: Events logged and aggregated, not stored per-user

### Paid Tier (Coming Soon)
- **Storage**: Vercel-secured infrastructure
- **Encryption**: At rest and in transit
- **Backups**: Daily backups for 30 days
- **Compliance**: SOC 2 Type II (in progress)

---

## Your Rights

You have complete control over your data:

### Opt Out / Disable
```bash
sudodog telemetry disable
```

### Check Status
```bash
sudodog telemetry status
```

### See What We Collect
```bash
sudodog telemetry info
```

### Request Data Deletion
Email: privacy@sudodog.com with your anonymous ID

### View Source Code
Our telemetry code is open source:
https://github.com/SudoDog-official/sudodog/blob/main/sudodog/telemetry.py

---

## Third-Party Services

SudoDog uses the following third-party services:

### Analytics (Free Tier)
- **Vercel Analytics** - Anonymous page views on sudodog.com
- **No third-party tracking** - We don't use Google Analytics, Facebook Pixel, etc.

### Infrastructure (Paid Tier)
- **Vercel** - Hosting and serverless functions
- **Vercel Postgres** - Database storage (when you opt in)

We do **not** share your data with third parties for advertising or marketing.

---

## Changes to This Policy

We'll update this policy as we add features. Major changes will be announced via:
- Email (if you have a paid account)
- GitHub repository announcements
- Blog post on sudodog.com

Version history available at:
https://github.com/SudoDog-official/sudodog/blob/main/PRIVACY.md

---

## Children's Privacy

SudoDog is not intended for children under 13. We do not knowingly collect data from children.

---

## International Users

SudoDog is developed in the United States. By using SudoDog, you consent to the transfer of your data to the US.

### GDPR Compliance (EU Users)
- **Legal basis**: Consent (you opt in)
- **Data minimization**: We collect the minimum necessary
- **Right to erasure**: Email privacy@sudodog.com
- **Data portability**: Export your data anytime

### CCPA Compliance (California Users)
- **Do Not Sell**: We don't sell your data (never have, never will)
- **Right to know**: View what we collect via `sudodog telemetry info`
- **Right to delete**: Email privacy@sudodog.com

---

## Contact Us

**Questions about privacy?**
- **Email**: privacy@sudodog.com
- **GitHub**: https://github.com/SudoDog-official/sudodog/issues
- **Security issues**: security@sudodog.com

---

## Open Source Transparency

Unlike most analytics tools, SudoDog's telemetry code is **completely open source**. You can:

1. **Read the source**: https://github.com/SudoDog-official/sudodog/blob/main/sudodog/telemetry.py
2. **Verify what's collected**: Search for `track_event` calls
3. **Audit the sanitization**: See how we remove PII
4. **Inspect the payload**: See exactly what gets sent

**No black boxes. No hidden tracking. Complete transparency.**

---

## Summary

**TL;DR:**
- ✅ Opt-in anonymous analytics (disabled by default)
- ✅ No PII, no tracking, no selling data
- ✅ Open source telemetry code
- ✅ Easy to disable: `sudodog telemetry disable`
- ✅ Used only to improve the product

**We're developers too. We built the privacy policy we'd want to see.**

---

*Last updated: October 31, 2025*  
*Version: 1.0.0*
