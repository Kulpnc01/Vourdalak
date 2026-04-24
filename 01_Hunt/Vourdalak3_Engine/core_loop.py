import asyncio
import enum
import logging
from typing import List, Set, Type, Optional
from models import Node, Edge, NodeType, EdgeType
from db import GraphDB

class OperationalPath(enum.Enum):
    INGESTION = "ingestion"      # Path A: Learn everything
    DEVOURING = "devouring"      # Path B: Dark Tetrad / Infidelity / Deceit
    RESURRECTION = "resurrection" # Path C: Correction / Support / Vulnerability

class BaseExtractor:
    """Base class for all independent extractors."""
    def __init__(self, path: OperationalPath):
        self.path = path

    async def can_handle(self, node: Node) -> bool:
        raise NotImplementedError

    async def extract(self, node: Node) -> List[Edge]:
        raise NotImplementedError

class VourdalakEngine:
    def __init__(self, path: OperationalPath, db_path: str = "vourdalak_graph.db"):
        self.path = path
        self.db = GraphDB(db_path)
        self.queue = asyncio.Queue()
        self.visited: Set[str] = set()
        self.extractors: List[BaseExtractor] = []
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("VourdalakEngine")

    def register_extractor(self, extractor_cls: Type[BaseExtractor]):
        self.extractors.append(extractor_cls(self.path))
        self.logger.info(f"Registered extractor: {extractor_cls.__name__} for Path: {self.path.value}")

    async def add_seed(self, node: Node):
        self.logger.info(f"Adding seed node: {node.type.value}:{node.value}")
        await self.queue.put(node)

    async def run(self, max_depth: int = 3):
        self.logger.info(f"Starting Vourdalak 3.0 Engine in {self.path.value} mode...")
        
        depth = 0
        while not self.queue.empty() and depth < max_depth:
            # Current level size
            level_size = self.queue.qsize()
            self.logger.info(f"Processing Depth {depth} | Nodes in Queue: {level_size}")
            
            tasks = []
            for _ in range(level_size):
                node = await self.queue.get()
                node_id = f"{node.type.value}:{node.value}"
                
                if node_id in self.visited:
                    self.queue.task_done()
                    continue
                
                self.visited.add(node_id)
                self.db.upsert_node(node)
                
                # Run applicable extractors
                for extractor in self.extractors:
                    if await extractor.can_handle(node):
                        tasks.append(self._run_extractor(extractor, node))
            
            if tasks:
                # Run extractors concurrently for this level
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception):
                        self.logger.error(f"Extractor failure: {res}")
                    elif res:
                        for edge in res:
                            self.db.upsert_edge(edge)
                            # Push new target node if not visited
                            target_id = f"{edge.target.type.value}:{edge.target.value}"
                            if target_id not in self.visited:
                                await self.queue.put(edge.target)

            depth += 1
            
        self.logger.info("Intelligence acquisition complete.")

    async def _run_extractor(self, extractor: BaseExtractor, node: Node) -> List[Edge]:
        self.logger.info(f" [*] {extractor.__class__.__name__} -> {node.value}")
        try:
            return await extractor.extract(node)
        except Exception as e:
            self.logger.error(f" [!] Error in {extractor.__class__.__name__} on {node.value}: {e}")
            return []

if __name__ == "__main__":
    # Example usage
    async def main():
        engine = VourdalakEngine(OperationalPath.INGESTION)
        # engine.register_extractor(SomeExtractor)
        await engine.add_seed(Node(NodeType.USERNAME, "matt_hersey925"))
        await engine.run()

    asyncio.run(main())
