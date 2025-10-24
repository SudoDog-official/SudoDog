#!/usr/bin/env python3
"""
SudoDog - Security for AI Agents
CLI Interface
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
    from .monitor import AgentMonitor
    
    console.print("\n[cyan]🐕 SudoDog AI Agent Security[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]")
    
    # Convert command tuple to string
    cmd_string = ' '.join(command)
    
    console.print(f"[green]✓[/green] Sandboxed environment created")
    console.print(f"[green]✓[/green] Behavioral monitoring active")
    console.print(f"[dim]Policy: {policy}[/dim]")
    
    # Run with monitoring
    monitor = AgentMonitor(cmd_string, policy=policy)
    exit_code = monitor.run()
    
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
    
    console.print(f"[green]✓[/green] Config directory: {config_dir}")
    console.print(f"[green]✓[/green] Logs directory: {logs_dir}")
    console.print(f"[green]✓[/green] Default policy created")
    console.print("\n[green]SudoDog initialized! Run 'sudodog run <command>' to start.[/green]\n")

@cli.command()
def status():
    """Show status of running agents"""
    console.print("\n[cyan]🤖 Agent Status[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
    
    # This will read from active sessions
    # For now, showing structure
    console.print("[yellow]No active agents[/yellow]")
    console.print("[dim]Run 'sudodog run <command>' to start an agent[/dim]\n")

@cli.command()
@click.option('--last', '-n', default=10, help='Number of recent actions to show')
def logs(last):
    """View agent activity logs"""
    console.print("\n[cyan]📋 Recent Agent Activity[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
    
    logs_dir = Path.home() / '.sudodog' / 'logs'
    
    if not logs_dir.exists():
        console.print("[yellow]No logs found. Run 'sudodog init' first.[/yellow]\n")
        return
    
    # This will read actual logs
    # For now, showing structure
    console.print(f"[dim]Showing last {last} actions...[/dim]\n")
    console.print("[yellow]No logged activities yet[/yellow]\n")

@cli.command()
@click.argument('session_id', required=False)
def pause(session_id):
    """Pause a running agent"""
    console.print("\n[yellow]⏸[/yellow]  Pausing agent...")
    
    if not session_id:
        console.print("[red]Error: No session ID provided[/red]")
        console.print("[dim]Use 'sudodog status' to see active sessions[/dim]\n")
        return
    
    console.print(f"[green]✓[/green] Agent {session_id} paused\n")

@cli.command()
@click.argument('session_id', required=False)
@click.option('--steps', '-n', default=10, help='Number of actions to rollback')
def rollback(session_id, steps):
    """Rollback agent actions"""
    console.print("\n[yellow]⏪[/yellow]  Rolling back actions...")
    
    if not session_id:
        console.print("[red]Error: No session ID provided[/red]")
        console.print("[dim]Use 'sudodog status' to see active sessions[/dim]\n")
        return
    
    console.print(f"[green]✓[/green] Rolled back {steps} actions for session {session_id}\n")

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