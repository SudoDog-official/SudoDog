#!/bin/bash
# Setup script for SudoDog Docker + Daemon upgrade

echo "🐕 SudoDog Docker + Daemon Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the right directory
if [ ! -d "sudodog" ]; then
    echo "❌ Error: sudodog directory not found"
    echo "   Please run this script from the project root"
    exit 1
fi

echo "📦 Step 1: Installing Python dependencies..."
pip3 install docker --break-system-packages 2>/dev/null || pip3 install docker

echo ""
echo "📁 Step 2: Moving new files to sudodog directory..."

# Move the Docker sandbox module
if [ -f "/home/claude/docker_sandbox.py" ]; then
    cp /home/claude/docker_sandbox.py sudodog/
    echo "✓ Installed docker_sandbox.py"
fi

# Move the daemon module
if [ -f "/home/claude/daemon.py" ]; then
    cp /home/claude/daemon.py sudodog/
    echo "✓ Installed daemon.py"
fi

echo ""
echo "🔄 Step 3: Updating requirements.txt..."

# Add docker to requirements if not already there
if ! grep -q "docker" requirements.txt 2>/dev/null; then
    echo "docker>=6.1.0" >> requirements.txt
    echo "✓ Added docker to requirements.txt"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Install SudoDog: pip3 install -e . --break-system-packages"
echo "2. Test Docker: docker run hello-world"
echo "3. Start daemon: sudodog daemon start"
echo "4. Run an agent: sudodog run --docker python test_agent.py"
echo ""
