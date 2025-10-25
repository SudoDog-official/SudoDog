#!/bin/bash
set -e

echo "🐕 Installing SudoDog..."
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is required but not installed."
    echo "   Install it with: sudo apt install git"
    exit 1
fi

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is required but not installed."
    echo "   Install it with: sudo apt install python3"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ Error: pip is required but not installed."
    echo "   Install it with: sudo apt install python3-pip"
    exit 1
fi

echo "📦 Installing SudoDog from GitHub..."

# Try regular pip first, fall back to --break-system-packages if needed
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
echo "Quick start:"
echo "  sudodog init          # Initialize SudoDog"
echo "  sudodog run python your_agent.py"
echo ""
echo "Documentation: https://github.com/SudoDog-official/sudodog"
