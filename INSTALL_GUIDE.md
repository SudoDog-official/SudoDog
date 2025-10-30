# SudoDog Docker + Daemon - Installation Guide

## Current Status
✅ All files are in your GitHub repo (I can see them!)
✅ Docker installed on your Linux test PC
✅ cli.py updated with daemon commands

## What You Need to Do

### On Your Linux Test PC (where Docker is installed):

**Step 1: Clone/Pull Your Repo**
```bash
cd ~/projects
git clone https://github.com/SudoDog-official/sudodog.git
# OR if you already have it:
cd ~/projects/sudodog
git pull
```

**Step 2: Update requirements.txt**

Add this line to `requirements.txt`:
```
docker>=6.1.0
```

**Step 3: Install Dependencies**
```bash
cd ~/projects/sudodog
pip3 install docker --break-system-packages
```

**Step 4: Install SudoDog**
```bash
pip3 uninstall sudodog -y
pip3 install -e . --break-system-packages
```

**Step 5: Initialize SudoDog**
```bash
sudodog init
```

**Step 6: Test Docker Access**
```bash
# Make sure Docker works
docker run hello-world

# If you get permission denied:
sudo usermod -aG docker $USER
# Then LOG OUT and LOG BACK IN
```

**Step 7: Test SudoDog with Docker**
```bash
# Test basic Docker run
sudodog run --docker python -c "print('Hello from Docker!')"
```

**Step 8: Start the Daemon**
```bash
# Start in foreground (so you can see what's happening)
sudodog daemon start --foreground
```

**Step 9: In Another Terminal - Test Monitoring**
```bash
# Run an agent
sudodog run --docker python -c "import time; print('Working...'); time.sleep(10); print('Done!')"

# Check daemon status
sudodog daemon status
```

## Your File Structure Should Be:

```
~/projects/sudodog/
├── sudodog/
│   ├── __init__.py
│   ├── blocker.py
│   ├── cli.py           ← Updated with daemon commands
│   ├── daemon.py         ← NEW
│   ├── docker_sandbox.py ← NEW
│   ├── monitor.py
│   └── sandbox.py
├── requirements.txt      ← Add docker>=6.1.0
├── setup.py
├── README.md
└── ... other files
```

## Quick Commands Reference

```bash
# Run with Docker sandbox
sudodog run --docker python script.py

# Run with resource limits
sudodog run --docker --cpu-limit 2.0 --memory-limit 1g python script.py

# Start daemon (foreground - see logs)
sudodog daemon start --foreground

# Start daemon (background)
sudodog daemon start

# Check daemon status
sudodog daemon status

# Stop daemon
sudodog daemon stop

# View logs
sudodog logs --last 20
```

## Troubleshooting

### "Docker is not running"
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### "Permission denied" when accessing Docker
```bash
sudo usermod -aG docker $USER
# Then LOG OUT and LOG BACK IN (important!)
```

### "Module 'docker' not found"
```bash
pip3 install docker --break-system-packages
```

### Can't find sudodog command
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Testing Everything Works

Run this complete test:

```bash
# 1. Initialize
sudodog init

# 2. Test Docker
docker run hello-world

# 3. Test SudoDog with Docker
sudodog run --docker python -c "print('Test 1: Hello from Docker')"

# 4. Start daemon
sudodog daemon start --foreground &

# 5. Run agent while daemon monitors
sudodog run --docker python -c "import time; time.sleep(5); print('Test 2: Monitored!')"

# 6. Check status
sudodog daemon status

# 7. Stop daemon
sudodog daemon stop
```

If all 7 steps work - you're ready! 🎉

## What Changed?

**Before:**
- Basic namespace isolation
- No ongoing monitoring
- No resource limits

**After:**
- ✅ Strong Docker container isolation
- ✅ Background daemon monitoring
- ✅ CPU & memory limits
- ✅ Real-time stats
- ✅ Alert system

## Next Steps After This Works

1. Add email/Slack alerting
2. Build web dashboard
3. Multi-server support
4. Advanced anomaly detection

---

**Need help?** Just let me know which step fails!
