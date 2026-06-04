#!/usr/bin/env python3
"""Split sites into chunks for parallel processing in GitHub Actions."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITES_DIR = ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
SITE_PROFILES_PATH = ROOT / "config" / "site_profiles.json"

def discover_site_names() -> list[str]:
    names = []
    for file_path in sorted(SITES_DIR.glob("*.py")):
        name = file_path.stem
        if name in {"__init__", "soup_spec"}:
            continue
        names.append(name)
    return names

def load_profiles() -> dict[str, Any]:
    if not SITE_PROFILES_PATH.exists():
        return {}
    return json.loads(SITE_PROFILES_PATH.read_text(encoding="utf-8"))

def main():
    sites = discover_site_names()

    # Priority grouping: Tier 1 always together in chunk 0? 
    # Or just distribute everything.
    # Let's group by tier first to ensure Tier 1 sites are distributed or isolated.
    
    # Actually, a simple split is usually best for load balancing.
    # But we might want to run Tier 1 sites first or in a specific chunk.
    
    num_chunks = 4
    chunks = [[] for _ in range(num_chunks)]
    
    # Distribute sites across chunks
    for i, site in enumerate(sites):
        chunks[i % num_chunks].append(site)
        
    matrix = {"include": []}
    for i, chunk_sites in enumerate(chunks):
        matrix["include"].append({
            "chunk": i + 1,
            "sites": " ".join(chunk_sites)
        })
        
    print(json.dumps(matrix))

if __name__ == "__main__":
    main()
