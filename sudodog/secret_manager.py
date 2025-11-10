#!/usr/bin/env python3
"""
SudoDog Secret Manager - Secure credential injection for AI agents
Provides environment variable injection with validation and audit logging
"""

import os
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path

class SecretManager:
    """Manages secure credential injection for containerized AI agents"""
    
    def __init__(self, audit_log_path: Optional[str] = None):
        # Try /var/log/sudodog first, fallback to ~/.sudodog/logs
        if audit_log_path is None:
            try:
                default_path = Path("/var/log/sudodog/secrets.log")
                default_path.parent.mkdir(parents=True, exist_ok=True)
                # Test if writable
                test_file = default_path.parent / ".write_test"
                test_file.touch()
                test_file.unlink()
                audit_log_path = str(default_path)
            except (PermissionError, OSError):
                # Fallback to user home directory
                home_path = Path.home() / ".sudodog" / "logs" / "secrets.log"
                home_path.parent.mkdir(parents=True, exist_ok=True)
                audit_log_path = str(home_path)
        
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup audit logging
        self.audit_logger = logging.getLogger('sudodog.secrets')
        self.audit_logger.setLevel(logging.INFO)
        
        if not self.audit_logger.handlers:
            handler = logging.FileHandler(self.audit_log_path)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.audit_logger.addHandler(handler)
    
    def validate_secret_name(self, name: str) -> bool:
        """Validate secret name follows secure naming conventions"""
        if not name:
            return False
        
        # Must be uppercase with underscores, alphanumeric only
        if not all(c.isupper() or c.isdigit() or c == '_' for c in name):
            return False
        
        # Must start with letter
        if not name[0].isalpha():
            return False
        
        # Reasonable length limits
        if len(name) < 2 or len(name) > 64:
            return False
        
        return True
    
    def validate_secret_value(self, value: str) -> bool:
        """Validate secret value meets security requirements"""
        if not value:
            return False
        
        # No newlines or null bytes
        if '\n' in value or '\0' in value:
            return False
        
        # Reasonable length limit
        if len(value) > 4096:
            return False
        
        return True
    
    def load_secrets_from_file(self, secrets_file: str) -> Dict[str, str]:
        """Load secrets from a JSON file with validation"""
        try:
            with open(secrets_file, 'r') as f:
                secrets = json.load(f)
            
            if not isinstance(secrets, dict):
                raise ValueError("Secrets file must contain a JSON object")
            
            validated_secrets = {}
            for name, value in secrets.items():
                if not self.validate_secret_name(name):
                    self.audit_logger.warning(f"Invalid secret name rejected: {name}")
                    continue
                
                if not self.validate_secret_value(str(value)):
                    self.audit_logger.warning(f"Invalid secret value rejected for: {name}")
                    continue
                
                validated_secrets[name] = str(value)
            
            self.audit_logger.info(f"Loaded {len(validated_secrets)} secrets from {secrets_file}")
            return validated_secrets
            
        except Exception as e:
            self.audit_logger.error(f"Failed to load secrets from {secrets_file}: {str(e)}")
            raise
    
    def inject_secrets(self, secrets: Dict[str, str], container_id: Optional[str] = None) -> List[str]:
        """
        Convert secrets to environment variable format for Docker
        Returns list of env var strings in format: KEY=value
        """
        env_vars = []
        
        for name, value in secrets.items():
            env_vars.append(f"{name}={value}")
            
            # Audit log (without revealing the actual value)
            self.audit_logger.info(
                f"Secret injected: {name} "
                f"(container: {container_id or 'N/A'}) "
                f"(length: {len(value)} chars)"
            )
        
        return env_vars
    
    def mask_secret(self, value: str, show_chars: int = 4) -> str:
        """Mask a secret value for logging purposes"""
        if len(value) <= show_chars:
            return '*' * len(value)
        
        return value[:show_chars] + '*' * (len(value) - show_chars)
    
    def audit_secret_access(self, secret_name: str, accessed_by: str, action: str):
        """Log secret access for audit trail"""
        self.audit_logger.info(
            f"Secret access: {secret_name} | "
            f"Accessed by: {accessed_by} | "
            f"Action: {action} | "
            f"Timestamp: {datetime.utcnow().isoformat()}"
        )
    
    def get_secret_stats(self) -> Dict:
        """Get statistics about secret usage"""
        stats = {
            'total_injections': 0,
            'unique_secrets': set(),
            'access_count_by_secret': {},
            'last_access': {}
        }
        
        try:
            if not self.audit_log_path.exists():
                return stats
                
            with open(self.audit_log_path, 'r') as f:
                for line in f:
                    if 'Secret injected:' in line:
                        stats['total_injections'] += 1
                        # Extract secret name from log
                        parts = line.split('Secret injected:')
                        if len(parts) > 1:
                            secret_name = parts[1].split('(')[0].strip()
                            stats['unique_secrets'].add(secret_name)
                            stats['access_count_by_secret'][secret_name] = \
                                stats['access_count_by_secret'].get(secret_name, 0) + 1
                            stats['last_access'][secret_name] = line.split(' - ')[0]
        
        except Exception as e:
            self.audit_logger.error(f"Failed to get secret stats: {str(e)}")
        
        # Convert set to list for JSON serialization
        stats['unique_secrets'] = list(stats['unique_secrets'])
        stats['unique_secret_count'] = len(stats['unique_secrets'])
        
        return stats
