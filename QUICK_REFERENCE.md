# SudoDog Docker + Daemon - Quick Reference

## Installation (One-Time Setup)

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# LOG OUT AND BACK IN

# 2. Setup SudoDog
cd ~/projects/sudodog
bash /home/claude/setup_docker.sh

# 3. Replace CLI
cp /home/claude/cli_updated.py sudodog/cli.py

# 4. Reinstall
pip3 install -e . --break-system-packages
```

## Daily Usage

### Start Daemon (Background)
```bash
sudodog daemon start
```

### Run Agent with Docker
```bash
sudodog run --docker python my_agent.py
```

### Check Status
```bash
sudodog daemon status
```

### View Logs
```bash
sudodog logs --last 20
```

### Stop Daemon
```bash
sudodog daemon stop
```

## Command Cheatsheet

| Command | What It Does |
|---------|-------------|
| `sudodog run python script.py` | Run with namespace sandbox (old) |
| `sudodog run --docker python script.py` | Run with Docker sandbox (new) |
| `sudodog run --docker --cpu-limit 2.0 python script.py` | Limit to 2 CPU cores |
| `sudodog run --docker --memory-limit 1g python script.py` | Limit to 1GB RAM |
| `sudodog daemon start` | Start monitoring daemon (background) |
| `sudodog daemon start --foreground` | Start daemon (see logs) |
| `sudodog daemon status` | Show active containers & stats |
| `sudodog daemon stop` | Stop daemon |
| `sudodog logs` | View recent agent activity |
| `sudodog status` | Show active sessions |

## Resource Limits

| Limit | Example Values | Default |
|-------|---------------|---------|
| CPU | 0.5, 1.0, 2.0 (cores) | 1.0 |
| Memory | 256m, 512m, 1g, 2g | 512m |

## What Changed?

### Before
✅ Pattern detection (SQL, shell commands)  
✅ Basic namespace isolation  
✅ Local logging  
❌ Weak isolation (can be escaped)  
❌ No resource limits  
❌ No ongoing monitoring  

### After (Now!)
✅ Pattern detection (SQL, shell commands)  
✅ **Strong Docker isolation**  
✅ Local logging  
✅ **Resource limits (CPU, memory)**  
✅ **Background daemon monitoring**  
✅ **Real-time container stats**  
✅ **Multi-container management**  

## Daemon Features

The daemon monitors all containers every 5 seconds and tracks:
- CPU usage %
- Memory usage %
- Container status
- Alerts when thresholds exceeded

Alerts logged to: `~/.sudodog/alerts.jsonl`

## Typical Workflow

```bash
# Morning: Start daemon
sudodog daemon start

# Run your agents throughout the day
sudodog run --docker python agent1.py
sudodog run --docker python agent2.py
sudodog run --docker python agent3.py

# Check what's happening
sudodog daemon status

# View logs
sudodog logs --last 50

# Evening: Stop daemon
sudodog daemon stop
```

## Troubleshooting

**"Docker is not running"**
```bash
sudo systemctl start docker
```

**"Permission denied"**
```bash
sudo usermod -aG docker $USER
# Then LOG OUT and LOG BACK IN
```

**Daemon won't start**
```bash
# Try foreground mode to see errors
sudodog daemon start --foreground
```

**Container stuck?**
```bash
# List all Docker containers
docker ps -a

# Force remove if needed
docker rm -f <container_id>
```

## Files & Directories

```
~/.sudodog/
├── config.json          # Configuration
├── daemon.json          # Daemon state
├── daemon.pid           # Daemon process ID
├── sessions.json        # Active sessions
├── logs/                # Agent logs
│   └── *.jsonl
├── alerts.jsonl         # Alert history
└── backups/             # File rollback backups
```

## Next Steps

Now that Docker + Daemon works:

1. **Add real-time alerting** (email, Slack)
2. **Build web dashboard** (see all agents visually)
3. **Multi-server support** (monitor agents on different machines)
4. **Advanced detection** (LLM-based anomaly detection)

---

**Quick Test:**
```bash
sudodog run --docker python -c "print('Hello from Docker!')"
```

Should show container creation, execution, and cleanup!
