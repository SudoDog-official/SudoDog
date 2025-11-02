"""
Platform Telemetry - Send data to SudoDog Platform
"""

import requests
from datetime import datetime
import uuid
from pathlib import Path
import json

PLATFORM_API = "https://sudodog-platform.fly.dev/api/telemetry"

def get_or_create_user_id():
    """Get or create anonymous user ID"""
    config_dir = Path.home() / '.sudodog'
    config_dir.mkdir(exist_ok=True)
    
    user_id_file = config_dir / 'user_id.txt'
    
    if user_id_file.exists():
        return user_id_file.read_text().strip()
    else:
        user_id = f"free-user-{uuid.uuid4().hex[:8]}"
        user_id_file.write_text(user_id)
        return user_id

def send_platform_telemetry(event_type, data):
    """Send telemetry to SudoDog Platform (silent fail)"""
    try:
        user_id = get_or_create_user_id()
        
        payload = {
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat() + "Z",
            "data": data
        }
        
        requests.post(PLATFORM_API, json=payload, timeout=2)
    except:
        # Silent fail - never break the CLI
        pass
