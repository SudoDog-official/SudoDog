#!/bin/bash
# SudoDog Installation Script
# curl -sL install.sudodog.com | bash

set -e

SUDODOG_VERSION="0.1.0"
INSTALL_DIR="$HOME/.local/bin"
PYTHON_MIN_VERSION="3.8"

echo "🐕 SudoDog Installer v${SUDODOG_VERSION}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Check if running on Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo "❌ Error: SudoDog currently only supports Linux"
    echo "   macOS support coming soon!"
    exit 1
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Install Python 3.8+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python ${PYTHON_VERSION}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    echo "   Install pip3 and try again"
    exit 1
fi

echo "✓ Found pip3"

# Create install directory
mkdir -p "$INSTALL_DIR"

# Install SudoDog
echo
echo "📦 Installing SudoDog..."
pip3 install --user sudodog

# Check if install dir is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo
    echo "⚠️  Warning: $INSTALL_DIR is not in your PATH"
    echo
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo
fi

# Initialize SudoDog
echo
echo "🔧 Initializing SudoDog..."
sudodog init

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SudoDog installed successfully!"
echo
echo "Get started:"
echo "  sudodog run python your_agent.py"
echo
echo "Learn more:"
echo "  sudodog --help"
echo "  https://docs.sudodog.com"
echo