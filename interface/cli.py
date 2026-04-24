import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parents[1]))

from core.models import Node, NodeType
from modules.okhotnik.engine import OkhotnikEngine
from modules.smotrityel.engine import Smotrityel
from modules.feed.engine import FeedEngine

def main():
    parser = argparse.ArgumentParser(description="Vourdalak v3 Modular Interface")
    parser.add_argument("--target", help="Seed identifier")
    parser.add_argument("--type", default="username", help="Identifier type")
    parser.add_argument("--path", choices=["A", "B", "C"], help="Operational Path")
    parser.add_argument("--gui", action="store_true", help="Launch GUI")
    
    args = parser.parse_args()

    if args.gui:
        print("[*] Launching Graphical Interface...")
        # GUI import here...
        return

    if args.target:
        print(f"[*] Starting Modular Hunt for {args.target}...")
        # Sequential Execution Logic
        # 1. Okhotnik (Acquisition)
        # 2. Smotrityel (Normalization)
        # 3. Feed (Path Implementation)
        pass

if __name__ == "__main__":
    main()
