#!/usr/bin/env python3
"""
SudoDog Stats - Simple CLI to view telemetry metrics
Usage: python sudodog_stats.py [command]
"""

from sudodog_telemetry import LocalTelemetry

def main():
    import sys
    
    telemetry = LocalTelemetry()
    
    if not telemetry.is_enabled():
        print("⚠️  Telemetry is currently DISABLED")
        print("No stats are being collected.")
        print("\nTo enable: sudodog telemetry enable")
        return
    
    # If no command, show full stats
    if len(sys.argv) < 2:
        telemetry.print_stats()
        return
    
    command = sys.argv[1]
    
    # Simple commands
    commands = {
        'installs': lambda: print(f"Total Installations: {telemetry.get_total_installs():,}"),
        'users': lambda: print(f"Total Users: {telemetry.get_total_users():,}"),
        'dau': lambda: print(f"Daily Active Users: {telemetry.get_active_users(days=1):,}"),
        'wau': lambda: print(f"Weekly Active Users: {telemetry.get_active_users(days=7):,}"),
        'mau': lambda: print(f"Monthly Active Users: {telemetry.get_active_users(days=30):,}"),
    }
    
    if command in commands:
        commands[command]()
    elif command == "help":
        print("SudoDog Stats Commands:")
        print("  (no command)  - Show all statistics")
        print("  installs      - Total installations")
        print("  users         - Total unique users")
        print("  dau           - Daily active users")
        print("  wau           - Weekly active users")
        print("  mau           - Monthly active users")
        print("  help          - Show this help")
    else:
        print(f"Unknown command: {command}")
        print("Try: python sudodog_stats.py help")


if __name__ == "__main__":
    main()
