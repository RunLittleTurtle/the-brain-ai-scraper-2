"""
URL validation utilities for intent inference.

This module provides functions for validating and checking the health of URLs
identified in an intent specification.
"""
from typing import Dict, Any, List, Tuple
import asyncio
import re
from urllib.parse import urlparse
import httpx


async def check_url_health(url: str) -> Tuple[str, str]:
    """
    Perform basic health check on a URL.
    
    Args:
        url: The URL to check
        
    Returns:
        A tuple of (url, status) where status is one of:
        - "healthy": URL is accessible
        - "unreachable": URL cannot be reached
        - "invalid": URL is not properly formatted
    """
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    # Validate URL format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return url, "invalid"
    except Exception:
        return url, "invalid"
    
    # Check if URL is reachable
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.head(url)
            if response.status_code < 400:
                return url, "healthy"
            else:
                return url, "unreachable"
    except Exception:
        return url, "unreachable"


async def validate_urls(urls: List[str]) -> Dict[str, str]:
    """
    Validate a list of URLs concurrently.
    
    Args:
        urls: List of URLs to validate
        
    Returns:
        Dictionary mapping each URL to its health status
    """
    tasks = [check_url_health(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return {url: status for url, status in results}


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract URLs from text using regex pattern matching.
    
    Args:
        text: Text that may contain URLs
        
    Returns:
        List of extracted URLs
    """
    # Basic URL regex pattern
    url_pattern = r'https?://[^\s()<>]+|(?:www\.[^\s()<>]+)'
    
    # Find all matches
    matches = re.findall(url_pattern, text)
    
    # Ensure all URLs have schemes
    normalized_urls = []
    for url in matches:
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        normalized_urls.append(url)
    
    return normalized_urls


def normalize_url(url: str) -> str:
    """
    Normalize a URL by ensuring it has a scheme.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL with scheme
    """
    if not url.startswith(('http://', 'https://')):
        return f"https://{url}"
    return url
