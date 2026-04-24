import random
import asyncio
from curl_cffi import requests

class StealthClient:
    """Shared network client designed to bypass TLS fingerprinting."""
    
    # Common 2026 User Agents
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    def __init__(self, proxy: str = None):
        self.proxy = proxy

    async def get(self, url: str, headers: dict = None, impersonate: str = "chrome110"):
        if not headers:
            headers = {}
        
        headers.setdefault("User-Agent", random.choice(self.USER_AGENTS))
        headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8")
        headers.setdefault("Accept-Language", "en-US,en;q=0.5")
        
        # Use curl_cffi's async implementation
        # Note: curl_cffi.requests.AsyncSession is preferred for multiple requests
        # but for individual calls we can use the top level async methods if available 
        # or wrap the synchronous one if necessary. 
        # Actually, curl_cffi provides an AsyncSession.
        
        async with requests.AsyncSession() as s:
            response = await s.get(
                url, 
                headers=headers, 
                impersonate=impersonate,
                proxies={"http": self.proxy, "https": self.proxy} if self.proxy else None,
                timeout=30
            )
            return response

    async def post(self, url: str, data: any = None, json: any = None, headers: dict = None, impersonate: str = "chrome110"):
        if not headers:
            headers = {}
        
        headers.setdefault("User-Agent", random.choice(self.USER_AGENTS))
        
        async with requests.AsyncSession() as s:
            response = await s.post(
                url, 
                data=data,
                json=json,
                headers=headers, 
                impersonate=impersonate,
                proxies={"http": self.proxy, "https": self.proxy} if self.proxy else None,
                timeout=30
            )
            return response
