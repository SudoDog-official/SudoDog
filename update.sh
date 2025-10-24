#!/bin/bash
# Quick update script for SudoDog development

echo "🐕 Updating SudoDog..."
echo

# Make sure we're in the right directory
cd ~/projects/sudodog

# Activate virtual environment
source venv/bin/activate

# Reinstall in development mode
pip install -e . --force-reinstall --no-deps

echo
echo "✓ SudoDog updated!"
echo
echo "Test it with:"
echo "  python -m sudodog.cli run python3 test_agent.py"
echo
