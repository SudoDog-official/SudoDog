#!/usr/bin/env python3
"""
Simple Hello World Agent - Your First SudoDog Agent
This is a minimal agent to verify your SudoDog installation works
"""
import time

print("🤖 Hello from your AI agent!")
print("✓ SudoDog is protecting this execution")
print()

# Simple safe operation
print("Performing safe operations...")
time.sleep(0.5)

# Write a temp file
with open('/tmp/sudodog_hello.txt', 'w') as f:
    f.write("Hello from SudoDog!\n")
    f.write(f"Timestamp: {time.time()}\n")

print("✓ Created file: /tmp/sudodog_hello.txt")
print()
print("Success! Your SudoDog installation is working.")
print("Next steps:")
print("  1. Run: sudodog logs")
print("  2. Try: sudodog run python examples/demo_agent.py")
print("  3. Try: sudodog run --docker python examples/demo_agent.py")
