import time
import os

print(f"Starting long task in container {os.getenv('HOSTNAME')}")

for i in range(10):
    print(f"Working... {i+1}/10")
    time.sleep(2)

print("Task complete!")
