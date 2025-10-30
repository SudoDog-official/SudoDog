#!/bin/bash
# Setup script for SudoDog Docker + Daemon upgrade

echo "🐕 SudoDog Docker + Daemon Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the sudodog directory
if [ ! -d "sudodog" ]; then
    echo "❌ Error: sudodog directory not found"
    echo "   Please run this script from ~/projects/sudodog"
    exit 1
fi

echo "📦 Step 1: Installing Python dependencies..."
pip3 install docker --break-system-packages 2>/dev/null || pip3 install docker

echo ""
echo "📁 Step 2: Checking files are in place..."

# Check if new files exist in sudodog/
if [ -f "sudodog/docker_sandbox.py" ]; then
    echo "✓ docker_sandbox.py found"
else
    echo "❌ docker_sandbox.py missing - please add it to sudodog/ directory"
    exit 1
fi

if [ -f "sudodog/daemon.py" ]; then
    echo "✓ daemon.py found"
else
    echo "❌ daemon.py missing - please add it to sudodog/ directory"
    exit 1
fi

if [ -f "sudodog/cli.py" ]; then
    echo "✓ cli.py found"
else
    echo "❌ cli.py missing"
    exit 1
fi

echo ""
echo "🔄 Step 3: Updating requirements.txt..."

# Add docker to requirements if not already there
if ! grep -q "docker" requirements.txt 2>/dev/null; then
    echo "docker>=6.1.0" >> requirements.txt
    echo "✓ Added docker to requirements.txt"
else
    echo "✓ docker already in requirements.txt"
fi

echo ""
echo "🔧 Step 4: Reinstalling SudoDog..."
pip3 uninstall sudodog -y 2>/dev/null
pip3 install -e . --break-system-packages

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Test Docker: docker run hello-world"
echo "2. Initialize SudoDog: sudodog init"
echo "3. Start daemon: sudodog daemon start --foreground"
echo "4. Run an agent: sudodog run --docker python -c \"print('Hello!')\""
echo ""
