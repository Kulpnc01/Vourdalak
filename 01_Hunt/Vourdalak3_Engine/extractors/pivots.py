from models import Node, Edge, NodeType, EdgeType
from core_loop import BaseExtractor, OperationalPath
from network import StealthClient

class BreachEmulatorExtractor(BaseExtractor):
    """
    Simulated Breach Data Pivot.
    In a production Vourdalak 3.0, this would query a local 
    Elasticsearch instance containing leaked credential dumps.
    """
    def __init__(self, path: OperationalPath):
        super().__init__(path)
        self.client = StealthClient()

    async def can_handle(self, node: Node) -> bool:
        # We pivot on emails and usernames
        return node.type in [NodeType.EMAIL, NodeType.USERNAME]

    async def extract(self, node: Node) -> list[Edge]:
        edges = []
        
        # Path B: Devouring - This path is the most aggressive with credentials
        if self.path == OperationalPath.DEVOURING:
            # Placeholder for actual breach lookup logic
            # This would yield nodes of type CREDENTIAL
            pass

        return edges

class IdentityPivotExtractor(BaseExtractor):
    """
    Expands an IDENTITY (Full Name) into potential USERNAME nodes.
    """
    def __init__(self, path: OperationalPath):
        super().__init__(path)
        
    async def can_handle(self, node: Node) -> bool:
        return node.type == NodeType.IDENTITY

    async def extract(self, node: Node) -> list[Edge]:
        edges = []
        full_name = node.value
        parts = full_name.split()
        
        if len(parts) >= 2:
            first = parts[0].lower()
            last = parts[-1].lower()
            
            # Generate common username patterns
            variations = [
                f"{first}{last}",
                f"{first}_{last}",
                f"{first}.{last}",
                f"{first[0]}{last}",
                f"{first}{last[0]}"
            ]
            
            for v in variations:
                username_node = Node(NodeType.USERNAME, v)
                edges.append(Edge(node, username_node, EdgeType.OWNED_BY))
                
        return edges
