"""
SudoDog - HTTP Interceptor
Captures all HTTP requests/responses for monitoring and analysis
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import re

class HTTPInterceptor:
    """Intercepts and logs HTTP calls made by AI agents"""
    
    def __init__(self, session_id: str, log_dir: Optional[Path] = None):
        self.session_id = session_id
        self.log_dir = log_dir or Path.home() / '.sudodog' / 'logs'
        self.http_log_file = self.log_dir / f'{session_id}_http.jsonl'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Patterns for detecting API providers
        self.provider_patterns = {
            'openai': r'api\.openai\.com',
            'anthropic': r'api\.anthropic\.com',
            'google': r'(generativelanguage\.googleapis\.com|aiplatform\.googleapis\.com)',
            'cohere': r'api\.cohere\.(ai|com)',
            'huggingface': r'api-inference\.huggingface\.co',
            'replicate': r'api\.replicate\.com',
        }
        
        # Sensitive headers to redact
        self.sensitive_headers = {
            'authorization', 'api-key', 'x-api-key', 'apikey',
            'auth-token', 'x-auth-token', 'bearer', 'cookie',
            'x-openai-api-key', 'x-anthropic-api-key'
        }
        
        # Patterns for sensitive data in bodies
        self.sensitive_patterns = [
            (r'"api_key"\s*:\s*"([^"]+)"', '"api_key": "[REDACTED]"'),
            (r'"apiKey"\s*:\s*"([^"]+)"', '"apiKey": "[REDACTED]"'),
            (r'"token"\s*:\s*"([^"]+)"', '"token": "[REDACTED]"'),
            (r'"password"\s*:\s*"([^"]+)"', '"password": "[REDACTED]"'),
            (r'Bearer\s+([A-Za-z0-9\-._~+/]+)', 'Bearer [REDACTED]'),
        ]
    
    def detect_provider(self, url: str) -> str:
        """Detect API provider from URL"""
        for provider, pattern in self.provider_patterns.items():
            if re.search(pattern, url, re.IGNORECASE):
                return provider
        return 'unknown'
    
    def redact_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Redact sensitive headers"""
        if not headers:
            return {}
        
        redacted = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                redacted[key] = '[REDACTED]'
            else:
                redacted[key] = value
        return redacted
    
    def redact_body(self, body: str) -> str:
        """Redact sensitive data from request/response body"""
        if not body:
            return body
        
        redacted = body
        for pattern, replacement in self.sensitive_patterns:
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
        
        return redacted
    
    def truncate_body(self, body: str, max_length: int = 5000) -> str:
        """Truncate very long bodies to prevent log bloat"""
        if not body or len(body) <= max_length:
            return body
        
        return body[:max_length] + f'\n... [TRUNCATED {len(body) - max_length} chars]'
    
    def log_request(self, 
                   method: str,
                   url: str,
                   headers: Optional[Dict] = None,
                   body: Optional[str] = None,
                   request_id: Optional[str] = None) -> str:
        """
        Log an HTTP request
        
        Returns:
            request_id for matching with response
        """
        if request_id is None:
            request_id = f"{int(time.time() * 1000)}"
        
        provider = self.detect_provider(url)
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'request_id': request_id,
            'type': 'http_request',
            'method': method.upper(),
            'url': url,
            'provider': provider,
            'headers': self.redact_headers(headers or {}),
            'body': self.truncate_body(self.redact_body(body or '')),
        }
        
        with open(self.http_log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        return request_id
    
    def log_response(self,
                    request_id: str,
                    status_code: int,
                    headers: Optional[Dict] = None,
                    body: Optional[str] = None,
                    duration_ms: Optional[float] = None,
                    error: Optional[str] = None):
        """Log an HTTP response"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'request_id': request_id,
            'type': 'http_response',
            'status_code': status_code,
            'headers': self.redact_headers(headers or {}),
            'body': self.truncate_body(self.redact_body(body or '')),
            'duration_ms': duration_ms,
            'error': error,
        }
        
        with open(self.http_log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from HTTP logs"""
        if not self.http_log_file.exists():
            return {
                'total_requests': 0,
                'by_provider': {},
                'by_status': {},
                'total_duration_ms': 0,
                'errors': 0
            }
        
        stats = {
            'total_requests': 0,
            'by_provider': {},
            'by_status': {},
            'total_duration_ms': 0,
            'errors': 0
        }
        
        with open(self.http_log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    if entry['type'] == 'http_request':
                        stats['total_requests'] += 1
                        provider = entry.get('provider', 'unknown')
                        stats['by_provider'][provider] = stats['by_provider'].get(provider, 0) + 1
                    
                    elif entry['type'] == 'http_response':
                        status = entry.get('status_code')
                        if status:
                            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                        
                        duration = entry.get('duration_ms', 0)
                        if duration:
                            stats['total_duration_ms'] += duration
                        
                        if entry.get('error') or (status and status >= 400):
                            stats['errors'] += 1
                
                except json.JSONDecodeError:
                    continue
        
        return stats


def patch_requests_library(interceptor: HTTPInterceptor):
    """Monkey-patch the requests library to intercept HTTP calls"""
    try:
        import requests
        original_request = requests.Session.request
        
        def intercepted_request(self, method, url, **kwargs):
            start_time = time.time()
            request_id = None
            
            try:
                # Log request
                headers = kwargs.get('headers', {})
                body = None
                
                # Extract body
                if 'json' in kwargs:
                    body = json.dumps(kwargs['json'])
                elif 'data' in kwargs:
                    body = str(kwargs['data'])
                
                request_id = interceptor.log_request(
                    method=method,
                    url=url,
                    headers=headers,
                    body=body
                )
                
                # Make actual request
                response = original_request(self, method, url, **kwargs)
                
                # Log response
                duration_ms = (time.time() - start_time) * 1000
                
                response_headers = dict(response.headers)
                response_body = None
                try:
                    response_body = response.text
                except:
                    response_body = '[Binary content]'
                
                interceptor.log_response(
                    request_id=request_id,
                    status_code=response.status_code,
                    headers=response_headers,
                    body=response_body,
                    duration_ms=duration_ms
                )
                
                return response
                
            except Exception as e:
                # Log error
                duration_ms = (time.time() - start_time) * 1000
                if request_id:
                    interceptor.log_response(
                        request_id=request_id,
                        status_code=0,
                        error=str(e),
                        duration_ms=duration_ms
                    )
                raise
        
        requests.Session.request = intercepted_request
        return True
        
    except ImportError:
        # requests not installed, that's OK
        return False


def patch_urllib3_library(interceptor: HTTPInterceptor):
    """Monkey-patch urllib3 to intercept HTTP calls"""
    try:
        import urllib3
        original_urlopen = urllib3.HTTPConnectionPool.urlopen
        
        def intercepted_urlopen(self, method, url, body=None, headers=None, **kwargs):
            start_time = time.time()
            request_id = None
            
            try:
                # Build full URL
                full_url = f"{self.scheme}://{self.host}:{self.port}{url}"
                
                # Log request
                request_id = interceptor.log_request(
                    method=method,
                    url=full_url,
                    headers=headers,
                    body=body.decode('utf-8') if isinstance(body, bytes) else body
                )
                
                # Make actual request
                response = original_urlopen(self, method, url, body=body, headers=headers, **kwargs)
                
                # Log response
                duration_ms = (time.time() - start_time) * 1000
                
                response_headers = dict(response.headers)
                response_body = response.data.decode('utf-8') if response.data else None
                
                interceptor.log_response(
                    request_id=request_id,
                    status_code=response.status,
                    headers=response_headers,
                    body=response_body,
                    duration_ms=duration_ms
                )
                
                return response
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                if request_id:
                    interceptor.log_response(
                        request_id=request_id,
                        status_code=0,
                        error=str(e),
                        duration_ms=duration_ms
                    )
                raise
        
        urllib3.HTTPConnectionPool.urlopen = intercepted_urlopen
        return True
        
    except ImportError:
        return False


def patch_httpx_library(interceptor: HTTPInterceptor):
    """Monkey-patch httpx to intercept HTTP calls"""
    try:
        import httpx
        original_request = httpx.Client.request
        
        def intercepted_request(self, method, url, **kwargs):
            start_time = time.time()
            request_id = None
            
            try:
                # Log request
                headers = kwargs.get('headers', {})
                body = None
                
                if 'json' in kwargs:
                    body = json.dumps(kwargs['json'])
                elif 'content' in kwargs:
                    body = str(kwargs['content'])
                
                request_id = interceptor.log_request(
                    method=method,
                    url=str(url),
                    headers=headers,
                    body=body
                )
                
                # Make actual request
                response = original_request(self, method, url, **kwargs)
                
                # Log response
                duration_ms = (time.time() - start_time) * 1000
                
                interceptor.log_response(
                    request_id=request_id,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=response.text,
                    duration_ms=duration_ms
                )
                
                return response
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                if request_id:
                    interceptor.log_response(
                        request_id=request_id,
                        status_code=0,
                        error=str(e),
                        duration_ms=duration_ms
                    )
                raise
        
        httpx.Client.request = intercepted_request
        return True
        
    except ImportError:
        return False


def install_interceptor(session_id: str, log_dir: Optional[Path] = None) -> HTTPInterceptor:
    """
    Install HTTP interceptor for the current session
    
    Returns:
        HTTPInterceptor instance
    """
    interceptor = HTTPInterceptor(session_id, log_dir)
    
    # Try to patch all common HTTP libraries
    patched = []
    
    if patch_requests_library(interceptor):
        patched.append('requests')
    
    if patch_urllib3_library(interceptor):
        patched.append('urllib3')
    
    if patch_httpx_library(interceptor):
        patched.append('httpx')
    
    return interceptor
