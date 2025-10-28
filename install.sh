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
echo "Quick start:"
echo "  sudodog init          # Initialize SudoDog"
echo "  sudodog run python your_agent.py"
echo ""
echo "Documentation: https://github.com/SudoDog-official/sudodog"
echo "Support: support@sudodog.com"
