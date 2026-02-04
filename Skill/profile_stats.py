#!/usr/bin/env python3
"""
profile_stats.py - Display ZeroEDIT profile statistics and generate samples

Usage:
    python profile_stats.py <profile.json>
    python profile_stats.py <profile.json> --samples 10
    python profile_stats.py <profile.json> --seed 12345
"""

import json
import struct
import sys
from pathlib import Path

try:
    import xxhash
    HAS_XXHASH = True
except ImportError:
    HAS_XXHASH = False
    import hashlib


def load_profile(path: str) -> dict:
    """Load JSON profile."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def hash_coords(seed: int, *coords: int) -> int:
    """Hash seed + coordinates for deterministic selection."""
    if HAS_XXHASH:
        h = xxhash.xxh32(seed=seed & 0xFFFFFFFF)
        h.update(struct.pack('<' + 'i' * len(coords), *coords))
        return h.intdigest()
    else:
        # Fallback to hashlib
        data = f"{seed}:" + ":".join(str(c) for c in coords)
        return int(hashlib.md5(data.encode()).hexdigest(), 16)


def generate_prompt(seed: int, idx: int, profile: dict) -> str:
    """Generate a single prompt from seed and index."""
    templates = profile['templates']
    pools = profile['pools']
    
    # Select template
    template_hash = hash_coords(seed, idx, 0)
    template = templates[template_hash % len(templates)]
    
    # Select components
    components = {}
    for i, (key, pool) in enumerate(pools.items()):
        comp_hash = hash_coords(seed, idx, i + 1)
        components[key] = pool[comp_hash % len(pool)]
    
    try:
        return template.format(**components)
    except KeyError:
        # Partial formatting fallback
        for key in pools.keys():
            template = template.replace(f"{{{key}}}", components.get(key, f"[{key}]"))
        return template


def calculate_combinations(profile: dict) -> int:
    """Calculate total unique combinations."""
    total = len(profile.get('templates', []))
    for pool in profile.get('pools', {}).values():
        total *= len(pool)
    return total


def main():
    if len(sys.argv) < 2:
        print("Usage: python profile_stats.py <profile.json> [--samples N] [--seed S]")
        sys.exit(1)
    
    profile_path = sys.argv[1]
    
    # Parse arguments
    num_samples = 5
    seed = 42
    
    for i, arg in enumerate(sys.argv):
        if arg == '--samples' and i + 1 < len(sys.argv):
            num_samples = int(sys.argv[i + 1])
        if arg == '--seed' and i + 1 < len(sys.argv):
            seed = int(sys.argv[i + 1])
    
    # Load profile
    try:
        profile = load_profile(profile_path)
    except Exception as e:
        print(f"Error loading profile: {e}")
        sys.exit(1)
    
    # Display statistics
    print("=" * 70)
    print("ZEROEDIT PROFILE STATISTICS")
    print("=" * 70)
    print(f"File: {profile_path}")
    print(f"Name: {profile.get('name', 'N/A')}")
    print(f"Description: {profile.get('description', 'N/A')}")
    print(f"Version: {profile.get('version', 'N/A')}")
    print()
    
    print("Pool Sizes:")
    for pool_name, pool_items in profile.get('pools', {}).items():
        print(f"  {pool_name}: {len(pool_items)} entries")
    print(f"  templates: {len(profile.get('templates', []))}")
    print()
    
    total = calculate_combinations(profile)
    print(f"Total unique combinations: {total:,}")
    print(f"Scientific notation: {total:.2e}")
    print()
    
    # Generate samples
    print("=" * 70)
    print(f"SAMPLE OUTPUTS (seed={seed}, indices 0-{num_samples-1})")
    print("=" * 70)
    
    for i in range(num_samples):
        prompt = generate_prompt(seed, i, profile)
        words = len(prompt.split())
        print(f"\n[{i}] ({words} words)")
        print(prompt)
    
    # Determinism check
    print()
    print("=" * 70)
    print("DETERMINISM CHECK")
    print("=" * 70)
    p1 = generate_prompt(seed, 1000, profile)
    p2 = generate_prompt(seed, 1000, profile)
    match = p1 == p2
    print(f"seed={seed}, idx=1000: {'✓ MATCH' if match else '✗ MISMATCH'}")
    
    if not HAS_XXHASH:
        print("\nNote: xxhash not installed, using hashlib fallback.")
        print("Install xxhash for full compatibility: pip install xxhash")


if __name__ == "__main__":
    main()
