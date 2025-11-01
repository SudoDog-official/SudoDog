#!/bin/bash
set -e

echo "🐕 Installing SudoDog..."
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Unable to detect OS"
    exit 1
fi

# Function to install packages based on OS
install_package() {
    case $OS in
        ubuntu|debian)
            sudo apt-get update -qq
            sudo apt-get install -y "$@"
            ;;
        fedora|centos|rhel)
            sudo dnf install -y "$@"
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm "$@"
            ;;
        *)
            echo "❌ Unsupported OS: $OS"
            exit 1
            ;;
    esac
}

# Check and install git
if ! command -v git &> /dev/null; then
    echo "📦 Installing git..."
    install_package git
fi

# Check and install python3
if ! command -v python3 &> /dev/null; then
    echo "📦 Installing python3..."
    case $OS in
        ubuntu|debian)
            install_package python3 python3-pip
            ;;
        fedora|centos|rhel)
            install_package python3 python3-pip
            ;;
        arch|manjaro)
            install_package python python-pip
            ;;
    esac
fi

# Check and install pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "📦 Installing pip..."
    case $OS in
        ubuntu|debian)
            install_package python3-pip
            ;;
        fedora|centos|rhel)
            install_package python3-pip
            ;;
        arch|manjaro)
            install_package python-pip
            ;;
    esac
fi

echo "✅ All dependencies installed!"
echo ""
echo "📦 Installing SudoDog from GitHub..."

# Try installing with pip, handle different scenarios
if pip3 install git+https://github.com/SudoDog-official/sudodog.git 2>/dev/null; then
    echo "✅ Installed with pip3"
elif pip3 install git+https://github.com/SudoDog-official/sudodog.git --break-system-packages 2>/dev/null; then
    echo "✅ Installed with pip3 --break-system-packages"
elif pip install git+https://github.com/SudoDog-official/sudodog.git 2>/dev/null; then
    echo "✅ Installed with pip"
elif pip install git+https://github.com/SudoDog-official/sudodog.git --break-system-packages; then
    echo "✅ Installed with pip --break-system-packages"
else
    echo "❌ Installation failed. Please try manually:"
    echo "   pip3 install git+https://github.com/SudoDog-official/sudodog.git --break-system-packages"
    exit 1
fi

echo ""
echo "✅ SudoDog installed successfully!"
echo ""

# Create examples directory with sample agents
echo "📝 Creating sample agents..."
mkdir -p ~/sudodog-examples
cd ~/sudodog-examples

# Create hello world agent
cat > hello_agent.py << 'EOF'
#!/usr/bin/env python3
"""Simple Hello World Agent - Your First SudoDog Agent"""
import time

print("🤖 Hello from your AI agent!")
print("✓ SudoDog is protecting this execution\n")

print("Performing safe operations...")
time.sleep(0.5)

with open('/tmp/sudodog_hello.txt', 'w') as f:
    f.write("Hello from SudoDog!\n")
    f.write(f"Timestamp: {time.time()}\n")

print("✓ Created file: /tmp/sudodog_hello.txt\n")
print("Success! Your SudoDog installation is working.")
print("Next steps:")
print("  1. Run: sudodog logs")
print("  2. Try: sudodog run python ~/sudodog-examples/demo_agent.py")
EOF

# Create demo agent
cat > demo_agent.py << 'EOF'
#!/usr/bin/env python3
"""Demo AI Agent - Shows SudoDog security features in action"""
import time
import sys

print("🤖 AI Agent Starting...")
time.sleep(1)

print("\n[Safe Operation] Reading OS information...")
try:
    with open('/etc/os-release', 'r') as f:
        lines = f.readlines()[:3]
        for line in lines:
            print(f"  {line.strip()}")
except Exception as e:
    print(f"  Error: {e}")
time.sleep(1)

print("\n[Safe Operation] Creating temporary file...")
with open('/tmp/sudodog_test.txt', 'w') as f:
    f.write("AI agent was here\n")
print(f"  ✓ Created: /tmp/sudodog_test.txt")
time.sleep(1)

print("\n[Dangerous Operation] Attempting to read /etc/shadow...")
try:
    with open('/etc/shadow', 'r') as f:
        content = f.read()
except PermissionError:
    print("  ✓ Blocked by container isolation")
except Exception as e:
    print(f"  ✓ Blocked: {type(e).__name__}")
time.sleep(1)

print("\n[Dangerous Operation] Simulating database query...")
print("  Query: DROP TABLE customers;")
print("  ⚠️ Pattern detected by SudoDog!")

print("\n✓ Demo complete! Run 'sudodog logs' to see the audit trail")
sys.exit(0)
EOF

chmod +x hello_agent.py demo_agent.py
echo "  ✓ Created ~/sudodog-examples/"

echo ""
echo "🎉 Ready to go! Try these commands:"
echo ""
echo "  # 1. Initialize SudoDog"
echo "  sudodog init"
echo ""
echo "  # 2. Run your first agent (basic isolation)"
echo "  sudodog run python ~/sudodog-examples/hello_agent.py"
echo ""
echo "  # 3. Run with Docker (stronger isolation + monitoring)"
echo "  sudodog run --docker python ~/sudodog-examples/demo_agent.py"
echo ""
echo "  # 4. View the security audit trail"
echo "  sudodog logs"
echo ""
echo "📚 Documentation: https://github.com/SudoDog-official/sudodog#readme"
echo "💡 Need help? support@sudodog.com"
echo ""
echo "Note: For Docker features, install Docker first:"
echo "  curl -fsSL https://get.docker.com | sudo sh"
echo ""
