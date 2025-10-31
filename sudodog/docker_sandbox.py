"""
SudoDog - Docker-based Sandboxing
Provides strong isolation using Docker containers
"""

import docker
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import json
import uuid
from rich.console import Console

console = Console()

class DockerSandbox:
    """Docker-based sandbox for AI agents"""
    
    def __init__(self, 
                 session_id: str,
                 image: str = 'python:3.11-slim',
                 network_enabled: bool = True,
                 allowed_domains: List[str] = None,
                 cpu_limit: float = None,
                 memory_limit: str = None):
        """
        Initialize Docker sandbox
        
        Args:
            session_id: Unique session identifier
            image: Docker image to use (default: python:3.11-slim)
            network_enabled: Allow network access
            allowed_domains: List of allowed domains (if network enabled)
            cpu_limit: CPU limit in cores (e.g., 2.0 = 2 cores, None = no limit)
            memory_limit: Memory limit (e.g., "512m", "1g", None = no limit)
        """
        self.session_id = session_id
        self.image = image
        self.network_enabled = network_enabled
        self.allowed_domains = allowed_domains or []
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            raise RuntimeError(f"Docker is not running or not accessible: {e}")
        
        self.container = None
        self.container_id = None
        
    def create_container(self, command: str, working_dir: str = "/workspace") -> str:
        """
        Create and configure Docker container
        
        Args:
            command: Command to run in container
            working_dir: Working directory inside container
            
        Returns:
            Container ID
        """
        console.print(f"[cyan]🐳 Creating Docker container...[/cyan]")
        
        # Show image info
        if self.image != 'python:3.11-slim':
            console.print(f"[dim]   Image: {self.image}[/dim]")
        
        # Network configuration
        if self.network_enabled:
            network_mode = "bridge"
            console.print(f"[dim]   Network: enabled[/dim]")
        else:
            network_mode = "none"
            console.print(f"[dim]   Network: isolated[/dim]")
        
        # Resource limits
        if self.cpu_limit:
            console.print(f"[dim]   CPU limit: {self.cpu_limit} cores[/dim]")
        if self.memory_limit:
            console.print(f"[dim]   Memory limit: {self.memory_limit}[/dim]")
        
        # Container configuration
        container_config = {
            'image': self.image,
            'command': ['sh', '-c', command],
            'working_dir': working_dir,
            'detach': True,
            'network_mode': network_mode,
            'read_only': False,  # Allow writes to temp directories
            'security_opt': ['no-new-privileges'],  # Security hardening
            'cap_drop': ['ALL'],  # Drop all capabilities
            'cap_add': ['NET_BIND_SERVICE'] if self.network_enabled else [],
            'labels': {
                'sudodog.session_id': self.session_id,
                'sudodog.managed': 'true',
                'sudodog.image': self.image
            },
            # Mount working directory
            'volumes': {
                str(Path.cwd()): {'bind': working_dir, 'mode': 'rw'}
            },
            # Environment variables
            'environment': {
                'SUDODOG_SESSION': self.session_id,
                'PYTHONUNBUFFERED': '1'
            }
        }
        
        # Add resource limits if specified
        if self.memory_limit:
            container_config['mem_limit'] = self.memory_limit
        
        if self.cpu_limit:
            container_config['cpu_quota'] = int(self.cpu_limit * 100000)
            container_config['cpu_period'] = 100000
        
        try:
            # Ensure image exists
            try:
                self.client.images.get(self.image)
            except docker.errors.ImageNotFound:
                console.print(f"[yellow]⚠[/yellow]  Pulling image: {self.image} (this may take a moment)...")
                try:
                    self.client.images.pull(self.image)
                    console.print(f"[green]✓[/green] Image pulled successfully")
                except docker.errors.APIError as e:
                    console.print(f"[red]✗[/red] Failed to pull image: {e}")
                    console.print(f"[yellow]Tip:[/yellow] Make sure the image exists: docker pull {self.image}")
                    raise
            
            # Create container
            self.container = self.client.containers.create(**container_config)
            self.container_id = self.container.id[:12]
            
            console.print(f"[green]✓[/green] Container created: {self.container_id}")
            
            return self.container_id
            
        except docker.errors.APIError as e:
            console.print(f"[red]✗[/red] Failed to create container: {e}")
            raise
    
    def start(self) -> None:
        """Start the container"""
        if not self.container:
            raise RuntimeError("Container not created yet")
        
        console.print(f"[cyan]▶[/cyan]  Starting container {self.container_id}...")
        self.container.start()
        console.print(f"[green]✓[/green] Container running")
    
    def wait(self, timeout: Optional[int] = None) -> Dict:
        """
        Wait for container to complete
        
        Args:
            timeout: Timeout in seconds (None = wait forever)
            
        Returns:
            Dict with exit_code, stdout, stderr
        """
        if not self.container:
            raise RuntimeError("Container not started yet")
        
        try:
            # Wait for completion
            result = self.container.wait(timeout=timeout)
            exit_code = result['StatusCode']
            
            # Get logs
            logs = self.container.logs(stdout=True, stderr=True).decode('utf-8')
            
            return {
                'exit_code': exit_code,
                'output': logs,
                'container_id': self.container_id
            }
            
        except Exception as e:
            console.print(f"[red]✗[/red] Error waiting for container: {e}")
            return {
                'exit_code': -1,
                'output': str(e),
                'container_id': self.container_id
            }
    
    def stop(self, timeout: int = 10) -> None:
        """Stop the container"""
        if self.container:
            console.print(f"[yellow]⏹[/yellow]  Stopping container {self.container_id}...")
            try:
                self.container.stop(timeout=timeout)
                console.print(f"[green]✓[/green] Container stopped")
            except Exception as e:
                console.print(f"[red]✗[/red] Error stopping container: {e}")
    
    def cleanup(self) -> None:
        """Remove the container"""
        if self.container:
            console.print(f"[dim]🗑[/dim]  Cleaning up container {self.container_id}...")
            try:
                self.container.remove(force=True)
                console.print(f"[green]✓[/green] Container removed")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow]  Cleanup warning: {e}")
    
    def get_stats(self) -> Dict:
        """Get container resource usage stats"""
        if not self.container:
            return {}
        
        try:
            stats = self.container.stats(stream=False)
            
            # Calculate CPU usage percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Memory usage
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
            
            return {
                'cpu_percent': round(cpu_percent, 2),
                'memory_usage_mb': round(memory_usage / (1024 * 1024), 2),
                'memory_percent': round(memory_percent, 2),
                'container_id': self.container_id
            }
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow]  Could not get stats: {e}")
            return {}
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        self.stop()
        self.cleanup()


class DockerSandboxManager:
    """Manage multiple Docker sandbox instances"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            raise RuntimeError(f"Docker is not running: {e}")
    
    def list_active_containers(self) -> List[Dict]:
        """List all SudoDog-managed containers"""
        containers = self.client.containers.list(
            filters={'label': 'sudodog.managed=true'}
        )
        
        return [{
            'container_id': c.id[:12],
            'session_id': c.labels.get('sudodog.session_id'),
            'image': c.labels.get('sudodog.image', 'unknown'),
            'status': c.status,
            'created': c.attrs['Created']
        } for c in containers]
    
    def stop_all(self) -> int:
        """Stop all SudoDog containers"""
        containers = self.client.containers.list(
            filters={'label': 'sudodog.managed=true'}
        )
        
        count = 0
        for container in containers:
            try:
                container.stop(timeout=10)
                container.remove(force=True)
                count += 1
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow]  Failed to stop {container.id[:12]}: {e}")
        
        return count
    
    def cleanup_old_containers(self, max_age_hours: int = 24) -> int:
        """Remove stopped containers older than max_age_hours"""
        containers = self.client.containers.list(
            all=True,
            filters={'label': 'sudodog.managed=true', 'status': 'exited'}
        )
        
        count = 0
        for container in containers:
            try:
                container.remove()
                count += 1
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow]  Failed to cleanup {container.id[:12]}: {e}")
        
        return count
