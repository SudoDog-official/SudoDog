#!/usr/bin/env python3
"""
SudoDog Local Telemetry System
Tracks user metrics in local SQLite database with simple CLI queries.
"""

import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import platform


class LocalTelemetry:
    """Local telemetry system using SQLite."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize telemetry system."""
        if db_path is None:
            db_path = Path.home() / ".sudodog" / "telemetry.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path = Path.home() / ".sudodog" / "config.json"
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event TEXT NOT NULL,
                properties TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_timestamp 
            ON events(event, timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_timestamp 
            ON events(user_id, timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def is_enabled(self) -> bool:
        """Check if telemetry is enabled."""
        if not self.config_path.exists():
            return False
        
        try:
            config = json.loads(self.config_path.read_text())
            return config.get('telemetry_enabled', False)
        except:
            return False
    
    def enable(self):
        """Enable telemetry."""
        config = {}
        if self.config_path.exists():
            config = json.loads(self.config_path.read_text())
        
        config['telemetry_enabled'] = True
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(config, indent=2))
        print("✓ Telemetry enabled")
    
    def disable(self):
        """Disable telemetry."""
        config = {}
        if self.config_path.exists():
            config = json.loads(self.config_path.read_text())
        
        config['telemetry_enabled'] = False
        self.config_path.write_text(json.dumps(config, indent=2))
        print("✓ Telemetry disabled")
    
    def get_user_id(self) -> str:
        """Get or create anonymous user ID."""
        id_path = Path.home() / ".sudodog" / "telemetry_id"
        
        if id_path.exists():
            return id_path.read_text().strip()
        
        # Create new anonymous ID
        anon_id = f"anon-{uuid.uuid4().hex[:16]}"
        id_path.parent.mkdir(parents=True, exist_ok=True)
        id_path.write_text(anon_id)
        return anon_id
    
    def track_event(self, event: str, properties: Optional[Dict[str, Any]] = None):
        """Track an event."""
        if not self.is_enabled():
            return
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO events (user_id, event, properties, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                self.get_user_id(),
                event,
                json.dumps(properties or {}),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            # Fail silently - telemetry should never break the app
            pass
    
    # ===== ANALYTICS QUERIES =====
    
    def get_total_installs(self) -> int:
        """Get total number of installations."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE event = 'first_time_init'
        """)
        
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    def get_total_users(self) -> int:
        """Get total unique users."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM events
        """)
        
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    def get_active_users(self, days: int = 30) -> int:
        """Get active users in last N days."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM events
            WHERE timestamp >= ?
        """, (cutoff,))
        
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    def get_event_counts(self, days: int = 30) -> Dict[str, int]:
        """Get event counts for last N days."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT event, COUNT(*) as count
            FROM events
            WHERE timestamp >= ?
            GROUP BY event
            ORDER BY count DESC
        """, (cutoff,))
        
        results = dict(cursor.fetchall())
        conn.close()
        return results
    
    def get_daily_stats(self, days: int = 7) -> list:
        """Get daily usage statistics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_events,
                COUNT(DISTINCT user_id) as unique_users
            FROM events
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, (cutoff,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_feature_adoption(self) -> Dict[str, Any]:
        """Get feature adoption statistics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Total runs
        cursor.execute("""
            SELECT COUNT(*) FROM events WHERE event = 'sudodog_run'
        """)
        total_runs = cursor.fetchone()[0]
        
        # Docker usage
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE event = 'sudodog_run' 
            AND json_extract(properties, '$.docker') = 1
        """)
        docker_runs = cursor.fetchone()[0]
        
        # Custom images
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE event = 'sudodog_run' 
            AND json_extract(properties, '$.custom_image') = 1
        """)
        custom_image_runs = cursor.fetchone()[0]
        
        # Daemon usage
        cursor.execute("""
            SELECT COUNT(*) FROM events WHERE event = 'daemon_started'
        """)
        daemon_starts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_runs': total_runs,
            'docker_usage_pct': round((docker_runs / total_runs * 100) if total_runs > 0 else 0, 1),
            'custom_image_pct': round((custom_image_runs / total_runs * 100) if total_runs > 0 else 0, 1),
            'daemon_starts': daemon_starts,
        }
    
    def print_stats(self):
        """Print comprehensive statistics."""
        print("\n🐕 SudoDog Telemetry Statistics")
        print("=" * 60)
        
        # Overall stats
        total_installs = self.get_total_installs()
        total_users = self.get_total_users()
        dau = self.get_active_users(days=1)
        wau = self.get_active_users(days=7)
        mau = self.get_active_users(days=30)
        
        print(f"\n📊 Overview:")
        print(f"  Total Installations:    {total_installs:,}")
        print(f"  Total Users:            {total_users:,}")
        print(f"  Daily Active Users:     {dau:,}")
        print(f"  Weekly Active Users:    {wau:,}")
        print(f"  Monthly Active Users:   {mau:,}")
        
        # Event counts
        print(f"\n📈 Top Events (Last 30 Days):")
        event_counts = self.get_event_counts(days=30)
        for event, count in list(event_counts.items())[:10]:
            print(f"  {event:.<30} {count:>6,}")
        
        # Feature adoption
        print(f"\n🚀 Feature Adoption:")
        features = self.get_feature_adoption()
        print(f"  Total Agent Runs:       {features['total_runs']:,}")
        print(f"  Docker Mode:            {features['docker_usage_pct']}%")
        print(f"  Custom Images:          {features['custom_image_pct']}%")
        print(f"  Daemon Starts:          {features['daemon_starts']:,}")
        
        # Daily stats
        print(f"\n📅 Last 7 Days:")
        daily_stats = self.get_daily_stats(days=7)
        print(f"  {'Date':<12} {'Events':>10} {'Users':>10}")
        print(f"  {'-'*12} {'-'*10} {'-'*10}")
        for date, events, users in daily_stats:
            print(f"  {date:<12} {events:>10,} {users:>10,}")
        
        print("\n" + "=" * 60)


# ===== CLI Interface =====

def main():
    """CLI for viewing telemetry stats."""
    import sys
    
    telemetry = LocalTelemetry()
    
    if len(sys.argv) < 2:
        telemetry.print_stats()
        return
    
    command = sys.argv[1]
    
    if command == "enable":
        telemetry.enable()
    elif command == "disable":
        telemetry.disable()
    elif command == "status":
        if telemetry.is_enabled():
            print("✓ Telemetry is ENABLED")
        else:
            print("✗ Telemetry is DISABLED")
    elif command == "stats":
        telemetry.print_stats()
    elif command == "installs":
        print(f"Total Installations: {telemetry.get_total_installs():,}")
    elif command == "users":
        print(f"Total Users: {telemetry.get_total_users():,}")
    elif command == "dau":
        print(f"Daily Active Users: {telemetry.get_active_users(days=1):,}")
    elif command == "wau":
        print(f"Weekly Active Users: {telemetry.get_active_users(days=7):,}")
    elif command == "mau":
        print(f"Monthly Active Users: {telemetry.get_active_users(days=30):,}")
    else:
        print(f"Unknown command: {command}")
        print("\nAvailable commands:")
        print("  stats       - Show all statistics")
        print("  installs    - Total installations")
        print("  users       - Total unique users")
        print("  dau         - Daily active users")
        print("  wau         - Weekly active users")
        print("  mau         - Monthly active users")
        print("  enable      - Enable telemetry")
        print("  disable     - Disable telemetry")
        print("  status      - Check telemetry status")


if __name__ == "__main__":
    main()
