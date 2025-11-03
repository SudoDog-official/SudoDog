#!/usr/bin/env python3
"""
SudoDog - Security for AI Agents
CLI Interface (with Docker + Daemon support)
"""

import click
import sys
from rich.console import Console
from rich.table import Table
from rich import box
from pathlib import Path
import json
from datetime import datetime
import platform

console = Console()

@click.group()
@click.version_option(version='0.2.0')
def cli():
    """🐕 SudoDog - Sandboxing and monitoring for AI agents in one command"""
    pass

@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('command', nargs=-1, required=True, type=click.UNPROCESSED)
@click.option('--policy', '-p', default='default', help='Security policy to use')
@click.option('--log-level', '-l', default='info', help='Logging level')
@click.option('--docker', is_flag=True, help='Use Docker sandbox (stronger isolation)')
@click.option('--image', default='python:3.11-slim', help='Docker image to use (requires --docker)')
@click.option('--cpu-limit', type=float, default=None, help='CPU limit in cores (e.g., 2.0)')
@click.option('--memory-limit', default=None, help='Memory limit (e.g., 512m, 1g)')
def run(command, policy, log_level, docker, image, cpu_limit, memory_limit):
    """Run an AI agent with SudoDog protection
    
    Examples:
        sudodog run python agent.py
        sudodog run --docker python agent.py
        sudodog run --docker --image my-agent:latest python agent.py
        sudodog run --docker --cpu-limit 2.0 --memory-limit 1g python agent.py
    """
    from .monitor import AgentMonitor, AgentSession
    from .telemetry import get_telemetry
    from .platform_telemetry import send_platform_telemetry
    from .sudodog_telemetry import LocalTelemetry
    
    # Track command usage (local telemetry)
    telemetry = get_telemetry()
    telemetry.track_command('run', {
        'docker': docker,
        'custom_image': image != 'python:3.11-slim',
        'has_cpu_limit': cpu_limit is not None,
        'has_memory_limit': memory_limit is not None,
    })
    
    # Track in local SQLite telemetry
    local_telemetry = LocalTelemetry()
    local_telemetry.track_event('sudodog_run', {
        'docker': docker,
        'custom_image': image != 'python:3.11-slim',
        'has_cpu_limit': cpu_limit is not None,
        'has_memory_limit': memory_limit is not None,
        'version': '0.2.0',
        'platform': platform.system(),
    })
    
    # Track first run (one-time)
    first_run_path = Path.home() / ".sudodog" / ".first_run_tracked"
    if not first_run_path.exists():
        local_telemetry.track_event('first_run', {
            'docker': docker,
            'platform': platform.system(),
            'version': '0.2.0',
        })
        first_run_path.parent.mkdir(parents=True, exist_ok=True)
        first_run_path.touch()
    
    console.print("\n[cyan]🐕 SudoDog AI Agent Security[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]")
    
    # Convert command tuple to string
    cmd_string = ' '.join(command)
    
    # Track execution start
    start_time = datetime.now()
    
    if docker:
        console.print(f"[cyan]🐳 Using Docker sandbox[/cyan]")
        from .docker_sandbox import DockerSandbox
        
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            with DockerSandbox(
                session_id, 
                image=image,
                cpu_limit=cpu_limit, 
                memory_limit=memory_limit
            ) as sandbox:
                # Create and start container
                sandbox.create_container(cmd_string)
                sandbox.start()
                
                # Wait for completion
                result = sandbox.wait(timeout=300)  # 5 minute timeout
                
                console.print(f"\n{result['output']}")
                console.print(f"\n[green]✓[/green] Container exited with code {result['exit_code']}")
                
                # Get final stats
                stats = sandbox.get_stats()
                if stats:
                    console.print(f"[dim]CPU: {stats['cpu_percent']}% | Memory: {stats['memory_usage_mb']}MB[/dim]\n")
                    
                    # Send telemetry to platform
                    send_platform_telemetry(
                        event_type='agent_execution',
                        data={
                            'cpu_usage': stats['cpu_percent'],
                            'memory_usage': stats['memory_usage_mb'],
                            'api_calls': 0,  # Docker doesn't track this yet
                            'duration': (datetime.now() - start_time).total_seconds(),
                            'agent_name': 'docker_agent',
                            'task_type': 'docker_execution',
                            'exit_code': result['exit_code']
                        }
                    )
                
                sys.exit(result['exit_code'])
        except Exception as e:
            # Track error
            telemetry.track_error(type(e).__name__, str(e))
            local_telemetry.track_event('error', {
                'error_type': type(e).__name__,
                'command': 'run',
                'docker': docker,
            })
            console.print(f"\n[red]✗[/red] Docker error: {e}\n")
            sys.exit(1)
    else:
        # Original namespace-based execution
        console.print(f"[green]✓[/green] Sandboxed environment created")
        console.print(f"[green]✓[/green] Behavioral monitoring active")
        console.print(f"[dim]Policy: {policy}[/dim]")
        
        # Run with monitoring
        monitor = AgentMonitor(cmd_string, policy=policy)
        
        # Add to active sessions
        AgentSession.add_session(monitor.session_id, cmd_string, 0)
        
        try:
            exit_code = monitor.run()
            
            # Send telemetry to platform after execution
            duration = (datetime.now() - start_time).total_seconds()
            send_platform_telemetry(
                event_type='agent_execution',
                data={
                    'cpu_usage': 0,  # Namespace sandbox doesn't track CPU yet
                    'memory_usage': 0,  # Add tracking later
                    'api_calls': 0,  # Add tracking later
                    'duration': duration,
                    'agent_name': 'namespace_agent',
                    'task_type': 'namespace_execution',
                    'exit_code': exit_code
                }
            )
        except Exception as e:
            # Track error
            telemetry.track_error(type(e).__name__, str(e))
            local_telemetry.track_event('error', {
                'error_type': type(e).__name__,
                'command': 'run',
                'docker': False,
            })
            raise
        finally:
            # Remove from active sessions
            AgentSession.remove_session(monitor.session_id)
        
        sys.exit(exit_code)

@cli.command()
def init():
    """Initialize SudoDog in current directory"""
    from .telemetry_ui import show_telemetry_prompt
    from .telemetry import get_telemetry
    from .sudodog_telemetry import LocalTelemetry
    
    console.print("\n[cyan]🐕 SudoDog Initialization[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
    
    # Create config directory
    config_dir = Path.home() / '.sudodog'
    is_first_time = not config_dir.exists()
    config_dir.mkdir(exist_ok=True)
    
    # Create default config
    config = {
        'version': '0.2.0',
        'created': datetime.now().isoformat(),
        'policies': {
            'default': {
                'block_patterns': [
                    '/etc/shadow',
                    '/etc/passwd',
                    '*.env',
                    'DROP TABLE',
                    'DELETE FROM'
                ],
                'allow_network': True,
                'max_file_writes': 100
            }
        }
    }
    
    config_file = config_dir / 'config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Create logs directory
    logs_dir = config_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Create backups directory
    backups_dir = config_dir / 'backups'
    backups_dir.mkdir(exist_ok=True)
    
    # Create sessions file
    sessions_file = config_dir / 'sessions.json'
    if not sessions_file.exists():
        with open(sessions_file, 'w') as f:
            json.dump([], f)
    
    console.print(f"[green]✓[/green] Config directory: {config_dir}")
    console.print(f"[green]✓[/green] Logs directory: {logs_dir}")
    console.print(f"[green]✓[/green] Backups directory: {backups_dir}")
    console.print(f"[green]✓[/green] Default policy created")
    console.print("\n[green]SudoDog initialized![/green]")
    
    # Track first-time initialization in local telemetry
    if is_first_time:
        local_telemetry = LocalTelemetry()
        local_telemetry.track_event('first_time_init', {
            'version': '0.2.0',
            'platform': platform.system(),
            'platform_version': platform.release(),
            'python_version': platform.python_version(),
        })
    
    # Show telemetry opt-in prompt
    console.print()
    response = show_telemetry_prompt()
    
    if response:
        telemetry = get_telemetry()
        telemetry.enable()
        telemetry.track_install()
    
    console.print("\n[green]Ready to use! Run 'sudodog run <command>' to start.[/green]\n")

@cli.command()
def status():
    """Show status of running agents"""
    from .monitor import AgentSession
    
    console.print("\n[cyan]🤖 Agent Status[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
    
    sessions = AgentSession.list_active()
    
    if not sessions:
        console.print("[yellow]No active agents[/yellow]")
        console.print("[dim]Run 'sudodog run <command>' to start an agent[/dim]\n")
        return
    
    table = Table(box=box.ROUNDED)
    table.add_column("Session ID", style="cyan")
    table.add_column("Command", style="white")
    table.add_column("Started", style="dim")
    
    for session in sessions:
        started = datetime.fromisoformat(session['started']).strftime('%Y-%m-%d %H:%M:%S')
        table.add_row(
            session['session_id'],
            session['command'][:50] + "..." if len(session['command']) > 50 else session['command'],
            started
        )
    
    console.print(table)
    console.print()

@cli.command()
@click.option('--last', '-n', default=10, help='Number of recent actions to show')
@click.option('--session', '-s', help='Show logs for specific session')
def logs(last, session):
    """View agent activity logs"""
    from .sudodog_telemetry import LocalTelemetry
    
    # Track logs viewed
    local_telemetry = LocalTelemetry()
    local_telemetry.track_event('logs_viewed', {
        'session_specific': session is not None,
        'limit': last,
    })
    
    console.print("\n[cyan]📋 Recent Agent Activity[/cyan]")
    console.print("[cyan]" + "─" * 40 + "[/cyan]\n")
    
    logs_dir = Path.home() / '.sudodog' / 'logs'
    
    if not logs_dir.exists():
        console.print("[yellow]No logs found. Run 'sudodog init' first.[/yellow]\n")
        return
    
    # Get log files
    if session:
        log_files = [logs_dir / f'{session}.jsonl']
        if not log_files[0].exists():
            console.print(f"[red]No logs found for session {session}[/red]\n")
            return
    else:
        log_files = sorted(logs_dir.glob('*.jsonl'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not log_files:
        console.print("[yellow]No logged activities yet[/yellow]\n")
        return
    
    console.print(f"[dim]Showing last {last} actions from recent sessions...[/dim]\n")
    
    total_shown = 0
    for log_file in log_files:
        if total_shown >= last:
            break
            
        with open(log_file, 'r') as f:
            for line in f:
                if total_shown >= last:
                    break
                    
                try:
                    entry = json.loads(line.strip())
                    timestamp = entry.get('timestamp', 'Unknown')
                    action_type = entry.get('action_type', 'unknown')
                    details = entry.get('details', {})
                    
                    # Format timestamp
                    if timestamp != 'Unknown':
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M:%S')
                    else:
                        time_str = 'Unknown'
                    
                    # Display based on action type
                    if action_type == 'start':
                        console.print(f"[green]✓[/green] [{time_str}] Started: {details.get('command', 'Unknown')}")
                    elif action_type == 'complete':
                        console.print(f"[green]✓[/green] [{time_str}] Completed - {details.get('total_actions', 0)} actions, {details.get('blocked_actions', 0)} blocked")
                    elif action_type == 'file_access':
                        console.print(f"[blue]📁[/blue] [{time_str}] File: {details.get('path', 'Unknown')} ({details.get('mode', 'Unknown')})")
                    elif action_type == 'blocked':
                        console.print(f"[red]🚨[/red] [{time_str}] BLOCKED: {details.get('reason', 'Unknown')}")
                    else:
                        console.print(f"[dim]  [{time_str}] {action_type}: {details}[/dim]")
                    
                    total_shown += 1
                except json.JSONDecodeError:
                    continue
    
    if total_shown == 0:
        console.print("[yellow]No logged activities yet[/yellow]\n")
    else:
        console.print(f"\n[dim]Showing {total_shown} most recent actions[/dim]")
        console.print(f"[dim]Log files: {logs_dir}[/dim]\n")

@cli.command()
@click.argument('session_id')
@click.option('--steps', '-n', default=None, type=int, help='Number of actions to rollback (default: all)')
def rollback(session_id, steps):
    """Rollback agent actions"""
    from .blocker import FileRollback
    from .telemetry import get_telemetry
    from .sudodog_telemetry import LocalTelemetry
    
    console.print("\n[yellow]⏪[/yellow]  Rolling back actions...")
    console.print(f"[dim]Session: {session_id}[/dim]\n")
    
    # Check if backup directory exists
    backup_dir = Path.home() / '.sudodog' / 'backups' / session_id
    
    if not backup_dir.exists():
        console.print(f"[red]✗[/red] No backups found for session {session_id}")
        console.print("[dim]Rollback requires file backups to exist[/dim]\n")
        return
    
    # Perform rollback
    rollback_handler = FileRollback(session_id)
    
    try:
        rolled_back, errors = rollback_handler.rollback(steps)
        
        # Track rollback
        telemetry = get_telemetry()
        telemetry.track_command('rollback', {
            'rollback': True,
            'steps': rolled_back,
        })
        
        # Track in local telemetry
        local_telemetry = LocalTelemetry()
        local_telemetry.track_event('rollback_used', {
            'steps': rolled_back,
            'version': '0.2.0',
            'session_id_length': len(session_id),
        })
        
        if rolled_back > 0:
            console.print(f"[green]✓[/green] Successfully rolled back {rolled_back} file operation(s)")
        else:
            console.print("[yellow]No operations to rollback[/yellow]")
        
        if errors:
            console.print(f"\n[red]Errors occurred:[/red]")
            for error in errors:
                console.print(f"[red]  • {error}[/red]")
        
        console.print()
        
    except Exception as e:
        telemetry = get_telemetry()
        telemetry.track_error(type(e).__name__, str(e))
        
        local_telemetry = LocalTelemetry()
        local_telemetry.track_event('error', {
            'error_type': type(e).__name__,
            'command': 'rollback',
        })
        
        console.print(f"[red]✗[/red] Rollback failed: {str(e)}\n")

@cli.command()
@click.argument('session_id', required=False)
def pause(session_id):
    """Pause a running agent"""
    console.print("\n[yellow]⏸[/yellow]  Feature coming soon...")
    console.print("[dim]Pause/resume requires process signal handling[/dim]\n")

@cli.command()
def policies():
    """List available security policies"""
    console.print("\n[cyan]🛡️  Security Policies[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
    
    config_file = Path.home() / '.sudodog' / 'config.json'
    
    if not config_file.exists():
        console.print("[yellow]No policies found. Run 'sudodog init' first.[/yellow]\n")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    table = Table(box=box.ROUNDED)
    table.add_column("Policy", style="cyan")
    table.add_column("Description", style="white")
    
    for policy_name, policy_config in config.get('policies', {}).items():
        blocked = len(policy_config.get('block_patterns', []))
        table.add_row(
            policy_name,
            f"Blocks {blocked} patterns"
        )
    
    console.print(table)
    console.print()

@cli.group()
def daemon():
    """Manage SudoDog background daemon"""
    pass

@daemon.command('start')
@click.option('--foreground', '-f', is_flag=True, help='Run in foreground (don\'t daemonize)')
@click.option('--interval', '-i', default=5, help='Check interval in seconds')
def daemon_start(foreground, interval):
    """Start the monitoring daemon"""
    from .sudodog_telemetry import LocalTelemetry
    
    try:
        from .daemon import SudoDogDaemon
        
        # Track daemon start
        local_telemetry = LocalTelemetry()
        local_telemetry.track_event('daemon_started', {
            'version': '0.2.0',
            'foreground': foreground,
            'interval': interval,
        })
        
        d = SudoDogDaemon(check_interval=interval)
        d.start(foreground=foreground)
    except ImportError:
        console.print("[red]✗[/red] Daemon module not found")
        console.print("[dim]Run the setup script to install daemon support[/dim]\n")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to start daemon: {e}\n")

@daemon.command('stop')
def daemon_stop():
    """Stop the monitoring daemon"""
    try:
        from .daemon import SudoDogDaemon
        
        d = SudoDogDaemon()
        d.stop()
    except ImportError:
        console.print("[red]✗[/red] Daemon module not found\n")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to stop daemon: {e}\n")

@daemon.command('status')
def daemon_status():
    """Show daemon status"""
    try:
        from .daemon import SudoDogDaemon
        
        d = SudoDogDaemon()
        status = d.status()
        
        if not status['running']:
            console.print(f"\n[yellow]⚠[/yellow]  {status['message']}\n")
            return
        
        console.print(f"\n[green]✓[/green] Daemon is running (PID: {status['pid']})")
        
        state = status.get('state', {})
        if state:
            console.print(f"[dim]Last check: {state.get('last_check', 'Unknown')}[/dim]")
            console.print(f"[dim]Active containers: {state.get('active_containers', 0)}[/dim]\n")
            
            if state.get('containers'):
                table = Table(box=box.ROUNDED)
                table.add_column("Container", style="cyan")
                table.add_column("Session", style="white")
                table.add_column("CPU%", style="yellow")
                table.add_column("Memory%", style="yellow")
                table.add_column("Alerts", style="red")
                
                for c in state['containers']:
                    stats = c.get('stats', {})
                    table.add_row(
                        c['container_id'],
                        c['session_id'][:16],
                        str(stats.get('cpu_percent', 'N/A')),
                        str(stats.get('memory_percent', 'N/A')),
                        str(c.get('alerts', 0))
                    )
                
                console.print(table)
        console.print()
    except ImportError:
        console.print("\n[red]✗[/red] Daemon module not found\n")
    except Exception as e:
        console.print(f"\n[red]✗[/red] Error getting daemon status: {e}\n")

@cli.command()
def version():
    """Show SudoDog version"""
    console.print("\n[cyan]🐕 SudoDog v0.2.0[/cyan]")
    console.print("[dim]Security for AI agents that actually works[/dim]\n")

@cli.command(hidden=True)
def stats():
    """View local telemetry statistics (admin only)"""
    from .sudodog_telemetry import LocalTelemetry
    
    telemetry = LocalTelemetry()
    
    if not telemetry.is_enabled():
        console.print("\n[yellow]⚠️  Local telemetry is currently DISABLED (opted out)[/yellow]")
        console.print("No stats are being collected.")
        console.print("\nTo re-enable: sudodog local-telemetry enable\n")
        return
    
    telemetry.print_stats()

@cli.group(name='local-telemetry')
def local_telemetry():
    """Manage local usage statistics (opt-out available)"""
    pass

@local_telemetry.command('status')
def local_telemetry_status():
    """Check local telemetry status"""
    from .sudodog_telemetry import LocalTelemetry
    
    t = LocalTelemetry()
    
    console.print("\n[cyan]📊 Local Usage Statistics[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
    
    if t.is_enabled():
        console.print("[green]✓[/green] Local telemetry is ENABLED (collecting usage stats)")
        console.print("\n[dim]What's collected:[/dim]")
        console.print("  • Installation count")
        console.print("  • Feature usage (Docker, daemon, etc.)")
        console.print("  • Anonymous usage patterns")
        console.print("\n[dim]What's NOT collected:[/dim]")
        console.print("  • Your name or personal info")
        console.print("  • File paths or code")
        console.print("  • Command arguments")
        console.print("\n[dim]All data stored locally in: ~/.sudodog/telemetry.db[/dim]")
        console.print("\n[dim]To opt-out: sudodog local-telemetry disable[/dim]\n")
    else:
        console.print("[yellow]✗[/yellow] Local telemetry is DISABLED (opted out)")
        console.print("\n[dim]You've opted out of local usage statistics.[/dim]")
        console.print("[dim]To re-enable: sudodog local-telemetry enable[/dim]\n")

@local_telemetry.command('disable')
def local_telemetry_disable():
    """Opt-out of local usage statistics"""
    from .sudodog_telemetry import LocalTelemetry
    
    t = LocalTelemetry()
    
    console.print("\n[yellow]Disabling local telemetry...[/yellow]")
    
    # Track opt-out before disabling
    t.track_event('local_telemetry_disabled', {
        'version': '0.2.0',
    })
    
    t.disable()
    
    console.print("[green]✓[/green] Local telemetry disabled (opted out)")
    console.print("\n[dim]You can re-enable anytime with: sudodog local-telemetry enable[/dim]\n")

@local_telemetry.command('enable')
def local_telemetry_enable():
    """Re-enable local usage statistics"""
    from .sudodog_telemetry import LocalTelemetry
    
    t = LocalTelemetry()
    t.enable()
    
    # Track opt-in
    t.track_event('local_telemetry_enabled', {
        'version': '0.2.0',
    })
    
    console.print("[green]✓[/green] Local telemetry enabled")
    console.print("\n[dim]Thanks! This helps improve SudoDog for everyone.[/dim]\n")

# Add telemetry commands
from .cli_telemetry import add_telemetry_commands
add_telemetry_commands(cli)

if __name__ == '__main__':
    cli()
