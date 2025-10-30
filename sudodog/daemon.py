"""
SudoDog - Background Daemon
Monitors Docker containers and provides real-time alerts
"""

import os
import sys
import time
import signal
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import docker
from rich.console import Console

console = Console()

class SudoDogDaemon:
    """Background daemon for monitoring AI agents"""
    
    def __init__(self, check_interval: int = 5):
        """
        Initialize daemon
        
        Args:
            check_interval: How often to check containers (seconds)
        """
        self.check_interval = check_interval
        self.running = False
        self.state_file = Path.home() / '.sudodog' / 'daemon.json'
        self.pid_file = Path.home() / '.sudodog' / 'daemon.pid'
        
        try:
            self.docker_client = docker.from_env()
        except docker.errors.DockerException as e:
            raise RuntimeError(f"Docker is not accessible: {e}")
        
        # Alert thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'max_containers': 10
        }
    
    def write_pid(self) -> None:
        """Write daemon PID to file"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    def remove_pid(self) -> None:
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def is_running(self) -> bool:
        """Check if daemon is already running"""
        if not self.pid_file.exists():
            return False
        
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            os.kill(pid, 0)  # Check if process exists
            return True
        except OSError:
            # Process doesn't exist, remove stale PID file
            self.remove_pid()
            return False
    
    def save_state(self, state: Dict) -> None:
        """Save daemon state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self) -> Dict:
        """Load daemon state"""
        if not self.state_file.exists():
            return {}
        
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def get_container_stats(self, container) -> Dict:
        """Get resource usage for a container"""
        try:
            stats = container.stats(stream=False)
            
            # CPU usage
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
                'memory_limit_mb': round(memory_limit / (1024 * 1024), 2),
                'memory_percent': round(memory_percent, 2)
            }
        except Exception as e:
            return {}
    
    def check_thresholds(self, container_id: str, stats: Dict) -> List[str]:
        """Check if any thresholds are exceeded"""
        alerts = []
        
        if stats.get('cpu_percent', 0) > self.thresholds['cpu_percent']:
            alerts.append(f"HIGH CPU: {stats['cpu_percent']}% (threshold: {self.thresholds['cpu_percent']}%)")
        
        if stats.get('memory_percent', 0) > self.thresholds['memory_percent']:
            alerts.append(f"HIGH MEMORY: {stats['memory_percent']}% (threshold: {self.thresholds['memory_percent']}%)")
        
        return alerts
    
    def log_alert(self, container_id: str, session_id: str, alerts: List[str]) -> None:
        """Log alerts to file"""
        alert_file = Path.home() / '.sudodog' / 'alerts.jsonl'
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'container_id': container_id,
            'session_id': session_id,
            'alerts': alerts
        }
        
        with open(alert_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Also print to console if running in foreground
        for alert in alerts:
            console.print(f"[red]🚨 ALERT[/red] [{session_id}] {alert}")
    
    def monitor_loop(self) -> None:
        """Main monitoring loop"""
        console.print(f"[green]✓[/green] SudoDog daemon started (PID: {os.getpid()})")
        console.print(f"[dim]Monitoring interval: {self.check_interval}s[/dim]")
        console.print(f"[dim]State file: {self.state_file}[/dim]\n")
        
        while self.running:
            try:
                # Get all SudoDog containers
                containers = self.docker_client.containers.list(
                    filters={'label': 'sudodog.managed=true'}
                )
                
                # Update state
                state = {
                    'last_check': datetime.now().isoformat(),
                    'active_containers': len(containers),
                    'containers': []
                }
                
                # Check each container
                for container in containers:
                    container_id = container.id[:12]
                    session_id = container.labels.get('sudodog.session_id', 'unknown')
                    
                    # Get stats
                    stats = self.get_container_stats(container)
                    
                    # Check thresholds
                    alerts = self.check_thresholds(container_id, stats)
                    
                    if alerts:
                        self.log_alert(container_id, session_id, alerts)
                    
                    # Add to state
                    state['containers'].append({
                        'container_id': container_id,
                        'session_id': session_id,
                        'status': container.status,
                        'stats': stats,
                        'alerts': len(alerts)
                    })
                
                # Check max containers threshold
                if len(containers) > self.thresholds['max_containers']:
                    console.print(f"[yellow]⚠[/yellow]  Too many containers: {len(containers)} (max: {self.thresholds['max_containers']})")
                
                # Save state
                self.save_state(state)
                
                # Sleep
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠[/yellow]  Daemon interrupted")
                break
            except Exception as e:
                console.print(f"[red]✗[/red] Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def start(self, foreground: bool = False) -> None:
        """Start the daemon"""
        if self.is_running():
            console.print("[yellow]⚠[/yellow]  Daemon is already running")
            return
        
        self.running = True
        self.write_pid()
        
        if foreground:
            # Run in foreground
            try:
                self.monitor_loop()
            finally:
                self.stop()
        else:
            # Fork to background (Unix only)
            if os.name != 'posix':
                console.print("[red]✗[/red] Background mode only supported on Unix systems")
                console.print("[dim]Use 'sudodog daemon start --foreground' instead[/dim]")
                return
            
            # Double fork to daemonize
            try:
                pid = os.fork()
                if pid > 0:
                    # Parent process
                    console.print(f"[green]✓[/green] Daemon started in background (PID: {pid})")
                    return
            except OSError as e:
                console.print(f"[red]✗[/red] Fork failed: {e}")
                return
            
            # First child
            os.setsid()
            
            try:
                pid = os.fork()
                if pid > 0:
                    # Exit first child
                    sys.exit(0)
            except OSError as e:
                console.print(f"[red]✗[/red] Fork failed: {e}")
                sys.exit(1)
            
            # Second child (daemon)
            os.chdir('/')
            os.umask(0)
            
            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            
            # Run monitoring loop
            try:
                self.monitor_loop()
            finally:
                self.remove_pid()
    
    def stop(self) -> None:
        """Stop the daemon"""
        if not self.is_running():
            console.print("[yellow]⚠[/yellow]  Daemon is not running")
            return
        
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            os.kill(pid, signal.SIGTERM)
            console.print(f"[green]✓[/green] Daemon stopped (PID: {pid})")
            self.remove_pid()
        except OSError as e:
            console.print(f"[red]✗[/red] Failed to stop daemon: {e}")
    
    def status(self) -> Dict:
        """Get daemon status"""
        if not self.is_running():
            return {
                'running': False,
                'message': 'Daemon is not running'
            }
        
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        state = self.load_state()
        
        return {
            'running': True,
            'pid': pid,
            'state': state
        }
