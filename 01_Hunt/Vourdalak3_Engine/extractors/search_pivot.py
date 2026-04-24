from bs4 import BeautifulSoup
from urllib.parse import quote
from models import Node, Edge, NodeType, EdgeType
from core_loop import BaseExtractor, OperationalPath
from network import StealthClient

class SearchPivotExtractor(BaseExtractor):
    """
    Independent Search Engine Pivot.
    Uses raw search results to find where an identifier (email/username) appears.
    """
    def __init__(self, path: OperationalPath):
        super().__init__(path)
        self.client = StealthClient()

    async def can_handle(self, node: Node) -> bool:
        return node.type in [NodeType.USERNAME, NodeType.EMAIL, NodeType.PHONE]

    async def extract(self, node: Node) -> list[Edge]:
        edges = []
        # Construct a targeted search query
        query = f'"{node.value}"'
        search_url = f"https://duckduckgo.com/html/?q={quote(query)}"
        
        try:
            resp = await self.client.get(search_url)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Extract links from search results
            for result in soup.find_all('a', class_='result__url', href=True):
                href = result['href']
                if 'duckduckgo.com' in href: continue
                
                target_node = Node(NodeType.URL, href)
                edges.append(Edge(node, target_node, EdgeType.LINKED_TO))
                
                # Path B: Devouring - Look for specific platforms of interest
                if self.path == OperationalPath.DEVOURING:
                    if any(x in href.lower() for x in ['tinder', 'bumble', 'badoo', 'okcupid', 'ashleymadison']):
                        edges.append(Edge(node, target_node, EdgeType.MENTIONED, metadata={"flag": "dating_profile_detected"}))
                
                # Path C: Resurrection - Look for support forums, self-help, or positive activity
                if self.path == OperationalPath.RESURRECTION:
                    if any(x in href.lower() for x in ['forum', 'support', 'help', 'community']):
                        edges.append(Edge(node, target_node, EdgeType.LINKED_TO, metadata={"flag": "support_network_indicator"}))

        except Exception:
            pass

        return edges
