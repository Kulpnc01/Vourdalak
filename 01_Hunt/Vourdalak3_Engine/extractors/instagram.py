import json
import re
from bs4 import BeautifulSoup
from models import Node, Edge, NodeType, EdgeType
from core_loop import BaseExtractor, OperationalPath
from network import StealthClient

class InstagramStealthExtractor(BaseExtractor):
    """
    Independent Instagram Extractor.
    Uses curl_cffi to bypass TLS fingerprinting.
    """
    def __init__(self, path: OperationalPath):
        super().__init__(path)
        self.client = StealthClient()

    async def can_handle(self, node: Node) -> bool:
        return node.type == NodeType.USERNAME

    async def extract(self, node: Node) -> list[Edge]:
        edges = []
        url = f"https://www.instagram.com/{node.value}/"
        
        try:
            resp = await self.client.get(url)
            # Instagram often returns 200 but sends a login redirect in the HTML
            if resp.status_code != 200:
                return []

            if "login" in resp.url and "/accounts/login/" in resp.url:
                # Blocked or redirect to login
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Extract Meta description which often contains follower count and bio
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                content = meta_desc['content']
                node.metadata["ig_meta"] = content
                
                # Extract counts using regex
                # Example: "1,234 Followers, 567 Following, 89 Posts..."
                counts = re.findall(r'([\d,]+)\s+(Followers|Following|Posts)', content)
                for count, label in counts:
                    node.metadata[label.lower()] = count.replace(',', '')

            # Path B: Devouring - Look for infidelity/secret account markers
            if self.path == OperationalPath.DEVOURING:
                # Check for "private", "backup", or "secret" in bio keywords if possible
                title = soup.find('title')
                if title and any(x in title.text.lower() for x in ['private', 'backup']):
                    edges.append(Edge(node, node, EdgeType.MENTIONED, metadata={"flag": "hidden_account_indicator"}))

            # Extract any other social handles mentioned in the title/meta
            # (Instagram HTML is mostly JS-rendered, so we are limited without Playwright)
            
        except Exception:
            pass

        return edges
