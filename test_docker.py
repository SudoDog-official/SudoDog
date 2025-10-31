import os
print("Hello from Docker!")
print(f"Container hostname: {os.getenv('HOSTNAME', 'N/A')}")
print(f"SudoDog session: {os.getenv('SUDODOG_SESSION', 'N/A')}")
