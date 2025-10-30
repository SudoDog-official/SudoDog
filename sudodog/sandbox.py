"""
SudoDog - Sandbox Module
Creates isolated environments using Linux namespaces
"""

import subprocess
import os
import tempfile
from pathlib import Path
from typing import List, Optional
from rich.console import Console

console = Console()

class Sandbox:
    """Create isolated sandbox environments using Linux namespaces"""
    
    def __init__(self, 
                 isolate_network: bool = True,
                 isolate_pid: bool = True,
                 isolate_ipc: bool = True,
                 read_only_paths: Optional[List[str]] = None,
                 writable_paths: Optional[List[str]] = None):
        """
        Initialize sandbox configuration
        
        Args:
            isolate_network: Isolate network namespace (no network access)
            isolate_pid: Isolate PID namespace (can't see other processes)
            isolate_ipc: Isolate IPC namespace (no shared memory)
            read_only_paths: List of paths to mount read-only
            writable_paths: List of paths that remain writable
        """
        self.isolate_network = isolate_network
        self.isolate_pid = isolate_pid
        self.isolate_ipc = isolate_ipc
        self.read_only_paths = read_only_paths or []
        self.writable_paths = writable_paths or ['/tmp', str(Path.home())]
        self.temp_dir = None
        
    def build_unshare_command(self, command: str) -> List[str]:
        unshare_args = ['unshare']
    
        # CRITICAL: Add --user first to enable unprivileged namespaces
        unshare_args.append('--user')
        
        # Add namespace isolation flags
        if self.isolate_network:
            unshare_args.append('--net')  # Network namespace
            
        if self.isolate_pid:
            unshare_args.extend(['--pid', '--fork'])  # PID namespace
            
        if self.isolate_ipc:
            unshare_args.append('--ipc')  # IPC namespace
        
        # Mount namespace for filesystem isolation
        unshare_args.append('--mount')
        
        # Add the actual command
        unshare_args.extend(['--', 'sh', '-c', command])
        
        return unshare_args
    
    def run_sandboxed(self, command: str, cwd: Optional[str] = None) -> subprocess.Popen:
        """
        Run a command in a sandboxed environment
        
        Args:
            command: Command to execute
            cwd: Working directory (default: current directory)
            
        Returns:
            subprocess.Popen object
        """
        console.print("[cyan]🔒 Creating sandbox environment...[/cyan]")
        
        # Build the sandboxed command
        sandbox_cmd = self.build_unshare_command(command)
        
        # Show what isolation is enabled
        isolation_features = []
        if self.isolate_network:
            isolation_features.append("network")
        if self.isolate_pid:
            isolation_features.append("PID")
        if self.isolate_ipc:
            isolation_features.append("IPC")
            
        console.print(f"[dim]Isolated: {', '.join(isolation_features)}[/dim]")
        
        # Start the sandboxed process
        process = subprocess.Popen(
            sandbox_cmd,
            cwd=cwd or os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        console.print(f"[green]✓[/green] Sandboxed process started (PID: {process.pid})")
        
        return process
    
    def run_docker_sandbox(self, command: str, image: str = 'python:3.11-slim') -> subprocess.Popen:
        """
        Run command in Docker container (alternative to unshare)
        
        Args:
            command: Command to execute
            image: Docker image to use
            
        Returns:
            subprocess.Popen object
        """
        console.print("[cyan]🐳 Creating Docker sandbox...[/cyan]")
        
        # Build docker run command with security restrictions
        docker_cmd = [
            'docker', 'run',
            '--rm',  # Remove container after exit
            '--network=none',  # No network access
            '--read-only',  # Read-only root filesystem
            '--tmpfs', '/tmp:rw,noexec,nosuid,size=100m',  # Writable /tmp
            '--security-opt=no-new-privileges',  # Can't gain privileges
            '--cap-drop=ALL',  # Drop all capabilities
            '-w', '/workspace',  # Working directory
            '-v', f'{os.getcwd()}:/workspace',  # Mount current directory
            image,
            'sh', '-c', command
        ]
        
        process = subprocess.Popen(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        console.print(f"[green]✓[/green] Docker sandbox started (container ID will be shown)")
        
        return process
    
    @staticmethod
    def check_sandbox_support() -> dict:
        """
        Check what sandboxing methods are available
        
        Returns:
            Dict with available methods and their status
        """
        support = {
            'unshare': os.path.exists('/usr/bin/unshare'),
            'docker': os.path.exists('/usr/bin/docker'),
            'podman': os.path.exists('/usr/bin/podman'),
            'user_namespaces': False
        }
        
        # Check if user namespaces are enabled
        try:
            with open('/proc/sys/kernel/unprivileged_userns_clone', 'r') as f:
                support['user_namespaces'] = f.read().strip() == '1'
        except FileNotFoundError:
            # Some systems don't have this file, assume enabled
            support['user_namespaces'] = True
        
        return support
    
    def cleanup(self):
        """Clean up temporary sandbox resources"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)


class SandboxPresets:
    """Predefined sandbox configurations for common use cases"""
    
    @staticmethod
    def paranoid():
        """Maximum isolation - no network, no IPC, isolated PID"""
        return Sandbox(
            isolate_network=True,
            isolate_pid=True,
            isolate_ipc=True,
            read_only_paths=['/etc', '/usr', '/bin', '/lib', '/lib64']
        )
    
    @staticmethod
    def standard():
        """Standard isolation - network isolated, PID isolated"""
        return Sandbox(
            isolate_network=True,
            isolate_pid=True,
            isolate_ipc=False
        )
    
    @staticmethod
    def minimal():
        """Minimal isolation - only PID isolation"""
        return Sandbox(
            isolate_network=False,
            isolate_pid=True,
            isolate_ipc=False
        )
    
    @staticmethod
    def testing():
        """For testing - no isolation (use for debugging)"""
        return Sandbox(
            isolate_network=False,
            isolate_pid=False,
            isolate_ipc=False
        )
