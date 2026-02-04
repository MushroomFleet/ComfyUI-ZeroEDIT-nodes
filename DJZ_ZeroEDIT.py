"""
DJZ-ZeroEDIT - Procedural Semantic EDIT Prompt Generation with JSON Profiles
ComfyUI Custom Node using ZeroBytes Position-is-Seed Methodology

Generates infinite deterministic EDIT prompts using O(1) coordinate hashing.
Same (seed, prompt_index, profile) → same edit prompt, always, everywhere.

Based on DJZ-ZeroPrompt-V2 architecture, specialized for image editing operations.
Edit prompts follow the pattern: action + target + integration + preservation

Features:
- JSON profile support for customizable edit vocabulary pools
- Auto-discovery of custom profiles in /profiles/edit/ directory
- Profile-specific prompt statistics
- Edit-specific template structures with preservation clauses
"""

import json
import os
import struct
from pathlib import Path

try:
    import xxhash
except ImportError:
    raise ImportError(
        "DJZ-ZeroEDIT requires xxhash. Install with: pip install xxhash"
    )


# =============================================================================
# PROFILE MANAGEMENT
# =============================================================================

def get_profiles_dir() -> Path:
    """Get the edit profiles directory path."""
    return Path(__file__).parent / "profiles" / "edit"


def discover_profiles() -> list[str]:
    """
    Discover all available JSON edit profiles.
    Returns list of profile filenames (without path).
    """
    profiles_dir = get_profiles_dir()
    
    if not profiles_dir.exists():
        profiles_dir.mkdir(parents=True, exist_ok=True)
        return ["default-EDIT.json"]
    
    profiles = sorted([
        f.name for f in profiles_dir.glob("*.json")
        if f.is_file()
    ])
    
    # Ensure default-EDIT is first if it exists
    if "default-EDIT.json" in profiles:
        profiles.remove("default-EDIT.json")
        profiles.insert(0, "default-EDIT.json")
    
    return profiles if profiles else ["default-EDIT.json"]


def load_profile(profile_name: str) -> dict:
    """
    Load a profile from JSON file.
    Returns profile dict with 'templates' and 'pools'.
    """
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / profile_name
    
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_name}")
    
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    # Validate required fields
    if 'templates' not in profile:
        raise ValueError(f"Profile {profile_name} missing 'templates' field")
    if 'pools' not in profile:
        raise ValueError(f"Profile {profile_name} missing 'pools' field")
    
    return profile


def calculate_combinations(profile: dict) -> int:
    """Calculate total unique edit prompt combinations for a profile."""
    total = len(profile.get('templates', []))
    for pool in profile.get('pools', {}).values():
        total *= len(pool)
    return total


# =============================================================================
# CORE HASH FUNCTIONS - O(1) Position-Based Generation
# =============================================================================

def edit_hash(seed: int, *coords: int) -> int:
    """
    Pure O(1) hash from seed + arbitrary coordinate tuple.
    Uses xxhash32 for speed and cross-platform determinism.
    """
    h = xxhash.xxh32(seed=seed & 0xFFFFFFFF)
    h.update(struct.pack('<' + 'i' * len(coords), *coords))
    return h.intdigest()


def hash_to_index(h: int, pool_size: int) -> int:
    """Map hash to valid index in any pool."""
    return h % pool_size


# =============================================================================
# EDIT PROMPT GENERATION
# =============================================================================

def generate_edit_prompt(seed: int, prompt_idx: int, profile: dict) -> str:
    """
    O(1) edit prompt generation from seed, index, and profile.
    
    Args:
        seed: World seed for consistent generation
        prompt_idx: Position in infinite edit prompt space
        profile: Loaded profile dict with 'templates' and 'pools'
    
    Returns:
        Complete formatted edit prompt as a single paragraph
    """
    templates = profile['templates']
    pools = profile['pools']
    
    # Select template using coordinate 0
    template_hash = edit_hash(seed, prompt_idx, 0)
    template = templates[hash_to_index(template_hash, len(templates))]
    
    # Generate each component with unique coordinate
    components = {}
    for i, (key, pool) in enumerate(pools.items()):
        component_hash = edit_hash(seed, prompt_idx, i + 1)
        components[key] = pool[hash_to_index(component_hash, len(pool))]
    
    # Format template with available components
    try:
        return template.format(**components)
    except KeyError as e:
        # If template references a key not in pools, return partial
        for key in pools.keys():
            template = template.replace(f"{{{key}}}", components.get(key, f"[{key}]"))
        return template


# =============================================================================
# COMFYUI NODE CLASS - MAIN GENERATOR
# =============================================================================

class DJZZeroEDIT:
    """
    DJZ Zero EDIT - Procedural Semantic EDIT Prompt Generator with Profiles
    
    Generates infinite deterministic edit prompts using position-is-seed methodology.
    Same (seed, prompt_index, profile) always produces the same edit prompt.
    
    Edit prompts include: action verb, target element, integration details,
    and preservation clauses for unchanged elements.
    """
    
    # Class-level cache for profiles
    _profile_cache: dict = {}
    _last_profile_scan: float = 0
    
    @classmethod
    def INPUT_TYPES(cls):
        # Discover available edit profiles
        profiles = discover_profiles()
        
        return {
            "required": {
                "profile": (profiles, {
                    "default": profiles[0] if profiles else "default-EDIT.json",
                    "tooltip": "Select edit vocabulary profile (JSON files in /profiles/edit/ folder)"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                    "tooltip": "World seed - different seeds explore different edit prompt universes"
                }),
                "prompt_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                    "tooltip": "Position in infinite edit prompt space - each index is a unique edit"
                }),
            },
            "optional": {
                "prefix": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Text to prepend to the generated edit prompt"
                }),
                "suffix": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Text to append to the generated edit prompt"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("edit_prompt",)
    OUTPUT_TOOLTIPS = ("Generated edit prompt as a single paragraph",)
    FUNCTION = "generate"
    CATEGORY = "DJZ-Nodes"
    DESCRIPTION = "Generates deterministic EDIT prompts from seed + index + profile. Same inputs = same output, always."
    
    def generate(self, profile: str, seed: int, prompt_index: int,
                 prefix: str = "", suffix: str = "") -> tuple:
        """
        Generate a single edit prompt from seed, index, and selected profile.
        
        Returns:
            Tuple containing the generated edit prompt string
        """
        # Load profile (with caching)
        if profile not in self._profile_cache:
            try:
                self._profile_cache[profile] = load_profile(profile)
            except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
                # Return error message as prompt
                return (f"[Error loading profile '{profile}': {str(e)}]",)
        
        profile_data = self._profile_cache[profile]
        
        # Generate edit prompt
        prompt = generate_edit_prompt(seed, prompt_index, profile_data)
        
        # Apply prefix/suffix if provided
        if prefix or suffix:
            prompt = f"{prefix}{prompt}{suffix}"
        
        return (prompt,)
    
    @classmethod
    def IS_CHANGED(cls, profile: str, seed: int, prompt_index: int,
                   prefix: str = "", suffix: str = ""):
        """Ensure node updates when inputs change."""
        profile_hash = xxhash.xxh32(profile.encode()).intdigest()
        return edit_hash(seed ^ profile_hash, prompt_index, 0)


# =============================================================================
# COMFYUI NODE CLASS - BATCH GENERATOR
# =============================================================================

class DJZZeroEDITBatch:
    """
    DJZ Zero EDIT Batch - Generate multiple sequential edit prompts.
    
    Generates a batch of edit prompts starting from prompt_index.
    Useful for exploring the edit prompt space or creating variations.
    """
    
    _profile_cache: dict = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        profiles = discover_profiles()
        
        return {
            "required": {
                "profile": (profiles, {
                    "default": profiles[0] if profiles else "default-EDIT.json",
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                }),
                "start_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                    "tooltip": "Starting position in edit prompt space"
                }),
                "batch_size": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 64,
                    "tooltip": "Number of sequential edit prompts to generate"
                }),
            },
            "optional": {
                "prefix": ("STRING", {"default": "", "multiline": False}),
                "suffix": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("edit_prompts",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "generate_batch"
    CATEGORY = "DJZ-Nodes"
    DESCRIPTION = "Generates a batch of sequential deterministic EDIT prompts."
    
    def generate_batch(self, profile: str, seed: int, start_index: int,
                       batch_size: int, prefix: str = "", suffix: str = "") -> tuple:
        """Generate multiple sequential edit prompts."""
        if profile not in self._profile_cache:
            try:
                self._profile_cache[profile] = load_profile(profile)
            except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
                return ([f"[Error loading profile '{profile}': {str(e)}]"],)
        
        profile_data = self._profile_cache[profile]
        prompts = []
        
        for i in range(batch_size):
            prompt = generate_edit_prompt(seed, start_index + i, profile_data)
            if prefix or suffix:
                prompt = f"{prefix}{prompt}{suffix}"
            prompts.append(prompt)
        
        return (prompts,)
    
    @classmethod
    def IS_CHANGED(cls, profile: str, seed: int, start_index: int,
                   batch_size: int, prefix: str = "", suffix: str = ""):
        profile_hash = xxhash.xxh32(profile.encode()).intdigest()
        return edit_hash(seed ^ profile_hash, start_index, batch_size)


# =============================================================================
# PROFILE INFO NODE
# =============================================================================

class DJZZeroEDITProfileInfo:
    """
    Utility node to display edit profile statistics.
    Shows pool sizes and total combinations for selected profile.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        profiles = discover_profiles()
        
        return {
            "required": {
                "profile": (profiles, {
                    "default": profiles[0] if profiles else "default-EDIT.json",
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("info",)
    FUNCTION = "get_info"
    CATEGORY = "DJZ-Nodes"
    DESCRIPTION = "Display statistics about a ZeroEDIT profile"
    
    def get_info(self, profile: str) -> tuple:
        """Get profile information as formatted string."""
        try:
            profile_data = load_profile(profile)
        except Exception as e:
            return (f"Error loading profile: {e}",)
        
        lines = [
            f"Profile: {profile_data.get('name', profile)}",
            f"Description: {profile_data.get('description', 'N/A')}",
            f"Version: {profile_data.get('version', 'N/A')}",
            "",
            "Pool Sizes:",
        ]
        
        for pool_name, pool_items in profile_data.get('pools', {}).items():
            lines.append(f"  {pool_name}: {len(pool_items)} entries")
        
        lines.append(f"  templates: {len(profile_data.get('templates', []))} variations")
        lines.append("")
        
        total = calculate_combinations(profile_data)
        lines.append(f"Total unique edit prompts: {total:,}")
        lines.append(f"Scientific notation: {total:.2e}")
        
        return ("\n".join(lines),)
    
    @classmethod
    def IS_CHANGED(cls, profile: str):
        """Check if profile file has changed."""
        profile_path = get_profiles_dir() / profile
        if profile_path.exists():
            return profile_path.stat().st_mtime
        return 0


# =============================================================================
# COMFYUI REGISTRATION
# =============================================================================

NODE_CLASS_MAPPINGS = {
    "DJZ-ZeroEDIT": DJZZeroEDIT,
    "DJZ-ZeroEDIT-Batch": DJZZeroEDITBatch,
    "DJZ-ZeroEDIT-ProfileInfo": DJZZeroEDITProfileInfo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DJZ-ZeroEDIT": "DJZ Zero EDIT",
    "DJZ-ZeroEDIT-Batch": "DJZ Zero EDIT Batch",
    "DJZ-ZeroEDIT-ProfileInfo": "DJZ Zero EDIT Profile Info",
}


# =============================================================================
# STANDALONE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DJZ-ZeroEDIT - Procedural EDIT Prompt Generation with Profiles")
    print("=" * 70)
    
    # Discover profiles
    print("\n[Profile Discovery]")
    print("-" * 70)
    profiles = discover_profiles()
    print(f"Found {len(profiles)} profile(s): {', '.join(profiles)}")
    
    # Test each profile
    for profile_name in profiles:
        print(f"\n[Testing Profile: {profile_name}]")
        print("-" * 70)
        
        try:
            profile_data = load_profile(profile_name)
            
            # Show info
            print(f"Name: {profile_data.get('name', 'N/A')}")
            print(f"Description: {profile_data.get('description', 'N/A')}")
            
            # Pool stats
            print("\nPool sizes:")
            for pool_name, pool_items in profile_data.get('pools', {}).items():
                print(f"  {pool_name}: {len(pool_items)}")
            print(f"  templates: {len(profile_data.get('templates', []))}")
            
            # Calculate combinations
            total = calculate_combinations(profile_data)
            print(f"\nTotal combinations: {total:,} ({total:.2e})")
            
            # Generate sample edit prompts
            print(f"\nSample edit prompts (seed=42, indices 0-4):")
            for idx in range(5):
                prompt = generate_edit_prompt(seed=42, prompt_idx=idx, profile=profile_data)
                print(f"\n  [{idx}] {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
            
            # Verify determinism
            print(f"\nDeterminism check:")
            p1 = generate_edit_prompt(seed=42, prompt_idx=1000, profile=profile_data)
            p2 = generate_edit_prompt(seed=42, prompt_idx=1000, profile=profile_data)
            print(f"  seed=42, idx=1000: {'✓ MATCH' if p1 == p2 else '✗ MISMATCH'}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 70)
    print("Testing complete!")
