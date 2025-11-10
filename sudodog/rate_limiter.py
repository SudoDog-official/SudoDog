"""
SudoDog - Rate Limit Tracker
Tracks API usage and warns before hitting rate limits
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

class RateLimitTracker:
    """Track API rate limits and usage across providers"""
    
    # Known provider rate limits (requests per minute/hour)
    PROVIDER_LIMITS = {
        'openai': {
            'name': 'OpenAI',
            'limits': {
                'gpt-4': {'rpm': 500, 'tpm': 30000, 'rpd': 10000},
                'gpt-3.5-turbo': {'rpm': 3500, 'tpm': 90000, 'rpd': 10000},
                'default': {'rpm': 500, 'tpm': 30000, 'rpd': 10000}
            }
        },
        'anthropic': {
            'name': 'Anthropic',
            'limits': {
                'claude-3-opus': {'rpm': 1000, 'tpm': 80000, 'rpd': 50000},
                'claude-3-sonnet': {'rpm': 2000, 'tpm': 160000, 'rpd': 100000},
                'default': {'rpm': 1000, 'tpm': 80000, 'rpd': 50000}
            }
        },
        'google': {
            'name': 'Google AI',
            'limits': {
                'default': {'rpm': 60, 'tpm': 32000, 'rpd': 1500}
            }
        },
        'cohere': {
            'name': 'Cohere',
            'limits': {
                'default': {'rpm': 100, 'tpm': 40000, 'rpd': 10000}
            }
        },
        'huggingface': {
            'name': 'HuggingFace',
            'limits': {
                'default': {'rpm': 30, 'tpm': 10000, 'rpd': 1000}
            }
        },
        'replicate': {
            'name': 'Replicate',
            'limits': {
                'default': {'rpm': 50, 'tpm': 20000, 'rpd': 5000}
            }
        }
    }
    
    # Warning thresholds
    WARNING_THRESHOLD = 0.8  # Warn at 80%
    CRITICAL_THRESHOLD = 0.95  # Critical at 95%
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id
        self.config_dir = Path.home() / '.sudodog'
        self.limits_file = self.config_dir / 'rate_limits.json'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize limits config
        self.limits_config = self._load_limits_config()
    
    def _load_limits_config(self) -> Dict:
        """Load custom rate limit configuration"""
        if self.limits_file.exists():
            with open(self.limits_file, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            config = {
                'custom_limits': {},
                'warning_threshold': self.WARNING_THRESHOLD,
                'critical_threshold': self.CRITICAL_THRESHOLD
            }
            self._save_limits_config(config)
            return config
    
    def _save_limits_config(self, config: Dict):
        """Save rate limit configuration"""
        with open(self.limits_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_provider_limits(self, provider: str, model: Optional[str] = None) -> Dict:
        """Get rate limits for a provider/model"""
        provider = provider.lower()
        
        # Check custom limits first
        if provider in self.limits_config.get('custom_limits', {}):
            custom = self.limits_config['custom_limits'][provider]
            if model and model in custom:
                return custom[model]
            return custom.get('default', {})
        
        # Use built-in limits
        if provider in self.PROVIDER_LIMITS:
            limits = self.PROVIDER_LIMITS[provider]['limits']
            if model and model in limits:
                return limits[model]
            return limits.get('default', {})
        
        # Unknown provider - no limits
        return {}
    
    def analyze_usage(self, provider: str, time_window: str = 'minute') -> Dict:
        """
        Analyze API usage for a provider within a time window
        
        Args:
            provider: API provider name
            time_window: 'minute', 'hour', or 'day'
        
        Returns:
            Dict with usage stats and warnings
        """
        logs_dir = self.config_dir / 'logs'
        
        if not logs_dir.exists():
            return {
                'provider': provider,
                'requests': 0,
                'tokens': 0,
                'time_window': time_window,
                'limits': {},
                'usage_percent': 0,
                'warning': None
            }
        
        # Calculate time window
        now = datetime.now()
        if time_window == 'minute':
            start_time = now - timedelta(minutes=1)
            limit_key = 'rpm'
        elif time_window == 'hour':
            start_time = now - timedelta(hours=1)
            limit_key = 'tpm'
        elif time_window == 'day':
            start_time = now - timedelta(days=1)
            limit_key = 'rpd'
        else:
            raise ValueError(f"Invalid time_window: {time_window}")
        
        # Count requests from HTTP logs
        request_count = 0
        token_count = 0
        
        for log_file in logs_dir.glob('*_http.jsonl'):
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Only count requests for this provider
                        if entry.get('provider') != provider:
                            continue
                        
                        # Check if within time window
                        timestamp = datetime.fromisoformat(entry['timestamp'])
                        if timestamp < start_time:
                            continue
                        
                        if entry['type'] == 'http_request':
                            request_count += 1
                        
                        # Try to extract token count from response
                        elif entry['type'] == 'http_response':
                            body = entry.get('body', '')
                            if body and 'usage' in body:
                                try:
                                    usage = json.loads(body).get('usage', {})
                                    token_count += usage.get('total_tokens', 0)
                                except:
                                    pass
                    
                    except (json.JSONDecodeError, ValueError):
                        continue
        
        # Get limits for this provider
        limits = self.get_provider_limits(provider)
        limit_value = limits.get(limit_key, 0)
        
        # Calculate usage percentage
        usage_percent = (request_count / limit_value * 100) if limit_value > 0 else 0
        
        # Determine warning level
        warning = None
        if usage_percent >= self.limits_config.get('critical_threshold', self.CRITICAL_THRESHOLD) * 100:
            warning = 'critical'
        elif usage_percent >= self.limits_config.get('warning_threshold', self.WARNING_THRESHOLD) * 100:
            warning = 'warning'
        
        return {
            'provider': provider,
            'provider_name': self.PROVIDER_LIMITS.get(provider, {}).get('name', provider),
            'requests': request_count,
            'tokens': token_count,
            'time_window': time_window,
            'limit': limit_value,
            'usage_percent': round(usage_percent, 1),
            'warning': warning,
            'remaining': max(0, limit_value - request_count) if limit_value > 0 else None
        }
    
    def get_all_usage(self) -> List[Dict]:
        """Get usage stats for all providers"""
        logs_dir = self.config_dir / 'logs'
        
        if not logs_dir.exists():
            return []
        
        # Find all providers that have been used
        providers = set()
        for log_file in logs_dir.glob('*_http.jsonl'):
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        provider = entry.get('provider')
                        if provider and provider != 'unknown':
                            providers.add(provider)
                    except json.JSONDecodeError:
                        continue
        
        # Get usage for each provider
        all_usage = []
        for provider in providers:
            usage = self.analyze_usage(provider, 'minute')
            if usage['requests'] > 0:
                all_usage.append(usage)
        
        return sorted(all_usage, key=lambda x: x['usage_percent'], reverse=True)
    
    def check_limit_warnings(self, provider: str) -> Optional[str]:
        """
        Check if provider is approaching rate limits
        
        Returns warning message if applicable
        """
        usage = self.analyze_usage(provider, 'minute')
        
        if usage['warning'] == 'critical':
            return f"🚨 CRITICAL: {usage['provider_name']} at {usage['usage_percent']}% of rate limit!"
        elif usage['warning'] == 'warning':
            return f"⚠️  WARNING: {usage['provider_name']} at {usage['usage_percent']}% of rate limit"
        
        return None
    
    def get_usage_summary(self) -> Dict:
        """Get summary of all API usage"""
        all_usage = self.get_all_usage()
        
        total_requests = sum(u['requests'] for u in all_usage)
        providers_used = len(all_usage)
        warnings = [u for u in all_usage if u['warning']]
        
        return {
            'total_requests': total_requests,
            'providers_used': providers_used,
            'warnings': len(warnings),
            'providers': all_usage
        }
    
    def set_custom_limit(self, provider: str, limit_type: str, value: int):
        """Set a custom rate limit for a provider"""
        if 'custom_limits' not in self.limits_config:
            self.limits_config['custom_limits'] = {}
        
        if provider not in self.limits_config['custom_limits']:
            self.limits_config['custom_limits'][provider] = {'default': {}}
        
        self.limits_config['custom_limits'][provider]['default'][limit_type] = value
        self._save_limits_config(self.limits_config)
    
    def reset_usage(self):
        """Reset usage tracking (archive old logs)"""
        logs_dir = self.config_dir / 'logs'
        archive_dir = self.config_dir / 'logs_archive'
        archive_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for log_file in logs_dir.glob('*_http.jsonl'):
            archive_path = archive_dir / f"{timestamp}_{log_file.name}"
            log_file.rename(archive_path)
