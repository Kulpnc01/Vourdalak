import re
from bs4 import BeautifulSoup
from models import Node, Edge, NodeType, EdgeType
from core_loop import BaseExtractor, OperationalPath
from network import StealthClient

class GithubExtractor(BaseExtractor):
    def __init__(self, path: OperationalPath):
        super().__init__(path)
        self.client = StealthClient()

    async def can_handle(self, node: Node) -> bool:
        return node.type == NodeType.USERNAME

    async def extract(self, node: Node) -> list[Edge]:
        edges = []
        url = f"https://github.com/{node.value}"
        
        try:
            resp = await self.client.get(url)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 1. Identify Identity Node (Full Name)
            name_elem = soup.find('span', class_='p-name')
            if name_elem:
                name = name_elem.text.strip()
                identity_node = Node(NodeType.IDENTITY, name)
                edges.append(Edge(node, identity_node, EdgeType.OWNED_BY))

            # 2. Extract Social Links (URLs)
            # GitHub lists blog/website and other social accounts in the sidebar
            sidebar = soup.find('div', class_='js-profile-editable-area')
            if sidebar:
                # Find all links in the sidebar
                links = sidebar.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if 'mailto:' in href:
                        email = href.replace('mailto:', '').strip()
                        target_node = Node(NodeType.EMAIL, email)
                        edges.append(Edge(node, target_node, EdgeType.LINKED_TO))
                    elif 'twitter.com' in href:
                        user = href.split('/')[-1]
                        target_node = Node(NodeType.USERNAME, user)
                        edges.append(Edge(node, target_node, EdgeType.LINKED_TO))
                    elif href.startswith('http'):
                        target_node = Node(NodeType.URL, href)
                        edges.append(Edge(node, target_node, EdgeType.LINKED_TO))

            # Path B: Devouring - Look for toxic markers or hidden connections
            if self.path == OperationalPath.DEVOURING:
                # Analyze bio for specific keywords
                bio = soup.find('div', class_='p-note')
                if bio:
                    content = bio.text.lower()
                    # Logic to flag "dark tetrad" markers in bio could go here
                    if any(x in content for x in ['manipulate', 'chaos', 'ego']):
                        edges.append(Edge(node, node, EdgeType.MENTIONED, metadata={"flag": "dark_tetrad_marker"}))

        except Exception as e:
            # Logger is available in the engine, but we could add one here too
            pass

        return edges
