"""
SudoDog - Telemetry User Interface
Beautiful prompts for telemetry opt-in
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()


def show_telemetry_prompt() -> bool:
    """
    Show telemetry opt-in prompt to user
    
    Returns:
        True if user opted in, False otherwise
    """
    
    # Create the prompt content
    prompt_text = """[cyan]📊 Help Improve SudoDog[/cyan]

Share anonymous usage data to help us:
  [green]•[/green] Improve threat detection
  [green]•[/green] Fix bugs faster
  [green]•[/green] Prioritize features
  [green]•[/green] Train ML models for anomaly detection

[bold]We collect:[/bold]
  [green]✓[/green] Which features you use
  [green]✓[/green] Error messages (sanitized)
  [green]✓[/green] Performance metrics (CPU, memory, duration)
  [green]✓[/green] Threat patterns detected

[bold]We NEVER collect:[/bold]
  [red]✗[/red] Your agent code
  [red]✗[/red] File contents or paths
  [red]✗[/red] API keys or credentials
  [red]✗[/red] Command arguments or outputs
  [red]✗[/red] Any personally identifiable data

[bold]Where data goes:[/bold]
  [cyan]•[/cyan] Performance data sent to sudodog-platform.fly.dev
  [cyan]•[/cyan] Used to train ML models that detect anomalies
  [cyan]•[/cyan] Helps paid tier users get better insights
  [cyan]•[/cyan] All data is anonymous (ID: free-user-xxxxxxxx)

All data is anonymous and helps the entire community.

[dim]Privacy Policy: https://sudodog.com/privacy[/dim]
[dim]Telemetry Details: https://sudodog.com/telemetry[/dim]"""
    
    # Display the panel
    console.print()
    console.print(Panel(
        prompt_text,
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()
    
    # Ask for consent
    response = Confirm.ask(
        "[cyan]Enable anonymous analytics?[/cyan]",
        default=False  # Default to No (privacy-first)
    )
    
    if response:
        console.print("\n[green]✓[/green] Thank you! Anonymous analytics enabled.")
        console.print("[dim]You can disable anytime with: sudodog telemetry disable[/dim]\n")
    else:
        console.print("\n[dim]No problem! You can enable later with: sudodog telemetry enable[/dim]\n")
    
    return response


def show_telemetry_status(telemetry_status: dict) -> None:
    """
    Show current telemetry status to user
    
    Args:
        telemetry_status: Dict with 'enabled', 'anonymous_id', 'endpoint'
    """
    console.print()
    console.print("[cyan]📊 Telemetry Status[/cyan]")
    console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
    
    if telemetry_status['enabled']:
        console.print(f"[green]Status:[/green] Enabled")
        console.print(f"[dim]Anonymous ID:[/dim] {telemetry_status['anonymous_id']}")
        console.print(f"[dim]Platform API:[/dim] sudodog-platform.fly.dev\n")
    else:
        console.print("[yellow]Status:[/yellow] Disabled\n")
    
    # Show what we collect
    console.print("[bold]What we collect:[/bold]")
    console.print("  [green]•[/green] Command usage (which features you use)")
    console.print("  [green]•[/green] Error types (helps us fix bugs)")
    console.print("  [green]•[/green] Performance metrics (CPU, memory, execution time)")
    console.print("  [green]•[/green] Threat patterns (improves detection)")
    console.print("  [green]•[/green] Agent execution data (trains ML models)\n")
    
    # Show what we DON'T collect
    console.print("[bold]What we DON'T collect:[/bold]")
    console.print("  [red]•[/red] Your code or file contents")
    console.print("  [red]•[/red] Command arguments or outputs")
    console.print("  [red]•[/red] API keys or credentials")
    console.print("  [red]•[/red] Personally identifiable information\n")
    
    # Show how to change
    if telemetry_status['enabled']:
        console.print("[dim]To disable: sudodog telemetry disable[/dim]")
    else:
        console.print("[dim]To enable: sudodog telemetry enable[/dim]")
    
    console.print()
    console.print("[dim]Privacy Policy:[/dim] https://sudodog.com/privacy")
    console.print("[dim]Telemetry Details:[/dim] https://sudodog.com/telemetry")
    console.print()


def show_telemetry_info() -> None:
    """
    Show detailed information about what telemetry collects
    """
    
    info_text = """[cyan]📊 Telemetry Information[/cyan]

[bold]What We Collect (When Enabled):[/bold]

[green]1. Command Usage[/green]
   • Which commands you run (e.g., 'run', 'logs', 'daemon')
   • Options used (e.g., --docker, --cpu-limit)
   • NOT the actual command arguments or outputs

[green]2. Error Messages[/green]
   • Error types (e.g., "FileNotFoundError")
   • Sanitized error messages (paths and usernames removed)
   • Stack traces (with sensitive data stripped)
   • NOT your code or file contents

[green]3. Performance Metrics[/green]
   • Command execution time
   • Resource usage (CPU, memory)
   • Container statistics (when using Docker)
   • Sent to platform API for ML training

[green]4. Threat Patterns[/green]
   • Types of threats detected (e.g., "sql_injection")
   • Actions taken (e.g., "blocked", "warned")
   • NOT the actual commands that were blocked

[green]5. Platform Telemetry[/green]
   • Performance data sent to sudodog-platform.fly.dev
   • Used to train ML models for anomaly detection
   • Powers insights for paid tier users
   • Completely anonymous (ID: free-user-xxxxxxxx)

[bold]What We NEVER Collect:[/bold]

[red]✗[/red] Your agent code or scripts
[red]✗[/red] File contents or paths
[red]✗[/red] Command arguments or outputs
[red]✗[/red] API keys, tokens, or credentials
[red]✗[/red] Environment variables
[red]✗[/red] Personally identifiable information
[red]✗[/red] IP addresses (sanitized in logs)
[red]✗[/red] User names or email addresses

[bold]Privacy Guarantees:[/bold]

- [green]Opt-in only[/green] - Disabled by default
- [green]Anonymous[/green] - Uses random ID (e.g., free-user-a1b2c3d4)
- [green]Transparent[/green] - See exactly what we collect
- [green]Respectful[/green] - Easy to disable anytime
- [green]Beneficial[/green] - Helps train ML models for the community

[bold]How Your Data Helps:[/bold]

Your anonymous usage data helps:
- Train ML models to detect anomalies in AI agents
- Improve threat detection patterns
- Fix bugs and errors faster
- Understand which features are most valuable
- Provide better insights to paid tier users
- Help the entire community stay secure

[bold]The Value Exchange:[/bold]

Free tier users (you):
- Share anonymous performance data
- Help train ML models with real-world patterns

Paid tier users:
- Get ML-powered anomaly detection
- Benefit from insights trained on community data

Everyone wins - better security for all!

[bold]Your Rights:[/bold]

- Enable/disable anytime: [cyan]sudodog telemetry enable/disable[/cyan]
- Check status: [cyan]sudodog telemetry status[/cyan]
- View this info: [cyan]sudodog telemetry info[/cyan]

[dim]Full Privacy Policy: https://sudodog.com/privacy[/dim]
[dim]Technical Details: https://sudodog.com/telemetry[/dim]
[dim]Platform API: https://sudodog-platform.fly.dev[/dim]"""
    
    console.print()
    console.print(Panel(
        info_text,
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()
