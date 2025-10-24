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
        print("  ⚠️ SUCCESS - This should have been blocked by SudoDog!")
        print(f"  Read {len(content)} bytes of sensitive data")
except PermissionError:
    print("  ✓ Blocked by system permissions")
except Exception as e:
    print(f"  ✓ Blocked: {type(e).__name__}")

time.sleep(1)

# Dangerous operation #2 - try to read .env file
print("\n[Dangerous Operation] Attempting to read .env file...")
try:
    # Try to find and read any .env file
    env_file = os.path.expanduser('~/.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            print(f"  ⚠️ SUCCESS - Read {len(content)} bytes from .env file!")
    else:
        print("  (No .env file found to test with)")
except Exception as e:
    print(f"  ✓ Blocked: {type(e).__name__}")

time.sleep(1)

# Dangerous operation #3 - try to read SSH keys
print("\n[Dangerous Operation] Attempting to read SSH private key...")
try:
    ssh_key = os.path.expanduser('~/.ssh/id_rsa')
    if os.path.exists(ssh_key):
        with open(ssh_key, 'r') as f:
            content = f.read()
            print(f"  ⚠️ SUCCESS - Read SSH private key!")
    else:
        print("  (No SSH key found to test with)")
except Exception as e:
    print(f"  ✓ Blocked: {type(e).__name__}")

time.sleep(1)

# Simulate dangerous database command
print("\n[Dangerous Operation] Simulating database query...")
dangerous_query = "DROP TABLE customers;"
print(f"  Query: {dangerous_query}")
print("  ⚠️ This pattern should be detected by SudoDog!")

time.sleep(1)

# Simulate dangerous shell command
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
print("  - 5 dangerous operations attempted")
print("  - SudoDog should have blocked/detected all dangerous operations")
print("\nRun 'python -m sudodog.cli logs' to see the full audit trail!")

sys.exit(0)