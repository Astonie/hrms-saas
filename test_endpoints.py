#!/usr/bin/env python3
"""Quick endpoint smoke test script."""
import requests

endpoints = [
    'http://127.0.0.1:8000/api/v1/',
    'http://127.0.0.1:8000/api/v1/auth/me',
    'http://127.0.0.1:8000/api/v1/tenants/subscription-plans',
    'http://127.0.0.1:8000/health',
]

for url in endpoints:
    try:
        response = requests.get(url, timeout=5)
        print(f"\n{url}")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
    except Exception as e:
        print(f"\n{url}")
        print(f"Error: {e}")
