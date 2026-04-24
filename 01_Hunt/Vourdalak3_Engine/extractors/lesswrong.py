import json
from bs4 import BeautifulSoup
from models import Node, Edge, NodeType, EdgeType
from core_loop import BaseExtractor, OperationalPath
from network import StealthClient

class LessWrongExtractor(BaseExtractor):
    def __init__(self, path: OperationalPath):
        super().__init__(path)
        self.client = StealthClient()

    async def can_handle(self, node: Node) -> bool:
        return node.type == NodeType.USERNAME

    async def extract(self, node: Node) -> list[Edge]:
        edges = []
        # LessWrong users can be found at /users/username
        url = f"https://www.lesswrong.com/users/{node.value}"
        
        try:
            resp = await self.client.get(url)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # LessWrong often embeds data in a JSON script tag or structured HTML
            # Let's look for common indicators
            
            # 1. Identity variation
            display_name = soup.find('h1')
            if display_name:
                name = display_name.text.strip()
                if name != node.value:
                    identity_node = Node(NodeType.IDENTITY, name)
                    edges.append(Edge(node, identity_node, EdgeType.OWNED_BY))

            # 2. Path A: Ingestion - Extract full bio for predictive modeling
            if self.path == OperationalPath.INGESTION:
                bio_elem = soup.find('div', class_='UserPage-bio')
                if bio_elem:
                    bio_text = bio_elem.text.strip()
                    # Store bio in metadata for the predictive engine
                    node.metadata["bio"] = bio_text

            # 3. Path B: Devouring - Analyze karma and posts for Dark Tetrad traits
            # LessWrong users with very high karma but highly adversarial comments
            karma_elem = soup.find('div', class_='UserPage-karma')
            if karma_elem:
                try:
                    karma = int(karma_elem.text.replace(',', '').strip())
                    node.metadata["karma"] = karma
                except: pass

            # 4. Extract linked social accounts
            # These are often in a specific sidebar or listed in the bio
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'twitter.com' in href:
                    user = href.split('/')[-1]
                    target_node = Node(NodeType.USERNAME, user)
                    edges.append(Edge(node, target_node, EdgeType.LINKED_TO))
                elif 'github.com' in href:
                    user = href.split('/')[-1]
                    target_node = Node(NodeType.USERNAME, user)
                    edges.append(Edge(node, target_node, EdgeType.LINKED_TO))

        except Exception as e:
            pass

        return edges
