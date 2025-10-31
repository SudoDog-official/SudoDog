# test_dangerous_agent.py
import os
import subprocess
import time

print("🐕 Testing SudoDog Security Monitoring\n")

# Safe operations
print("✓ Safe: Reading system info...")
os.system("uname -a")
time.sleep(1)

print("\n✓ Safe: Creating temp file...")
with open("/tmp/test_file.txt", "w") as f:
    f.write("Test data")
time.sleep(1)

# Dangerous operations (should be caught)
print("\n⚠️ Dangerous: Attempting to read shadow file...")
try:
    with open("/etc/shadow", "r") as f:
        f.read()
except PermissionError:
    print("  (Blocked by permissions)")
time.sleep(1)

print("\n⚠️ Dangerous: Simulating SQL injection...")
dangerous_sql = "DROP TABLE users; DELETE FROM customers;"
print(f"  Query: {dangerous_sql}")
time.sleep(1)

print("\n⚠️ Dangerous: Simulating file deletion...")
dangerous_cmd = "rm -rf /important/data"
print(f"  Command: {dangerous_cmd}")
# Don't actually run it!

print("\n✅ Test complete! Check sudodog logs")
