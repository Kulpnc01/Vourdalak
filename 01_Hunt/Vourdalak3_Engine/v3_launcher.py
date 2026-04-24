import asyncio
import argparse
import sys
from pathlib import Path

# Add current directory to path so we can import modules
sys.path.append(str(Path(__file__).parent))

from core_loop import VourdalakEngine, OperationalPath
from models import Node, NodeType
from extractors import EXTRACTORS

async def run_v3_hunt(seed_value: str, seed_type: str, path: str, depth: int):
    # Map string path to Enum
    path_map = {
        "A": OperationalPath.INGESTION,
        "B": OperationalPath.DEVOURING,
        "C": OperationalPath.RESURRECTION
    }
    
    op_path = path_map.get(path.upper(), OperationalPath.INGESTION)
    
    # Map string type to Enum
    type_map = {
        "username": NodeType.USERNAME,
        "email": NodeType.EMAIL,
        "phone": NodeType.PHONE,
        "url": NodeType.URL,
        "identity": NodeType.IDENTITY
    }
    node_type = type_map.get(seed_type.lower(), NodeType.USERNAME)
    
    engine = VourdalakEngine(op_path)
    
    # Register all extractors
    for ext_cls in EXTRACTORS:
        engine.register_extractor(ext_cls)
        
    # Add initial seed
    await engine.add_seed(Node(node_type, seed_value))
    
    # Run the engine
    await engine.run(max_depth=depth)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vourdalak 3.0: Recursive Intelligence Engine")
    parser.add_argument("--seed", required=True, help="Initial point of contact (e.g., username or email)")
    parser.add_argument("--type", default="username", choices=["username", "email", "phone", "url", "identity"], help="Type of seed")
    parser.add_argument("--path", default="A", choices=["A", "B", "C"], help="Operational Path (A: Ingestion, B: Devouring, C: Resurrection)")
    parser.add_argument("--depth", type=int, default=3, help="Recursion depth limit")
    
    args = parser.parse_args()
    
    print("==================================================")
    print(f"  VOURDALAK 3.0: RECURSIVE ENGINE ACTIVATED       ")
    print(f"  Mode: {args.path} | Seed: {args.seed} ({args.type})")
    print("==================================================\n")
    
    asyncio.run(run_v3_hunt(args.seed, args.type, args.path, args.depth))
