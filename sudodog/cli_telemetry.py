"""
SudoDog - Telemetry CLI Commands
Manage anonymous analytics settings
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich import box
from .telemetry import get_telemetry
from .telemetry_ui import (
    show_telemetry_prompt,
    show_telemetry_status,
    show_telemetry_info
)

console = Console()


@click.group(name='telemetry')
def telemetry_group():
    """Manage anonymous analytics settings"""
    pass


@telemetry_group.command(name='enable')
def telemetry_enable():
    """Enable anonymous analytics"""
    telemetry = get_telemetry()
    
    if telemetry.is_enabled():
        console.print("\n[yellow]✓[/yellow] Analytics are already enabled\n")
        return
    
    telemetry.enable()
    
    console.print("\n[green]✓[/green] Anonymous analytics enabled")
    console.print(f"[dim]Anonymous ID: {telemetry.anonymous_id}[/dim]\n")
    console.print("[dim]View what we collect: sudodog telemetry info[/dim]")
    console.print("[dim]Check status: sudodog telemetry status[/dim]\n")


@telemetry_group.command(name='disable')
def telemetry_disable():
    """Disable anonymous analytics"""
    telemetry = get_telemetry()
    
    if not telemetry.is_enabled():
        console.print("\n[yellow]○[/yellow] Analytics are already disabled\n")
        return
    
    telemetry.disable()
    
    console.print("\n[green]✓[/green] Anonymous analytics disabled\n")
    console.print("We're no longer collecting any data.")
    console.print("[dim]You can re-enable anytime with: sudodog telemetry enable[/dim]\n")


@telemetry_group.command(name='status')
def telemetry_status():
    """Show telemetry status"""
    telemetry = get_telemetry()
    status = telemetry.get_status()
    
    show_telemetry_status(status)


@telemetry_group.command(name='info')
def telemetry_info():
    """Show detailed information about telemetry"""
    show_telemetry_info()


@telemetry_group.command(name='opt-in')
@click.option('--force', is_flag=True, help='Skip prompt and enable')
def telemetry_opt_in(force):
    """Interactive opt-in prompt (used during init)"""
    telemetry = get_telemetry()
    
    if telemetry.is_enabled():
        console.print("\n[green]✓[/green] Analytics are already enabled\n")
        return
    
    if force:
        telemetry.enable()
        console.print("\n[green]✓[/green] Anonymous analytics enabled\n")
        return
    
    # Show the interactive prompt
    response = show_telemetry_prompt()
    
    if response:
        telemetry.enable()
        # Track the install event
        telemetry.track_install()
    else:
        telemetry.disable()


# Export for use in main CLI
def add_telemetry_commands(cli):
    """Add telemetry commands to main CLI"""
    cli.add_command(telemetry_group)
