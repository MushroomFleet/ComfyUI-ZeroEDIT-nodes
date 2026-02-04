# DJZ-ZeroEDIT

**Procedural Semantic EDIT Prompt Generation for ComfyUI**

# Part of the DJZ-Zerobytes 0(1) procedural collection
https://github.com/MushroomFleet/ComfyUI-DJZ-ZeroPrompt
https://github.com/MushroomFleet/ComfyUI-ZeroENH
https://github.com/MushroomFleet/ComfyUI-ZeroEDIT-nodes

A deterministic procedural system for generating AI image editing prompts using the ZeroBytes position-is-seed methodology. Perfect for batch editing workflows, A/B testing edit variations, and exploring the edit prompt space systematically.

## Features

- **Deterministic Generation**: Same (seed, index, profile) → same edit prompt, always
- **O(1) Performance**: Instant generation via coordinate hashing, no iteration required
- **JSON Profile System**: Customizable vocabulary pools for different editing domains
- **Edit-Specific Templates**: Pre-structured for action, integration, and preservation clauses
- **4.4+ Billion Combinations**: Default profile covers comprehensive editing scenarios

## Installation

1. Clone or copy to your ComfyUI custom_nodes directory:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-repo/DJZ-ZeroEDIT
```

2. Install dependencies:
```bash
pip install xxhash
```

3. Restart ComfyUI

## Nodes

### DJZ Zero EDIT
Main generator node. Produces a single deterministic edit prompt.

**Inputs:**
- `profile` - JSON profile selection (from `/profiles/edit/`)
- `seed` - World seed (0 to 4,294,967,295)
- `prompt_index` - Position in infinite prompt space
- `prefix` (optional) - Text prepended to output
- `suffix` (optional) - Text appended to output

**Output:**
- `edit_prompt` - Complete edit instruction string

### DJZ Zero EDIT Batch
Generates multiple sequential edit prompts for batch operations.

**Inputs:**
- `profile` - JSON profile selection
- `seed` - World seed
- `start_index` - Starting position
- `batch_size` - Number of prompts (1-64)
- `prefix`/`suffix` (optional)

**Output:**
- `edit_prompts` - List of edit instruction strings

### DJZ Zero EDIT Profile Info
Displays statistics about the selected profile.

**Output:**
- `info` - Formatted string with pool sizes and combination count

## Profile Structure

Profiles are JSON files in `/profiles/edit/` containing:

```json
{
  "name": "Profile Name",
  "description": "What this profile generates",
  "version": "1.0.0",
  "templates": [
    "Template with {pool_name} placeholders"
  ],
  "pools": {
    "pool_name": ["item1", "item2", "..."]
  }
}
```

### Default Profile Pools

| Pool | Purpose | Count |
|------|---------|-------|
| `edit_operation` | Complete edit instructions (add/remove/change/transform) | 63 |
| `integration_detail` | How changes should blend with scene | 12 |
| `blending_phrase` | Seamlessness descriptions | 10 |
| `lighting_consistency` | Light matching requirements | 10 |
| `shadow_detail` | Shadow integration rules | 6 |
| `material_consistency` | Surface/texture matching | 10 |
| `preservation_clause` | What to keep unchanged | 14 |
| `style_element` | Artistic style continuity | 10 |

## Edit Operation Categories

The default profile covers these edit types:

**Element Addition** - Adding accessories, objects, environmental details
```
add a small knitted wizard hat on the subject's head...
```

**Element Removal** - Deleting unwanted objects, cleaning backgrounds
```
remove the person visible in the background, naturally reconstructing...
```

**Attribute Modification** - Changing colors, materials, time of day
```
change the dress to deep crimson red while maintaining the same cut...
```

**Style Transfer** - Converting to artistic styles
```
transform the photograph into the artistic style of Vincent van Gogh...
```

**Multi-Image Composition** - Combining elements from references
```
place the logo from the reference image centered on the chest...
```

## Creating Custom Profiles

1. Create a new JSON file in `/profiles/edit/`
2. Define templates with `{pool_name}` placeholders
3. Populate pools with domain-specific vocabulary
4. Ensure all referenced pools exist

### Example: Portrait Retouching Profile

```json
{
  "name": "Portrait Retouch",
  "description": "Professional portrait editing operations",
  "version": "1.0.0",
  "templates": [
    "{retouch_action}. {skin_handling}. {preservation}."
  ],
  "pools": {
    "retouch_action": [
      "Smooth skin texture while preserving natural pores",
      "Brighten the eyes and add subtle catchlights",
      "Remove temporary blemishes from the face"
    ],
    "skin_handling": [
      "Maintain realistic skin texture and undertones",
      "Keep natural color variation in the skin"
    ],
    "preservation": [
      "Preserve the subject's unique features and character",
      "Keep the natural expression unchanged"
    ]
  }
}
```

## ZeroBytes Methodology

This node implements position-is-seed procedural generation:

- **Coordinate System**: (seed, prompt_index, component_index)
- **Hash Function**: xxhash32 for speed and determinism
- **No Iteration**: Any prompt accessible in O(1) time
- **Cross-Platform**: Same results on any system

```python
# Conceptual model
hash(seed, prompt_idx=1000, component=0) → template selection
hash(seed, prompt_idx=1000, component=1) → edit_operation selection
hash(seed, prompt_idx=1000, component=2) → integration_detail selection
# ...
```

## Workflow Examples

### Sequential Edit Exploration
```
Seed: 42
Index 0 → "add a small knitted wizard hat..."
Index 1 → "turn this rough sketch into..."
Index 2 → "add a colorful silk scarf..."
```

### Parallel Seed Exploration
```
Index: 100
Seed 0 → variation A
Seed 1 → variation B
Seed 2 → variation C
```

### Batch Processing
Use the Batch node to generate 64 variations at once for automated testing.

## Combination Mathematics

Total unique prompts = templates × pool₁ × pool₂ × ... × poolₙ

Default profile:
```
7 × 63 × 12 × 10 × 10 × 6 × 10 × 14 × 10 = 4,445,280,000
```

That's over 4.4 billion unique edit prompts from a single profile.

## License

MIT License - See LICENSE file

## Credits

Based on DJZ-ZeroPrompt-V2 architecture.
Edit prompt patterns derived from Nano Banana Pro 2026 documentation and FLUX.1 Kontext community guidance.
