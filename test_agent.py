#!/usr/bin/env python3
"""
Demo AI Agent for testing SudoDog
This simulates an AI agent that does various operations
"""
import time
import os
import sys

print("🤖 AI Agent Starting...")
print("Analyzing environment...")
time.sleep(1)

# Safe operation - read a file
print("\n[Safe Operation] Reading OS information...")
try:
    with open('/etc/os-release', 'r') as f:
        lines = f.readlines()[:3]
        for line in lines:
            print(f"  {line.strip()}")
except Exception as e:
    print(f"  Error: {e}")
time.sleep(1)

# Safe operation - write to temp
print("\n[Safe Operation] Creating temporary file...")
try:
    temp_file = '/tmp/sudodog_test.txt'
    with open(temp_file, 'w') as f:
        f.write("AI agent was here\n")
        f.write(f"Timestamp: {time.time()}\n")
    print(f"  ✓ Created: {temp_file}")
except Exception as e:
    print(f"  ✗ Error: {e}")
time.sleep(1)

# Dangerous operation #1 - try to read sensitive file
print("\n[Dangerous Operation] Attempting to read /etc/shadow...")
try:
    with open('/etc/shadow', 'r') as f:
        content = f.read()
        print("  ⚠️ SUCCESS - This should have been blocked!")
        print(f"  Read {len(content)} bytes of sensitive data")
except PermissionError:
    print("  ✓ Blocked by system permissions")
except Exception as e:
    print(f"  ✓ Blocked: {type(e).__name__}")
time.sleep(1)

# Dangerous operation #2 - simulate SQL injection
print("\n[Dangerous Operation] Simulating database query...")
dangerous_query = "DROP TABLE customers; DELETE FROM users;"
print(f"  Query: {dangerous_query}")
print("  ⚠️ This pattern should be detected by SudoDog!")
time.sleep(1)

# Dangerous operation #3 - simulate dangerous shell command
print("\n[Dangerous Operation] Simulating file deletion...")
dangerous_command = "rm -rf /important/data"
print(f"  Command: {dangerous_command}")
print("  ⚠️ This pattern should be detected by SudoDog!")
time.sleep(1)

print("\n" + "="*50)
print("✓ AI Agent completed all operations")
print("="*50)
print("\nSummary:")
print("  - 2 safe operations (OS info, temp file)")
print("  - 3 dangerous operations attempted")
print("  - SudoDog should have logged/detected all operations")
print("\nRun 'sudodog logs' to see the full audit trail!")

sys.exit(0)
