# SudoDog Docker + Daemon Installation Guide

## What We're Installing

1. **Docker-based sandboxing** - Strong container isolation instead of namespaces
2. **Background daemon** - Monitors all containers in real-time
3. **New CLI commands** - Control daemon and use Docker sandbox

## Step-by-Step Installation

### Step 1: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# IMPORTANT: Log out and log back in for group changes to take effect
# Then test Docker works:
docker run hello-world
```

### Step 2: Navigate to Your Project

```bash
cd ~/projects/sudodog
```

### Step 3: Run Setup Script

```bash
bash /home/claude/setup_docker.sh
```

This will:
- Install Python `docker` package
- Copy new files to sudodog/
- Update requirements.txt

### Step 4: Replace CLI File

```bash
# Backup your old CLI
cp sudodog/cli.py sudodog/cli.py.backup

# Replace with new CLI
cp /home/claude/cli_updated.py sudodog/cli.py
```

### Step 5: Reinstall SudoDog

```bash
pip3 uninstall sudodog -y
pip3 install -e . --break-system-packages
```

### Step 6: Verify Installation

```bash
# Check version
sudodog version

# Check new daemon commands exist
sudodog daemon --help

# Check Docker flag exists
sudodog run --help | grep docker
```

## Testing the New Features

### Test 1: Run Agent with Docker Sandbox

```bash
# Create a simple test script
cat > test_docker.py << 'EOF'
import os
print("Hello from Docker!")
print(f"Container ID: {os.getenv('HOSTNAME')}")
print(f"SudoDog Session: {os.getenv('SUDODOG_SESSION')}")
EOF

# Run with Docker
sudodog run --docker python test_docker.py
```

You should see:
- Container creation
- Isolation confirmation
- CPU/Memory stats

### Test 2: Start the Daemon (Foreground)

```bash
# Start daemon in foreground to see output
sudodog daemon start --foreground
```

Leave this running in one terminal...

### Test 3: Run Agent While Daemon Monitors

Open a NEW terminal:

```bash
# Run a long-running task
sudodog run --docker python -c "import time; print('Working...'); time.sleep(30); print('Done!')"
```

Switch back to daemon terminal - you should see real-time monitoring!

### Test 4: Check Daemon Status

```bash
# In a new terminal
sudodog daemon status
```

Should show:
- Active containers
- CPU/Memory usage
- Any alerts

### Test 5: Resource Limits

```bash
# Test CPU limit
sudodog run --docker --cpu-limit 0.5 python -c "import time; time.sleep(5); print('Done')"

# Test memory limit
sudodog run --docker --memory-limit 256m python -c "print('Low memory mode')"
```

## New Commands

### Daemon Management

```bash
# Start daemon in background
sudodog daemon start

# Start daemon in foreground (see logs)
sudodog daemon start --foreground

# Check daemon status
sudodog daemon status

# Stop daemon
sudodog daemon stop

# Change monitoring interval
sudodog daemon start --interval 10  # Check every 10 seconds
```

### Docker Sandbox Options

```bash
# Basic Docker run
sudodog run --docker python script.py

# With resource limits
sudodog run --docker --cpu-limit 2.0 --memory-limit 1g python script.py

# Still works without Docker (old namespace method)
sudodog run python script.py
```

## Architecture Comparison

### Before (Namespace Isolation):
```
Agent → Linux Namespaces → System
         ↓
    Basic isolation
    Can be escaped
    No resource limits
```

### After (Docker + Daemon):
```
Agent → Docker Container → Isolated filesystem
         ↓
    Strong isolation
    Resource limits enforced
    Network isolation
    
Background Daemon monitors:
    - CPU usage
    - Memory usage
    - Alerts on thresholds
    - Multi-server ready
```

## Troubleshooting

### "Docker is not running"
```bash
sudo systemctl start docker
docker ps  # Should work
```

### "Permission denied"
```bash
# Make sure you're in docker group
groups | grep docker

# If not, add yourself and RESTART your session
sudo usermod -aG docker $USER
# Then log out and log back in
```

### "Module 'docker' not found"
```bash
pip3 install docker --break-system-packages
```

### Daemon won't start in background
```bash
# Use foreground mode instead
sudodog daemon start --foreground
```

## What's Next?

Now that you have Docker + Daemon working, the next features to add:

1. **Real-time Alerts** - Email/Slack when thresholds exceeded
2. **Web Dashboard** - See all agents visually
3. **Multi-server** - Monitor agents across multiple machines
4. **Advanced Detection** - LLM-based anomaly detection

## Files Created

- `sudodog/docker_sandbox.py` - Docker container management
- `sudodog/daemon.py` - Background monitoring daemon
- `sudodog/cli.py` - Updated CLI with new commands

## Testing Checklist

- [ ] Docker installed and running
- [ ] Setup script completed
- [ ] CLI replaced with new version
- [ ] SudoDog reinstalled
- [ ] `sudodog version` works
- [ ] `sudodog daemon --help` shows commands
- [ ] `sudodog run --docker python test.py` works
- [ ] Daemon starts in foreground
- [ ] Daemon shows container stats
- [ ] Resource limits work

---

**You're now running production-grade AI agent security! 🎉**
