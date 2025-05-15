"""
URL health check tool for intent inference.

This module provides a tool for checking the health of URLs
specified in intent specifications.
"""
import re
import asyncio
from typing import Dict, List, Optional
import httpx


async def _check_url_health(url: str, timeout: int = 10) -> str:
    """
    Check the health of a URL asynchronously.
    
    Args:
        url: URL to check
        timeout: Connection timeout in seconds
        
    Returns:
        Health status: "healthy", "unhealthy", or "invalid"
    """
    # Ensure URL has a scheme
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(
                url, 
                timeout=timeout,
                follow_redirects=True
            )
        return "healthy" if response.status_code < 400 else "unhealthy"
    except Exception:
        return "unhealthy"


def normalize_url(url: str) -> str:
    """
    Normalize a URL to ensure it has a scheme.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL
    """
    # Check if it's a domain without scheme
    if not url.startswith(('http://', 'https://')):
        # If it has a slash, it's likely a path, so add https:// prefix
        if '/' in url and not url.startswith('www.'):
            return f"https://{url}"
        # If it's just a domain, add https://www.
        if 'www.' not in url:
            return f"https://www.{url}"
        # If it starts with www., add https:// prefix
        return f"https://{url}"
    return url


async def check_urls_health(urls: List[str]) -> Dict[str, str]:
    """
    Check the health of multiple URLs.
    
    Args:
        urls: List of URLs to check
        
    Returns:
        Dictionary mapping URLs to their health status
    """
    normalized_urls = [normalize_url(url) for url in urls]
    tasks = [_check_url_health(url) for url in normalized_urls]
    results = await asyncio.gather(*tasks)
    
    return {url: result for url, result in zip(urls, results)}


def check_urls_health_sync(urls: List[str]) -> Dict[str, str]:
    """
    Synchronous wrapper for check_urls_health.
    
    Args:
        urls: List of URLs to check
        
    Returns:
        Dictionary mapping URLs to their health status
    """
    return asyncio.run(check_urls_health(urls))
