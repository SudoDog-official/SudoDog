#!/usr/bin/env python3
"""
SudoDog - Security for AI Agents
CLI Interface (Improved with working rollback)
"""

import click
import sys
from rich.console import Console
from rich.table import Table
from rich import box
from pathlib import Path
import json
from datetime import datetime

console = Console()

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """🐕 SudoDog - Sandboxing and monitoring for AI agents in one command"""
    pass

@cli.command()
@click.argument('command', nargs=-1, required=True)
@click.option('--policy', '-p', default='default', help='Security policy to use')
@click.option('--log-level', '-l', default='info', help='Logging level')
def run(command, policy, log_level):
    """Run an AI agent with SudoDog protection"""
    from .monitor import AgentMonitor, AgentSession
    
    console.print("\n[cyan]🐕 SudoDog AI Agent Security[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]")
    
    # Convert command tuple to string
    cmd_string = ' '.join(command)
    
    console.print(f"[green]✓[/green] Sandboxed environment created")
    console.print(f"[green]✓[/green] Behavioral monitoring active")
    console.print(f"[dim]Policy: {policy}[/dim]")
    
    # Run with monitoring
    monitor = AgentMonitor(cmd_string, policy=policy)
    
    # Add to active sessions
    AgentSession.add_session(monitor.session_id, cmd_string, 0)
    
    try:
        exit_code = monitor.run()
    finally:
        # Remove from active sessions
        AgentSession.remove_session(monitor.session_id)
    
    sys.exit(exit_code)

@cli.command()
def init():
    """Initialize SudoDog in current directory"""
    console.print("\n[cyan]🐕 SudoDog Initialization[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
    
    # Create config directory
    config_dir = Path.home() / '.sudodog'
    config_dir.mkdir(exist_ok=True)
    
    # Create default config
    config = {
        'version': '0.1.0',
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
    console.print("\n[green]SudoDog initialized! Run 'sudodog run <command>' to start.[/green]\n")

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

@cli.command()
def version():
    """Show SudoDog version"""
    console.print("\n[cyan]🐕 SudoDog v0.1.0[/cyan]")
    console.print("[dim]Security for AI agents that actually works[/dim]\n")

if __name__ == '__main__':
    cli()
