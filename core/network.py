import random
from curl_cffi import requests

class StealthClient:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]

    def __init__(self, proxy: str = None):
        self.proxy = proxy

    async def get(self, url: str, headers: dict = None, impersonate: str = "chrome110"):
        if not headers: headers = {}
        headers.setdefault("User-Agent", random.choice(self.USER_AGENTS))
        async with requests.AsyncSession() as s:
            return await s.get(url, headers=headers, impersonate=impersonate,
                               proxies={"http": self.proxy, "https": self.proxy} if self.proxy else None,
                               timeout=30)
