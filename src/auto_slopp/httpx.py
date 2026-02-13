"""Console script for httpx functionality."""

import httpx


def main() -> None:
    """Run httpx console script to test HTTP requests."""
    client = httpx.Client()
    try:
        response = client.get("https://httpbin.org/get")
        print(f"Status: {response.status_code}")
    finally:
        client.close()
