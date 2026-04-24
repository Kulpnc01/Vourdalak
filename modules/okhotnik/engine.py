import asyncio
import logging
from typing import List, Set, Type
from core.models import Node, Edge, NodeType
from core.database import GraphDB

class OkhotnikEngine:
    def __init__(self, db_path: str = "vourdalak_v3.db"):
        self.db = GraphDB(db_path)
        self.queue = asyncio.Queue()
        self.visited: Set[str] = set()
        self.extractors = []
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("Okhotnik")

    async def add_seed(self, node: Node):
        await self.queue.put(node)

    async def run(self, max_depth: int = 3):
        depth = 0
        while not self.queue.empty() and depth < max_depth:
            qsize = self.queue.qsize()
            for _ in range(qsize):
                node = await self.queue.get()
                node_id = f"{node.type.value}:{node.value}"
                if node_id in self.visited: continue
                self.visited.add(node_id)
                self.db.upsert_node(node)
                # Extractor logic here...
            depth += 1
