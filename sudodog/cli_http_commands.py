"""
HTTP CLI Commands for SudoDog
Add to cli.py with: from sudodog.cli_http_commands import register_http_commands
"""

import click
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()

def register_http_commands(cli):
    """Register HTTP commands with the CLI"""
    
    @cli.command()
    @click.option('--session', '-s', help='Show HTTP logs for specific session')
    @click.option('--provider', '-p', help='Filter by API provider (openai, anthropic, etc.)')
    @click.option('--last', '-n', default=20, help='Number of requests to show')
    @click.option('--errors-only', is_flag=True, help='Show only failed requests')
    def http(session, provider, last, errors_only):
        """View HTTP traffic logs"""
        from .http_interceptor import HTTPInterceptor
        
        console.print("\n[cyan]🌐 HTTP Traffic Logs[/cyan]")
        console.print("[cyan]" + "─" * 40 + "[/cyan]\n")
        
        logs_dir = Path.home() / '.sudodog' / 'logs'
        
        if not logs_dir.exists():
            console.print("[yellow]No logs found. Run 'sudodog init' first.[/yellow]\n")
            return
        
        if session:
            log_files = [logs_dir / f'{session}_http.jsonl']
            if not log_files[0].exists():
                console.print(f"[red]No HTTP logs found for session {session}[/red]\n")
                return
        else:
            log_files = sorted(logs_dir.glob('*_http.jsonl'), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not log_files:
            console.print("[yellow]No HTTP traffic logged yet[/yellow]")
            console.print("[dim]HTTP logging starts automatically with 'sudodog run'[/dim]\n")
            return
        
        total_shown = 0
        request_map = {}
        
        for log_file in log_files:
            if total_shown >= last:
                break
            
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        if provider and entry.get('provider') != provider:
                            continue
                        
                        if entry['type'] == 'http_request':
                            request_map[entry['request_id']] = entry
                        
                        elif entry['type'] == 'http_response':
                            request_id = entry['request_id']
                            request_data = request_map.get(request_id, {})
                            
                            if errors_only and entry.get('status_code', 0) < 400 and not entry.get('error'):
                                continue
                            
                            if total_shown >= last:
                                break
                            
                            timestamp = entry.get('timestamp', 'Unknown')
                            if timestamp != 'Unknown':
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                time_str = dt.strftime('%H:%M:%S')
                            else:
                                time_str = 'Unknown'
                            
                            method = request_data.get('method', 'GET')
                            url = request_data.get('url', 'Unknown')
                            provider_name = request_data.get('provider', 'unknown')
                            status = entry.get('status_code', 0)
                            duration = entry.get('duration_ms', 0)
                            error = entry.get('error')
                            
                            if len(url) > 60:
                                url = url[:57] + "..."
                            
                            if error:
                                status_color = 'red'
                                status_text = f'ERROR'
                            elif status >= 500:
                                status_color = 'red'
                                status_text = f'{status}'
                            elif status >= 400:
                                status_color = 'yellow'
                                status_text = f'{status}'
                            elif status >= 200:
                                status_color = 'green'
                                status_text = f'{status}'
                            else:
                                status_color = 'dim'
                                status_text = f'{status}'
                            
                            console.print(f"[{time_str}] [{provider_name.upper()}] {method} {url}")
                            console.print(f"  [{status_color}]↳ {status_text}[/{status_color}] {duration:.0f}ms", end='')
                            
                            if error:
                                console.print(f" [red]- {error}[/red]")
                            else:
                                console.print()
                            
                            total_shown += 1
                    
                    except json.JSONDecodeError:
                        continue
        
        if total_shown == 0:
            console.print("[yellow]No HTTP requests found[/yellow]\n")
        else:
            console.print(f"\n[dim]Showing {total_shown} most recent requests[/dim]")
            console.print(f"[dim]Log files: {logs_dir}/*_http.jsonl[/dim]\n")
    
    
    @cli.command(name='http-stats')
    @click.argument('session_id', required=False)
    def http_stats(session_id):
        """Show HTTP traffic statistics"""
        from .http_interceptor import HTTPInterceptor
        
        console.print("\n[cyan]📊 HTTP Traffic Statistics[/cyan]")
        console.print("[cyan]" + "━" * 40 + "[/cyan]\n")
        
        logs_dir = Path.home() / '.sudodog' / 'logs'
        
        if not logs_dir.exists():
            console.print("[yellow]No logs found.[/yellow]\n")
            return
        
        if session_id:
            log_files = [logs_dir / f'{session_id}_http.jsonl']
            if not log_files[0].exists():
                console.print(f"[red]No HTTP logs for session {session_id}[/red]\n")
                return
        else:
            log_files = list(logs_dir.glob('*_http.jsonl'))
        
        if not log_files:
            console.print("[yellow]No HTTP logs found[/yellow]\n")
            return
        
        total_stats = {
            'total_requests': 0,
            'by_provider': {},
            'by_status': {},
            'total_duration_ms': 0,
            'errors': 0
        }
        
        for log_file in log_files:
            interceptor = HTTPInterceptor(log_file.stem.replace('_http', ''), logs_dir.parent)
            stats = interceptor.get_stats()
            
            total_stats['total_requests'] += stats['total_requests']
            total_stats['total_duration_ms'] += stats['total_duration_ms']
            total_stats['errors'] += stats['errors']
            
            for provider, count in stats['by_provider'].items():
                total_stats['by_provider'][provider] = total_stats['by_provider'].get(provider, 0) + count
            
            for status, count in stats['by_status'].items():
                total_stats['by_status'][status] = total_stats['by_status'].get(status, 0) + count
        
        console.print(f"[green]Total Requests:[/green] {total_stats['total_requests']}")
        console.print(f"[yellow]Errors:[/yellow] {total_stats['errors']}")
        
        if total_stats['total_requests'] > 0:
            avg_duration = total_stats['total_duration_ms'] / total_stats['total_requests']
            console.print(f"[cyan]Avg Duration:[/cyan] {avg_duration:.0f}ms")
        
        if total_stats['by_provider']:
            console.print("\n[cyan]By Provider:[/cyan]")
            for provider, count in sorted(total_stats['by_provider'].items(), key=lambda x: x[1], reverse=True):
                console.print(f"  • {provider}: {count} requests")
        
        if total_stats['by_status']:
            console.print("\n[cyan]By Status Code:[/cyan]")
            for status, count in sorted(total_stats['by_status'].items()):
                status_str = str(status)
                if int(status) >= 500:
                    console.print(f"  • [red]{status_str}[/red]: {count}")
                elif int(status) >= 400:
                    console.print(f"  • [yellow]{status_str}[/yellow]: {count}")
                else:
                    console.print(f"  • [green]{status_str}[/green]: {count}")
        
        console.print()
