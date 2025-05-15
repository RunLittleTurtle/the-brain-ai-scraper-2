"""
URL health checking tools for the intent inference graph.

This module provides the check_urls_health_sync function which checks the health
of a list of URLs by making HTTP HEAD requests.
"""
from typing import Dict, List
import httpx
from urllib.parse import urlparse


def check_urls_health_sync(urls: List[str]) -> Dict[str, str]:
    """
    Check the health of a list of URLs synchronously.
    
    Args:
        urls: List of URLs to check
    
    Returns:
        Dictionary mapping URLs to health status ("healthy" or "unhealthy")
    """
    results = {}
    
    # Process each URL
    for url in urls:
        # Make sure URL has a scheme
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = f"https://{url}"
        
        try:
            # Set a reasonable timeout to avoid long waits
            with httpx.Client(timeout=5.0, follow_redirects=True) as client:
                # Use HEAD request to avoid downloading full content
                response = client.head(url)
                
                # Consider 2xx and 3xx responses as healthy
                if 200 <= response.status_code < 400:
                    results[url] = "healthy"
                else:
                    results[url] = "unhealthy"
        except Exception as e:
            # Any exception means the URL is unhealthy
            results[url] = "unhealthy"
    
    return results
