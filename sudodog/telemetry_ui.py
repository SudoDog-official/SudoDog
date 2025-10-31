"""
SudoDog - Telemetry Opt-In Prompt
Transparent, user-friendly consent flow
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich import box

console = Console()

def show_telemetry_prompt() -> bool:
    """
    Show telemetry opt-in prompt
    Returns: True if user opts in, False otherwise
    """
    
    console.print()
    
    # Create the prompt panel
    prompt_text = """[bold cyan]📊 Help Improve SudoDog[/bold cyan]

Share anonymous usage data to help us:
  [green]✓[/green] Improve threat detection
  [green]✓[/green] Fix bugs faster  
  [green]✓[/green] Prioritize features

[bold]We collect:[/bold]
  [green]✓[/green] Which commands you use
  [green]✓[/green] Error messages (sanitized)
  [green]✓[/green] Performance metrics
  [green]✓[/green] Threat patterns detected

[bold]We NEVER collect:[/bold]
  [red]✗[/red] Your agent code
  [red]✗[/red] File contents or paths
  [red]✗[/red] API keys or credentials
  [red]✗[/red] Command arguments
  [red]✗[/red] Any personally identifiable data

[dim]All data is anonymous and helps the entire community.[/dim]

[bold]Privacy Policy:[/bold] https://sudodog.com/privacy
[bold]Telemetry Details:[/bold] https://sudodog.com/telemetry"""

    panel = Panel(
        prompt_text,
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()
    
    # Ask for consent
    response = Confirm.ask(
        "[bold]Enable anonymous analytics?[/bold]",
        default=True
    )
    
    console.print()
    
    if response:
        console.print("[green]✓[/green] Thank you! Anonymous analytics enabled.")
        console.print("[dim]You can disable anytime with: sudodog telemetry disable[/dim]")
    else:
        console.print("[yellow]○[/yellow] Analytics disabled. You can enable later with: sudodog telemetry enable")
    
    console.print()
    
    return response


def show_telemetry_status(enabled: bool, anonymous_id: str = None) -> None:
    """Show current telemetry status"""
    
    console.print()
    console.print("[cyan]📊 Telemetry Status[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]")
    
    if enabled:
        console.print(f"[green]Status:[/green] Enabled")
        console.print(f"[dim]Anonymous ID: {anonymous_id}[/dim]")
        console.print()
        console.print("[bold]What we collect:[/bold]")
        console.print("  • Command usage (which features you use)")
        console.print("  • Error types (helps us fix bugs)")
        console.print("  • Performance metrics (execution time)")
        console.print("  • Threat patterns (improves detection)")
        console.print()
        console.print("[bold]What we DON'T collect:[/bold]")
        console.print("  • Your code or file contents")
        console.print("  • Command arguments or outputs")
        console.print("  • API keys or credentials")
        console.print("  • Personally identifiable information")
        console.print()
        console.print("[dim]To disable: sudodog telemetry disable[/dim]")
    else:
        console.print(f"[yellow]Status:[/yellow] Disabled")
        console.print()
        console.print("Analytics are disabled. We're not collecting any data.")
        console.print()
        console.print("[dim]To enable: sudodog telemetry enable[/dim]")
    
    console.print()
    console.print("[dim]Privacy Policy: https://sudodog.com/privacy[/dim]")
    console.print("[dim]Telemetry Details: https://sudodog.com/telemetry[/dim]")
    console.print()


def show_what_we_collect() -> None:
    """Show detailed information about what data is collected"""
    
    console.print()
    console.print("[cyan]📊 What SudoDog Collects[/cyan]")
    console.print("[cyan]" + "━" * 60 + "[/cyan]")
    console.print()
    
    # Example events
    examples = {
        "Command Usage": {
            "description": "Which commands you run",
            "example": {
                "event": "command_used",
                "command": "run",
                "used_docker": True,
                "cpu_limit": 2.0
            },
            "never": ["Actual command arguments", "File paths", "User data"]
        },
        "Error Tracking": {
            "description": "Sanitized error messages",
            "example": {
                "event": "error_occurred",
                "error_type": "ModuleNotFoundError",
                "error_message": "No module named '[SANITIZED]'"
            },
            "never": ["Full stack traces with paths", "User code", "Sensitive data"]
        },
        "Threat Detection": {
            "description": "Types of threats detected",
            "example": {
                "event": "threat_detected",
                "pattern_type": "sql_injection",
                "action_taken": "blocked"
            },
            "never": ["Actual blocked commands", "User data", "Code content"]
        },
        "Daemon Stats": {
            "description": "Aggregated performance metrics",
            "example": {
                "event": "daemon_stats",
                "container_count": 3,
                "avg_cpu_percent": 15.2,
                "avg_memory_percent": 28.5
            },
            "never": ["Container names", "User code", "Identifiable info"]
        }
    }
    
    for category, info in examples.items():
        console.print(f"[bold cyan]{category}[/bold cyan]")
        console.print(f"  {info['description']}")
        console.print()
        console.print("  [green]Example event:[/green]")
        console.print(f"  [dim]{info['example']}[/dim]")
        console.print()
        console.print("  [red]Never collected:[/red]")
        for item in info['never']:
            console.print(f"    • {item}")
        console.print()
    
    console.print("[bold]All events include:[/bold]")
    console.print("  • anonymous_id: One-way hash (not reversible)")
    console.print("  • timestamp: When event occurred")
    console.print("  • version: SudoDog version")
    console.print()
    console.print("[dim]View full source code:[/dim]")
    console.print("[dim]https://github.com/SudoDog-official/sudodog/blob/main/sudodog/telemetry.py[/dim]")
    console.print()
