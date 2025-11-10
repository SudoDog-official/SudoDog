"""
Rate Limit CLI Commands for SudoDog
Add to cli.py with: from sudodog.cli_rate_limit import register_rate_limit_commands
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def register_rate_limit_commands(cli):
    """Register rate limit commands with the CLI"""
    
    @cli.command()
    @click.option('--provider', '-p', help='Show limits for specific provider')
    @click.option('--window', '-w', default='minute', 
                  type=click.Choice(['minute', 'hour', 'day']),
                  help='Time window to analyze')
    def limits(provider, window):
        """View API rate limit usage and warnings"""
        from .rate_limiter import RateLimitTracker
        
        tracker = RateLimitTracker()
        
        console.print("\n[cyan]⚡ API Rate Limit Status[/cyan]")
        console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
        
        if provider:
            # Show specific provider
            usage = tracker.analyze_usage(provider, window)
            
            if usage['requests'] == 0:
                console.print(f"[yellow]No {provider} requests in last {window}[/yellow]\n")
                return
            
            _display_provider_usage(usage, window)
        else:
            # Show all providers
            summary = tracker.get_usage_summary()
            
            if summary['total_requests'] == 0:
                console.print("[yellow]No API requests tracked yet[/yellow]")
                console.print("[dim]Make some requests with 'sudodog run' first[/dim]\n")
                return
            
            # Summary stats
            console.print(f"[green]Total Requests:[/green] {summary['total_requests']}")
            console.print(f"[cyan]Providers Used:[/cyan] {summary['providers_used']}")
            
            if summary['warnings'] > 0:
                console.print(f"[red]⚠️  Warnings:[/red] {summary['warnings']}")
            
            console.print()
            
            # Table of all providers
            if summary['providers']:
                table = Table(box=box.ROUNDED)
                table.add_column("Provider", style="cyan")
                table.add_column("Requests", style="white")
                table.add_column("Limit", style="dim")
                table.add_column("Usage", style="yellow")
                table.add_column("Status", style="white")
                
                for usage in summary['providers']:
                    # Color code the usage percentage
                    usage_pct = usage['usage_percent']
                    if usage['warning'] == 'critical':
                        status = "[red]🚨 CRITICAL[/red]"
                        usage_str = f"[red]{usage_pct}%[/red]"
                    elif usage['warning'] == 'warning':
                        status = "[yellow]⚠️  WARNING[/yellow]"
                        usage_str = f"[yellow]{usage_pct}%[/yellow]"
                    else:
                        status = "[green]✓ OK[/green]"
                        usage_str = f"[green]{usage_pct}%[/green]"
                    
                    limit_str = f"{usage['limit']}/min" if usage['limit'] else "Unknown"
                    
                    table.add_row(
                        usage['provider_name'],
                        str(usage['requests']),
                        limit_str,
                        usage_str,
                        status
                    )
                
                console.print(table)
                console.print()
                
                # Show warnings
                warnings = [u for u in summary['providers'] if u['warning']]
                if warnings:
                    console.print("[yellow]⚠️  Rate Limit Warnings:[/yellow]")
                    for w in warnings:
                        remaining = w['remaining'] if w['remaining'] is not None else "?"
                        console.print(f"  • {w['provider_name']}: {w['usage_percent']}% used "
                                    f"({remaining} requests remaining)")
                    console.print()
    
    
    @cli.command(name='limits-info')
    @click.option('--provider', '-p', help='Show limits for specific provider')
    def limits_info(provider):
        """Show rate limit information for API providers"""
        from .rate_limiter import RateLimitTracker
        
        tracker = RateLimitTracker()
        
        console.print("\n[cyan]📋 API Provider Rate Limits[/cyan]")
        console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
        
        providers = [provider] if provider else tracker.PROVIDER_LIMITS.keys()
        
        for prov in providers:
            if prov not in tracker.PROVIDER_LIMITS:
                console.print(f"[red]Unknown provider: {prov}[/red]\n")
                continue
            
            info = tracker.PROVIDER_LIMITS[prov]
            console.print(f"[green]{info['name']}[/green]")
            
            for model, limits in info['limits'].items():
                console.print(f"  [cyan]{model}:[/cyan]")
                if 'rpm' in limits:
                    console.print(f"    • {limits['rpm']:,} requests/minute")
                if 'tpm' in limits:
                    console.print(f"    • {limits['tpm']:,} tokens/minute")
                if 'rpd' in limits:
                    console.print(f"    • {limits['rpd']:,} requests/day")
            console.print()
        
        console.print("[dim]💡 Set custom limits with: sudodog set-limit[/dim]\n")
    
    
    @cli.command(name='set-limit')
    @click.argument('provider')
    @click.argument('limit_type', type=click.Choice(['rpm', 'tpm', 'rpd']))
    @click.argument('value', type=int)
    def set_limit(provider, limit_type, value):
        """Set custom rate limit for a provider
        
        Examples:
            sudodog set-limit openai rpm 1000
            sudodog set-limit anthropic tpm 50000
        """
        from .rate_limiter import RateLimitTracker
        
        tracker = RateLimitTracker()
        tracker.set_custom_limit(provider, limit_type, value)
        
        limit_names = {
            'rpm': 'requests/minute',
            'tpm': 'tokens/minute',
            'rpd': 'requests/day'
        }
        
        console.print(f"\n[green]✓[/green] Set {provider} {limit_names[limit_type]} limit to {value:,}\n")


def _display_provider_usage(usage: dict, window: str):
    """Display detailed usage for a single provider"""
    console.print(f"[green]Provider:[/green] {usage['provider_name']}")
    console.print(f"[cyan]Time Window:[/cyan] Last {window}")
    console.print(f"[white]Requests:[/white] {usage['requests']}")
    
    if usage['limit']:
        console.print(f"[white]Limit:[/white] {usage['limit']:,}")
        console.print(f"[white]Remaining:[/white] {usage['remaining']:,}")
        
        # Progress bar
        usage_pct = usage['usage_percent']
        bar_width = 30
        filled = int(bar_width * usage_pct / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        if usage['warning'] == 'critical':
            color = 'red'
            status = '🚨 CRITICAL'
        elif usage['warning'] == 'warning':
            color = 'yellow'
            status = '⚠️  WARNING'
        else:
            color = 'green'
            status = '✓ OK'
        
        console.print(f"\n[{color}]{bar}[/{color}] {usage_pct}%")
        console.print(f"[{color}]{status}[/{color}]\n")
    else:
        console.print("[dim]No rate limit data available[/dim]\n")
