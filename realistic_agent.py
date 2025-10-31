#!/usr/bin/env python3
"""
Realistic AI Agent - Simulates a LangChain-style agent
that reads files, makes API calls, and writes results
"""
import time
import requests
import json
import os

print("🤖 LangChain Agent Starting...")
print("Task: Research and save report")

# Step 1: Read some configuration
print("\n[1/5] Reading configuration...")
try:
    # Try to read a config file
    if os.path.exists('.env'):
        print("  ⚠️ Found .env file - this should be protected!")
    else:
        print("  ✓ No sensitive files found")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(1)

# Step 2: Make API call (simulate)
print("\n[2/5] Making API call to fetch data...")
print("  URL: https://api.example.com/data")
print("  ✓ Data received (simulated)")

time.sleep(1)

# Step 3: Process data
print("\n[3/5] Processing data...")
data = {"result": "Important findings", "timestamp": time.time()}
print(f"  ✓ Processed {len(data)} items")

time.sleep(1)

# Step 4: Write results
print("\n[4/5] Writing results to file...")
try:
    output_file = '/tmp/agent_report.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  ✓ Saved to: {output_file}")
except Exception as e:
    print(f"  ✗ Error: {e}")

time.sleep(1)

# Step 5: Cleanup (dangerous command)
print("\n[5/5] Cleanup temporary files...")
cleanup_cmd = "rm -rf /tmp/old_data"
print(f"  Command: {cleanup_cmd}")
print("  ⚠️ This is a dangerous pattern!")

time.sleep(1)

print("\n✅ Agent completed successfully!")
print("Report saved to /tmp/agent_report.json")
