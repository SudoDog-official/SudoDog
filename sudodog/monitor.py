"""
SudoDog - Process Monitoring Module
Monitors system calls and file/network access
"""

import subprocess
import psutil
import os
import sys
from pathlib import Path
from datetime import datetime
import json
from rich.console import Console
from .blocker import AgentBlocker, FileRollback
from .sandbox import SandboxPresets

console = Console()

class AgentMonitor:
    """Monitor AI agent execution"""
    
    def __init__(self, command, policy='default', session_id=None, use_sandbox=True):
        self.command = command
        self.policy = policy
        self.session_id = session_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = Path.home() / '.sudodog' / 'logs' / f'{self.session_id}.jsonl'
        self.process = None
        self.actions = []
        self.blocker = AgentBlocker(policy)
        self.rollback = FileRollback(self.session_id)
        self.blocked_count = 0
        self.use_sandbox = use_sandbox
        self.sandbox = SandboxPresets.standard() if use_sandbox else None
        
    def log_action(self, action_type, details, allowed=True):
        """Log an action to file"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'action_type': action_type,
            'details': details,
            'allowed': allowed
        }
        
        self.actions.append(entry)
        
        # Append to log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
            
        return entry
    
    def check_policy(self, action_type, target):
        """Check if action is allowed by policy"""
        should_block, reason = self.blocker.should_block(action_type, target)
        
        if should_block:
            self.blocked_count += 1
            console.print(f"[red]🚨 BLOCKED:[/red] {reason}")
            console.print(f"[dim]   Target: {target}[/dim]")
        
        return not should_block  # Return True if allowed
    
    def run(self):
        """Execute the command with monitoring"""
        console.print(f"\n[cyan]🐕 Starting monitored execution[/cyan]")
        console.print(f"[dim]Command: {self.command}[/dim]")
        console.print(f"[dim]Session: {self.session_id}[/dim]\n")
        
        # Log the start
        self.log_action('start', {
            'command': self.command,
            'cwd': os.getcwd(),
            'user': os.getenv('USER')
        })
        
        # Check command for dangerous patterns BEFORE execution
        console.print(f"[cyan]🔍 Checking command for dangerous patterns...[/cyan]")
        should_block, reason, patterns = self.blocker.check_command(self.command)
        
        if should_block:
            self.blocked_count += 1
            console.print(f"[red]🚨 BLOCKED:[/red] {reason}")
            console.print(f"[red]   Command: {self.command}[/red]")
            console.print(f"[red]   Matched patterns: {', '.join(patterns[:3])}[/red]\n")
            
            # Log the blocked command
            self.log_action('blocked', {
                'command': self.command,
                'reason': reason,
                'patterns': patterns
            }, allowed=False)
            
            self.log_action('complete', {
                'exit_code': 1,
                'total_actions': len(self.actions),
                'blocked_actions': self.blocked_count
            })
            
            return 1  # Exit with error code
        
        console.print(f"[green]✓[/green] Command passed safety checks\n")
        
        try:
            # Start the process (sandboxed or normal)
            if self.sandbox:
                self.process = self.sandbox.run_sandboxed(self.command)
            else:
                self.process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # Monitor the process
            psutil_process = psutil.Process(self.process.pid)
            
            console.print(f"[green]✓[/green] Process started (PID: {self.process.pid})")
            
            # Monitor file operations
            try:
                open_files = psutil_process.open_files()
                for f in open_files:
                    allowed = self.check_policy('file_read', f.path)
                    self.log_action('file_access', {
                        'path': f.path,
                        'mode': f.mode
                    }, allowed)
                    
                    if not allowed:
                        console.print(f"[red]⚠[/red]  Blocked file access: {f.path}")
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            
            # Wait for completion
            stdout, stderr = self.process.communicate()
            
            # Log output
            if stdout:
                console.print("\n[cyan]Output:[/cyan]")
                console.print(stdout)
            
            if stderr:
                console.print("\n[yellow]Errors:[/yellow]")
                console.print(stderr)
            
            # Log completion
            self.log_action('complete', {
                'exit_code': self.process.returncode,
                'total_actions': len(self.actions),
                'blocked_actions': self.blocked_count
            })
            
            console.print(f"\n[green]✓[/green] Process completed")
            console.print(f"[dim]Total actions: {len(self.actions)}[/dim]")
            console.print(f"[dim]Blocked actions: {self.blocked_count}[/dim]")
            console.print(f"[dim]Log file: {self.log_file}[/dim]\n")
            
            return self.process.returncode
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠[/yellow]  Interrupted by user")
            self.log_action('interrupted', {'reason': 'user_keyboard'})
            if self.process:
                self.process.terminate()
            return 130
            
        except Exception as e:
            console.print(f"\n[red]✗[/red] Error: {str(e)}")
            self.log_action('error', {'error': str(e)}, allowed=False)
            return 1

class AgentSession:
    """Manage active agent sessions"""
    
    @staticmethod
    def list_active():
        """List all active sessions"""
        sessions_file = Path.home() / '.sudodog' / 'sessions.json'
        
        if not sessions_file.exists():
            return []
        
        with open(sessions_file, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def add_session(session_id, command, pid):
        """Add a new session"""
        sessions_file = Path.home() / '.sudodog' / 'sessions.json'
        
        sessions = AgentSession.list_active()
        sessions.append({
            'session_id': session_id,
            'command': command,
            'pid': pid,
            'started': datetime.now().isoformat()
        })
        
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    @staticmethod
    def remove_session(session_id):
        """Remove a session"""
        sessions_file = Path.home() / '.sudodog' / 'sessions.json'
        
        sessions = AgentSession.list_active()
        sessions = [s for s in sessions if s['session_id'] != session_id]
        
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
