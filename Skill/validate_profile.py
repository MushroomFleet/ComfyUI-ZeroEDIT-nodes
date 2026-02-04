#!/usr/bin/env python3
"""
validate_profile.py - Validate ZeroEDIT JSON profiles

Checks:
- Valid JSON syntax
- Required fields present (name, description, version, templates, pools)
- All template placeholders reference existing pools
- No empty pools
- No duplicate entries within pools
- Templates produce valid output

Usage:
    python validate_profile.py <profile.json>
    python validate_profile.py <profile.json> --test-output
"""

import json
import re
import sys
from pathlib import Path


def load_profile(path: str) -> dict:
    """Load and parse JSON profile."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_structure(profile: dict) -> list[str]:
    """Validate required fields and structure."""
    errors = []
    
    required_fields = ['name', 'description', 'version', 'templates', 'pools']
    for field in required_fields:
        if field not in profile:
            errors.append(f"Missing required field: '{field}'")
    
    if 'templates' in profile:
        if not isinstance(profile['templates'], list):
            errors.append("'templates' must be a list")
        elif len(profile['templates']) == 0:
            errors.append("'templates' cannot be empty")
    
    if 'pools' in profile:
        if not isinstance(profile['pools'], dict):
            errors.append("'pools' must be a dictionary")
    
    return errors


def validate_pools(profile: dict) -> list[str]:
    """Validate pool contents."""
    errors = []
    pools = profile.get('pools', {})
    
    for pool_name, pool_items in pools.items():
        # Check for empty pools
        if not pool_items:
            errors.append(f"Pool '{pool_name}' is empty")
            continue
        
        # Check for non-list pools
        if not isinstance(pool_items, list):
            errors.append(f"Pool '{pool_name}' must be a list")
            continue
        
        # Check for duplicates
        seen = set()
        for item in pool_items:
            item_lower = item.lower() if isinstance(item, str) else str(item)
            if item_lower in seen:
                errors.append(f"Duplicate entry in pool '{pool_name}': '{item}'")
            seen.add(item_lower)
        
        # Check for empty strings
        for i, item in enumerate(pool_items):
            if isinstance(item, str) and item.strip() == '':
                errors.append(f"Empty string at index {i} in pool '{pool_name}'")
    
    return errors


def validate_templates(profile: dict) -> list[str]:
    """Validate template placeholders reference existing pools."""
    errors = []
    templates = profile.get('templates', [])
    pools = profile.get('pools', {})
    pool_names = set(pools.keys())
    
    # Pattern to find {placeholder} references
    placeholder_pattern = re.compile(r'\{(\w+)\}')
    
    for i, template in enumerate(templates):
        if not isinstance(template, str):
            errors.append(f"Template at index {i} is not a string")
            continue
        
        placeholders = placeholder_pattern.findall(template)
        
        for placeholder in placeholders:
            if placeholder not in pool_names:
                errors.append(
                    f"Template {i} references undefined pool '{placeholder}'"
                )
    
    return errors


def calculate_combinations(profile: dict) -> int:
    """Calculate total unique combinations."""
    total = len(profile.get('templates', []))
    for pool in profile.get('pools', {}).values():
        total *= len(pool)
    return total


def generate_test_output(profile: dict, seed: int = 42, count: int = 5) -> list[str]:
    """Generate test outputs using simple hash simulation."""
    import hashlib
    
    templates = profile.get('templates', [])
    pools = profile.get('pools', {})
    outputs = []
    
    for idx in range(count):
        # Simple deterministic selection
        hash_input = f"{seed}-{idx}-0".encode()
        template_idx = int(hashlib.md5(hash_input).hexdigest(), 16) % len(templates)
        template = templates[template_idx]
        
        # Fill in placeholders
        components = {}
        for i, (pool_name, pool_items) in enumerate(pools.items()):
            hash_input = f"{seed}-{idx}-{i+1}".encode()
            item_idx = int(hashlib.md5(hash_input).hexdigest(), 16) % len(pool_items)
            components[pool_name] = pool_items[item_idx]
        
        try:
            output = template.format(**components)
            outputs.append(output)
        except KeyError as e:
            outputs.append(f"[ERROR: Missing pool {e}]")
    
    return outputs


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_profile.py <profile.json> [--test-output]")
        sys.exit(1)
    
    profile_path = sys.argv[1]
    test_output = '--test-output' in sys.argv
    
    print(f"Validating: {profile_path}")
    print("=" * 60)
    
    # Load profile
    try:
        profile = load_profile(profile_path)
    except json.JSONDecodeError as e:
        print(f"❌ INVALID JSON: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ FILE NOT FOUND: {profile_path}")
        sys.exit(1)
    
    # Run validations
    all_errors = []
    
    print("\n[Structure Validation]")
    errors = validate_structure(profile)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print("  ✓ All required fields present")
    
    print("\n[Pool Validation]")
    errors = validate_pools(profile)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print("  ✓ All pools valid")
    
    print("\n[Template Validation]")
    errors = validate_templates(profile)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print("  ✓ All template references valid")
    
    # Statistics
    print("\n[Profile Statistics]")
    print(f"  Name: {profile.get('name', 'N/A')}")
    print(f"  Version: {profile.get('version', 'N/A')}")
    print(f"  Templates: {len(profile.get('templates', []))}")
    print(f"  Pools: {len(profile.get('pools', {}))}")
    
    for pool_name, pool_items in profile.get('pools', {}).items():
        print(f"    - {pool_name}: {len(pool_items)} entries")
    
    total = calculate_combinations(profile)
    print(f"  Total combinations: {total:,} ({total:.2e})")
    
    # Test output
    if test_output and not all_errors:
        print("\n[Test Outputs (seed=42, indices 0-4)]")
        outputs = generate_test_output(profile)
        for i, output in enumerate(outputs):
            words = len(output.split())
            print(f"\n  [{i}] ({words} words)")
            print(f"  {output[:200]}{'...' if len(output) > 200 else ''}")
    
    # Final result
    print("\n" + "=" * 60)
    if all_errors:
        print(f"❌ VALIDATION FAILED: {len(all_errors)} error(s)")
        sys.exit(1)
    else:
        print("✓ VALIDATION PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
