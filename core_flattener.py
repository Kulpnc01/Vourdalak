import os
from pathlib import Path

def flatten_project(root_path, output_file, ignore_dirs=None, ignore_exts=None):
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', 'vourdalak_env', '01_Hunt/Input', '02_Feed', 'output', '03_Devour', 'sherlock', 'Vourdalak_3_3', 'Vourdalak_dead'}
    if ignore_exts is None:
        ignore_exts = {'.pyc', '.exe', '.zip', '.tar.gz', '.png', '.jpg', '.pdf', '.jsonl'}

    root = Path(root_path)
    print(f"[*] FLATTENING: {root.name} -> {output_file}")

    with open(output_file, 'w', encoding='utf-8') as out:
        # 1. Write Directory Tree Overview
        out.write(f"# PROJECT ARCHITECTURE: {root.name}\n")
        out.write("```text\n")
        for p in sorted(root.rglob('*')):
            # Check if path should be ignored
            rel_path = p.relative_to(root)
            if any(id_dir in str(rel_path) for id_dir in ignore_dirs): continue
            
            depth = len(p.parts) - len(root.parts)
            indent = "  " * depth
            out.write(f"{indent}{p.name}{'/' if p.is_dir() else ''}\n")
        out.write("```\n\n")

        # 2. Write File Contents
        for p in sorted(root.rglob('*')):
            if p.is_dir(): continue
            
            rel_path = p.relative_to(root)
            
            # Skip ignores
            if any(id_dir in str(rel_path) for id_dir in ignore_dirs): continue
            if p.suffix.lower() in ignore_exts: continue
            if p.name == output_file: continue

            print(f"  > Adding: {rel_path}")
            out.write(f"## FILE: {rel_path}\n")
            out.write(f"```{p.suffix.replace('.', '')}\n")
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"ERROR READING FILE: {e}")
            out.write("\n```\n\n")

    print(f"[SUCCESS] Flattened map saved to: {output_file}")

if __name__ == "__main__":
    # Flatten Vourdalak 2.0
    flatten_project('C:/HDT/Vourdalak2.0', 'Vourdalak_Logic_Map.md')
    
    # Flatten EgoWeaver 2.0
    flatten_project('C:/HDT/EgoWeaver2.0', 'EgoWeaver_Logic_Map.md')
