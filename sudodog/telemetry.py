"""
SudoDog - Telemetry Module
Privacy-first anonymous usage analytics
"""

import os
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any


class Telemetry:
    """
    Anonymous telemetry collection for improving SudoDog
    
    Privacy principles:
    - Opt-in only (user must consent)
    - Anonymous (no PII)
    - Transparent (show what's collected)
    - Configurable (easy to disable)
    """
    
    def __init__(self, endpoint: Optional[str] = None):
        self.config_dir = Path.home() / '.sudodog'
        self.config_file = self.config_dir / 'config.json'
        self.telemetry_endpoint = endpoint or 'https://www.sudodog.com/api/telemetry'
        # Load config
        self.config = self._load_config()
        self.enabled = self.config.get('telemetry_enabled', False)
        self.anonymous_id = self.config.get('anonymous_id', None)
        
        # Generate anonymous ID if telemetry enabled
        if self.enabled and not self.anonymous_id:
            self.anonymous_id = self._generate_anonymous_id()
            self._save_anonymous_id()
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_config(self) -> None:
        """Save configuration"""
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass
    
    def _generate_anonymous_id(self) -> str:
        """
        Generate anonymous user ID
        Uses machine-specific hash (not reversible to user identity)
        """
        # Use multiple machine identifiers
        machine_info = f"{os.uname().nodename}-{os.uname().machine}"
        
        # Hash to ensure anonymity
        hash_obj = hashlib.sha256(machine_info.encode())
        return f"anon-{hash_obj.hexdigest()[:16]}"
    
    def _save_anonymous_id(self) -> None:
        """Save anonymous ID to config"""
        self.config['anonymous_id'] = self.anonymous_id
        self._save_config()
    
    def enable(self) -> None:
        """Enable telemetry"""
        self.enabled = True
        self.config['telemetry_enabled'] = True
        
        if not self.anonymous_id:
            self.anonymous_id = self._generate_anonymous_id()
        
        self.config['anonymous_id'] = self.anonymous_id
        self.config['telemetry_enabled_at'] = datetime.now().isoformat()
        self._save_config()
    
    def disable(self) -> None:
        """Disable telemetry"""
        self.enabled = False
        self.config['telemetry_enabled'] = False
        self.config['telemetry_disabled_at'] = datetime.now().isoformat()
        self._save_config()
    
    def is_enabled(self) -> bool:
        """Check if telemetry is enabled"""
        return self.enabled
    
    def track_event(self, event_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track an anonymous event
        
        Args:
            event_type: Type of event (e.g., 'command_run', 'error')
            properties: Anonymous properties (no PII!)
        """
        if not self.enabled:
            return
        
        # Build event payload (all anonymous)
        event = {
            'anonymous_id': self.anonymous_id,
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'version': self._get_version(),
            'properties': properties or {}
        }
        
        # Send asynchronously (don't block user)
        try:
            # In production, use a queue + background worker
            # For now, send with short timeout
            requests.post(
                self.telemetry_endpoint,
                json=event,
                timeout=2,  # Don't block user
                headers={'Content-Type': 'application/json'}
            )
        except Exception:
            # Silently fail - never break user experience
            pass
    
    def track_command(self, command: str, options: Dict[str, Any]) -> None:
        """
        Track command usage (anonymous)
        
        NEVER collects:
        - Actual command arguments
        - File paths
        - User data
        """
        if not self.enabled:
            return
        
        # Only track which command was used, not arguments
        properties = {
            'command': command,  # e.g., 'run', 'logs', 'daemon'
            'used_docker': options.get('docker', False),
            'used_rollback': options.get('rollback', False),
            # Resource limits (aggregated for improvement)
            'cpu_limit': options.get('cpu_limit') if options.get('docker') else None,
            'memory_limit': options.get('memory_limit') if options.get('docker') else None,
        }
        
        self.track_event('command_used', properties)
    
    def track_error(self, error_type: str, error_message: str) -> None:
        """
        Track errors (helps us fix bugs)
        
        NEVER collects:
        - File paths from error
        - User data from error
        """
        if not self.enabled:
            return
        
        # Sanitize error message (remove paths, usernames, etc.)
        sanitized_message = self._sanitize_error(error_message)
        
        properties = {
            'error_type': error_type,
            'error_message': sanitized_message[:200],  # Truncate
        }
        
        self.track_event('error_occurred', properties)
    
    def track_daemon_stats(self, container_count: int, avg_cpu: float, avg_memory: float) -> None:
        """
        Track daemon statistics (aggregated, anonymous)
        
        Helps us understand typical usage patterns
        """
        if not self.enabled:
            return
        
        properties = {
            'container_count': container_count,
            'avg_cpu_percent': round(avg_cpu, 1),
            'avg_memory_percent': round(avg_memory, 1),
        }
        
        self.track_event('daemon_stats', properties)
    
    def track_threat_detection(self, pattern_type: str, action_taken: str) -> None:
        """
        Track threat detection (helps improve detection)
        
        NEVER collects:
        - Actual command that was blocked
        - User data
        - File contents
        """
        if not self.enabled:
            return
        
        properties = {
            'pattern_type': pattern_type,  # e.g., 'sql_injection', 'file_deletion'
            'action_taken': action_taken,  # e.g., 'blocked', 'warned', 'allowed'
        }
        
        self.track_event('threat_detected', properties)
    
    def track_install(self) -> None:
        """Track successful installation"""
        if not self.enabled:
            return
        
        properties = {
            'os': os.uname().sysname,
            'arch': os.uname().machine,
        }
        
        self.track_event('install_completed', properties)
    
    def _sanitize_error(self, error_message: str) -> str:
        """
        Remove PII from error messages
        """
        import re
        
        # Remove file paths
        sanitized = re.sub(r'/[^\s]+', '/[PATH]', error_message)
        
        # Remove what looks like usernames
        sanitized = re.sub(r'/home/[^/\s]+', '/home/[USER]', sanitized)
        
        # Remove what looks like IPs
        sanitized = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP]', sanitized)
        
        return sanitized
    
    def _get_version(self) -> str:
        """Get SudoDog version"""
        try:
            from importlib.metadata import version
            return version('sudodog')
        except Exception:
            return '0.1.0'  # Fallback
    
    def get_status(self) -> Dict:
        """Get telemetry status"""
        return {
            'enabled': self.enabled,
            'anonymous_id': self.anonymous_id if self.enabled else None,
            'endpoint': self.telemetry_endpoint,
        }


# Global telemetry instance
_telemetry_instance = None


def get_telemetry() -> Telemetry:
    """Get global telemetry instance"""
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = Telemetry()
    return _telemetry_instance
SudoDog - Telemetry Module
Privacy-first anonymous usage analytics
"""

import os
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any


class Telemetry:
    """
    Anonymous telemetry collection for improving SudoDog
    
    Privacy principles:
    - Opt-in only (user must consent)
    - Anonymous (no PII)
    - Transparent (show what's collected)
    - Configurable (easy to disable)
    """
    
    def __init__(self, endpoint: Optional[str] = None):
        self.config_dir = Path.home() / '.sudodog'
        self.config_file = self.config_dir / 'config.json'
        self.telemetry_endpoint = endpoint or 'https://telemetry.sudodog.com/v1/events'
        
        # Load config
        self.config = self._load_config()
        self.enabled = self.config.get('telemetry_enabled', False)
        self.anonymous_id = self.config.get('anonymous_id', None)
        
        # Generate anonymous ID if telemetry enabled
        if self.enabled and not self.anonymous_id:
            self.anonymous_id = self._generate_anonymous_id()
            self._save_anonymous_id()
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_config(self) -> None:
        """Save configuration"""
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass
    
    def _generate_anonymous_id(self) -> str:
        """
        Generate anonymous user ID
        Uses machine-specific hash (not reversible to user identity)
        """
        # Use multiple machine identifiers
        machine_info = f"{os.uname().nodename}-{os.uname().machine}"
        
        # Hash to ensure anonymity
        hash_obj = hashlib.sha256(machine_info.encode())
        return f"anon-{hash_obj.hexdigest()[:16]}"
    
    def _save_anonymous_id(self) -> None:
        """Save anonymous ID to config"""
        self.config['anonymous_id'] = self.anonymous_id
        self._save_config()
    
    def enable(self) -> None:
        """Enable telemetry"""
        self.enabled = True
        self.config['telemetry_enabled'] = True
        
        if not self.anonymous_id:
            self.anonymous_id = self._generate_anonymous_id()
        
        self.config['anonymous_id'] = self.anonymous_id
        self.config['telemetry_enabled_at'] = datetime.now().isoformat()
        self._save_config()
    
    def disable(self) -> None:
        """Disable telemetry"""
        self.enabled = False
        self.config['telemetry_enabled'] = False
        self.config['telemetry_disabled_at'] = datetime.now().isoformat()
        self._save_config()
    
    def is_enabled(self) -> bool:
        """Check if telemetry is enabled"""
        return self.enabled
    
    def track_event(self, event_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track an anonymous event
        
        Args:
            event_type: Type of event (e.g., 'command_run', 'error')
            properties: Anonymous properties (no PII!)
        """
        if not self.enabled:
            return
        
        # Build event payload (all anonymous)
        event = {
            'anonymous_id': self.anonymous_id,
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'version': self._get_version(),
            'properties': properties or {}
        }
        
        # Send asynchronously (don't block user)
        try:
            # In production, use a queue + background worker
            # For now, send with short timeout
            requests.post(
                self.telemetry_endpoint,
                json=event,
                timeout=2,  # Don't block user
                headers={'Content-Type': 'application/json'}
            )
        except Exception:
            # Silently fail - never break user experience
            pass
    
    def track_command(self, command: str, options: Dict[str, Any]) -> None:
        """
        Track command usage (anonymous)
        
        NEVER collects:
        - Actual command arguments
        - File paths
        - User data
        """
        if not self.enabled:
            return
        
        # Only track which command was used, not arguments
        properties = {
            'command': command,  # e.g., 'run', 'logs', 'daemon'
            'used_docker': options.get('docker', False),
            'used_rollback': options.get('rollback', False),
            # Resource limits (aggregated for improvement)
            'cpu_limit': options.get('cpu_limit') if options.get('docker') else None,
            'memory_limit': options.get('memory_limit') if options.get('docker') else None,
        }
        
        self.track_event('command_used', properties)
    
    def track_error(self, error_type: str, error_message: str) -> None:
        """
        Track errors (helps us fix bugs)
        
        NEVER collects:
        - File paths from error
        - User data from error
        """
        if not self.enabled:
            return
        
        # Sanitize error message (remove paths, usernames, etc.)
        sanitized_message = self._sanitize_error(error_message)
        
        properties = {
            'error_type': error_type,
            'error_message': sanitized_message[:200],  # Truncate
        }
        
        self.track_event('error_occurred', properties)
    
    def track_daemon_stats(self, container_count: int, avg_cpu: float, avg_memory: float) -> None:
        """
        Track daemon statistics (aggregated, anonymous)
        
        Helps us understand typical usage patterns
        """
        if not self.enabled:
            return
        
        properties = {
            'container_count': container_count,
            'avg_cpu_percent': round(avg_cpu, 1),
            'avg_memory_percent': round(avg_memory, 1),
        }
        
        self.track_event('daemon_stats', properties)
    
    def track_threat_detection(self, pattern_type: str, action_taken: str) -> None:
        """
        Track threat detection (helps improve detection)
        
        NEVER collects:
        - Actual command that was blocked
        - User data
        - File contents
        """
        if not self.enabled:
            return
        
        properties = {
            'pattern_type': pattern_type,  # e.g., 'sql_injection', 'file_deletion'
            'action_taken': action_taken,  # e.g., 'blocked', 'warned', 'allowed'
        }
        
        self.track_event('threat_detected', properties)
    
    def track_install(self) -> None:
        """Track successful installation"""
        if not self.enabled:
            return
        
        properties = {
            'os': os.uname().sysname,
            'arch': os.uname().machine,
        }
        
        self.track_event('install_completed', properties)
    
    def _sanitize_error(self, error_message: str) -> str:
        """
        Remove PII from error messages
        """
        import re
        
        # Remove file paths
        sanitized = re.sub(r'/[^\s]+', '/[PATH]', error_message)
        
        # Remove what looks like usernames
        sanitized = re.sub(r'/home/[^/\s]+', '/home/[USER]', sanitized)
        
        # Remove what looks like IPs
        sanitized = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP]', sanitized)
        
        return sanitized
    
    def _get_version(self) -> str:
        """Get SudoDog version"""
        try:
            from importlib.metadata import version
            return version('sudodog')
        except Exception:
            return '0.1.0'  # Fallback
    
    def get_status(self) -> Dict:
        """Get telemetry status"""
        return {
            'enabled': self.enabled,
            'anonymous_id': self.anonymous_id if self.enabled else None,
            'endpoint': self.telemetry_endpoint,
        }


# Global telemetry instance
_telemetry_instance = None


def get_telemetry() -> Telemetry:
    """Get global telemetry instance"""
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = Telemetry()
    return _telemetry_instance
