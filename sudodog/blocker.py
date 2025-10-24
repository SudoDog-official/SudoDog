"""
SudoDog - Blocking Logic
Simple but effective blocking for AI agent security
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional

class AgentBlocker:
    """Implements blocking rules for AI agents"""
    
    # Sensitive files that agents should never access
    BLOCKED_READ_PATHS = [
        '/etc/shadow',           # Password hashes
        '/etc/passwd',           # User accounts
        '/etc/sudoers',          # Sudo config
        '~/.ssh/id_rsa',         # SSH private keys
        '~/.ssh/id_ed25519',     # SSH private keys
        '~/.aws/credentials',    # AWS credentials
        '~/.config/gcloud/',     # Google Cloud credentials
        '.env',                  # Environment variables
        '.env.local',            # Local environment
        '.env.production',       # Production environment
        '~/.docker/config.json', # Docker credentials
        '~/.kube/config',        # Kubernetes config
    ]
    
    # Paths that should never be written to
    BLOCKED_WRITE_PATHS = [
        '/etc/',                 # System configuration
        '/usr/bin/',             # System binaries
        '/usr/sbin/',            # System admin binaries
        '/bin/',                 # Essential binaries
        '/sbin/',                # System binaries
        '/boot/',                # Boot files
        '/sys/',                 # System files
        '/proc/',                # Process files
    ]
    
    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        # Database operations
        r'DROP\s+TABLE',
        r'DROP\s+DATABASE',
        r'TRUNCATE\s+TABLE',
        r'DELETE\s+FROM\s+\w+\s*;?\s*$',  # DELETE without WHERE
        
        # File system operations
        r'rm\s+-rf\s+/',
        r'rm\s+-rf\s+\*',
        r'sudo\s+rm',
        r'chmod\s+777',
        
        # System operations
        r'mkfs\.',               # Format filesystem
        r'dd\s+if=',             # Disk operations
        r':(){ :|:& };:',        # Fork bomb
        
        # Network exfiltration
        r'curl.*pastebin',
        r'wget.*pastebin',
    ]
    
    def __init__(self, policy='default'):
        self.policy = policy
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.DANGEROUS_PATTERNS]
    
    def check_file_read(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if file read should be allowed
        
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        expanded_path = os.path.expanduser(path)
        
        for blocked in self.BLOCKED_READ_PATHS:
            blocked_expanded = os.path.expanduser(blocked)
            
            # Check exact match
            if expanded_path == blocked_expanded:
                return False, f"Access to {path} is blocked (sensitive file)"
            
            # Check if path is within blocked directory
            if blocked_expanded.endswith('/'):
                if expanded_path.startswith(blocked_expanded):
                    return False, f"Access to {path} is blocked (sensitive directory)"
            
            # Check pattern match (for *.env files)
            if '*' in blocked:
                pattern = blocked.replace('*', '.*')
                if re.search(pattern, path):
                    return False, f"Access to {path} is blocked (matches sensitive pattern)"
        
        return True, None
    
    def check_file_write(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if file write should be allowed
        
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        expanded_path = os.path.expanduser(path)
        
        for blocked in self.BLOCKED_WRITE_PATHS:
            if expanded_path.startswith(blocked):
                return False, f"Write to {path} is blocked (system directory)"
        
        return True, None
    
    def check_command(self, command: str) -> Tuple[bool, Optional[str], List[str]]:
        """
        Check if command contains dangerous patterns
        
        Returns:
            (allowed: bool, reason: Optional[str], matched_patterns: List[str])
        """
        matched_patterns = []
        
        for pattern in self.compiled_patterns:
            if pattern.search(command):
                matched_patterns.append(pattern.pattern)
        
        if matched_patterns:
            reason = f"Command contains dangerous patterns: {', '.join(matched_patterns[:2])}"
            return False, reason, matched_patterns
        
        return True, None, []
    
    def should_block(self, action_type: str, target: str) -> Tuple[bool, Optional[str]]:
        """
        Main blocking decision function
        
        Args:
            action_type: Type of action ('file_read', 'file_write', 'command', etc.)
            target: The target of the action (file path, command string, etc.)
        
        Returns:
            (should_block: bool, reason: Optional[str])
        """
        if action_type == 'file_read':
            allowed, reason = self.check_file_read(target)
            return not allowed, reason
        
        elif action_type == 'file_write':
            allowed, reason = self.check_file_write(target)
            return not allowed, reason
        
        elif action_type == 'command':
            allowed, reason, _ = self.check_command(target)
            return not allowed, reason
        
        # Unknown action types are allowed by default
        return False, None


class FileRollback:
    """Handles rollback of file operations"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.backup_dir = Path.home() / '.sudodog' / 'backups' / session_id
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.operations = []
    
    def backup_file(self, file_path: str) -> bool:
        """
        Create backup of file before it's modified
        
        Returns:
            True if backup successful, False otherwise
        """
        try:
            source = Path(file_path)
            
            if not source.exists():
                # File doesn't exist yet (will be created)
                self.operations.append({
                    'type': 'create',
                    'path': file_path,
                    'backup': None
                })
                return True
            
            # Create backup
            backup_path = self.backup_dir / source.name
            
            # If backup already exists, append number
            counter = 1
            while backup_path.exists():
                backup_path = self.backup_dir / f"{source.stem}_{counter}{source.suffix}"
                counter += 1
            
            # Copy file to backup
            import shutil
            shutil.copy2(source, backup_path)
            
            self.operations.append({
                'type': 'modify',
                'path': file_path,
                'backup': str(backup_path)
            })
            
            return True
            
        except Exception as e:
            print(f"Backup failed for {file_path}: {e}")
            return False
    
    def rollback(self, steps: int = None) -> Tuple[int, List[str]]:
        """
        Rollback file operations
        
        Args:
            steps: Number of operations to rollback (None = all)
        
        Returns:
            (num_rolled_back: int, errors: List[str])
        """
        import shutil
        
        if steps is None:
            steps = len(self.operations)
        
        operations_to_rollback = self.operations[-steps:]
        rolled_back = 0
        errors = []
        
        for op in reversed(operations_to_rollback):
            try:
                if op['type'] == 'create':
                    # Delete file that was created
                    path = Path(op['path'])
                    if path.exists():
                        path.unlink()
                        rolled_back += 1
                
                elif op['type'] == 'modify':
                    # Restore from backup
                    if op['backup']:
                        shutil.copy2(op['backup'], op['path'])
                        rolled_back += 1
                
            except Exception as e:
                errors.append(f"Failed to rollback {op['path']}: {e}")
        
        return rolled_back, errors
    
    def cleanup(self):
        """Remove backup directory"""
        import shutil
        try:
            shutil.rmtree(self.backup_dir)
        except:
            pass
