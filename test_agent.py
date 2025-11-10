#!/usr/bin/env python3
"""
Test Agent - Demonstrates HTTP Interception
Makes various API calls to test the HTTP interceptor
"""

import requests
import time
import json

def test_openai_api():
    """Simulate OpenAI API call"""
    print("Testing OpenAI API...")
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': 'Bearer sk-test-key-12345',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4',
                'messages': [{'role': 'user', 'content': 'Hello!'}]
            },
            timeout=5
        )
    except Exception as e:
        print(f"Expected error: {e}")

def test_anthropic_api():
    """Simulate Anthropic API call"""
    print("Testing Anthropic API...")
    try:
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': 'sk-ant-test-key',
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'claude-3-sonnet-20240229',
                'messages': [{'role': 'user', 'content': 'Hello!'}],
                'max_tokens': 100
            },
            timeout=5
        )
    except Exception as e:
        print(f"Expected error: {e}")

def test_generic_api():
    """Make a generic API call"""
    print("Testing generic API...")
    try:
        response = requests.get('https://api.github.com/users/github', timeout=5)
        print(f"GitHub API Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("🤖 Test Agent Starting...")
    print("Making various HTTP requests...\n")
    
    test_openai_api()
    time.sleep(0.5)
    
    test_anthropic_api()
    time.sleep(0.5)
    
    test_generic_api()
    
    print("\n✓ Test agent completed")
    print("Check 'sudodog http' to see logged requests!")

if __name__ == '__main__':
    main()
