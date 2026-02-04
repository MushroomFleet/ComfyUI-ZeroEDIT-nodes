---
name: zeroedit-profile-builder
description: Create JSON vocabulary profiles for DJZ-ZeroEDIT procedural EDIT prompt generation. Use when user wants to build an edit profile from a system prompt, style guide, enhancement instructions, or example prompts. Triggers on phrases like "create zeroedit profile", "build edit profile", "make EDIT json", "convert to zeroedit", "zeroedit profile from", or when user uploads enhancement system prompts, style guides, or prompt examples and mentions ZeroEDIT, EDIT profile, or procedural edit generation.
---

# ZeroEDIT Profile Builder

Convert enhancement system prompts, style guides, and example edit instructions into procedural generation profiles (.json) for DJZ-ZeroEDIT.

## Profile Structure

```json
{
  "name": "Profile Name",
  "description": "What edit prompts this generates",
  "version": "1.0.0",
  "templates": ["Template with {pool} placeholders"],
  "pools": {
    "pool_name": ["item1", "item2"]
  }
}
```

## Conversion Pipeline

```
INPUT: System prompt / Style guide / Examples
  → [1] Edit Pattern Analysis
  → [2] Pool Extraction (edit-specific)
  → [3] Template Synthesis
  → [4] Validation & Statistics
OUTPUT: profile.json
```

## Step 1: Edit Pattern Analysis

Identify the edit domain and map content to semantic pools. For edit prompts, use these core pool categories:

| Pool | Purpose | Look For |
|------|---------|----------|
| `edit_operation` | Complete edit instructions | Action + target + details as phrases |
| `target` | What to modify | Objects, attributes, regions, elements |
| `action` | Edit verbs | add, remove, change, transform, replace |
| `integration` | Blending requirements | Lighting match, style continuity |
| `preservation` | What stays unchanged | Preservation clauses, keep/maintain phrases |
| `location` | Where in image | Position references, spatial terms |

**Domain-specific pools** - Create custom pools matching the source material:
- Character profiles: `expression`, `pose`, `outfit`, `hair`, `skin`
- Environments: `architecture`, `materials`, `lighting`, `season`
- Style transfer: `art_style`, `color_palette`, `texture`, `mood`

## Step 2: Pool Extraction

**For system prompts with vocabulary lists:**
1. Extract listed terms directly into appropriate pools
2. Preserve exact phrasing for domain-specific terminology
3. Expand abbreviated lists with logical variations

**For example-based sources:**
1. Parse examples to identify recurring patterns
2. Extract variable segments as pool entries
3. Identify fixed template structure

**For narrative style guides:**
1. Convert descriptive rules into pool entries
2. Extract approved/forbidden lists
3. Transform guidelines into concrete phrases

## Step 3: Template Synthesis

Create 4-8 templates following edit prompt structure:

```
[Context] + [Action] + [Target] + [Integration] + [Preservation]
```

**Template rules:**
- Use `{pool_name}` syntax for variable content
- Keep grammatical connectors in templates (Using, Ensure, Keep)
- End with preservation clause placeholder
- Include period placement in templates

**Example template patterns:**
```
"Using the provided image, {edit_operation}. {integration}. {preservation}."
"{edit_operation}. Ensure the change {blending}. {preservation}."
"In this image, {edit_operation}. {integration}. {preservation}, maintaining {style_element}."
```

## Step 4: Validation

**Required checks:**
- [ ] All `{pool}` references exist in pools
- [ ] No empty pools
- [ ] Valid JSON syntax
- [ ] No duplicate items within pools
- [ ] Templates produce grammatical output when filled

**Edit-specific validation:**
- [ ] Preservation clauses present in templates
- [ ] Integration/blending language included
- [ ] Action verbs appropriate for edit operations

## Output Format

Always provide:

```
## Analysis Summary
- Source type: [system prompt / style guide / examples]
- Edit domain: [character / environment / style / general]
- Identified pools: [list with counts]

## Generated Profile
[Complete JSON]

## Statistics
- Templates: N
- Pool sizes: pool_name(N), ...
- Total combinations: N (scientific notation)

## Sample Outputs (seed=42, indices 0-4)
[0] generated edit prompt...
```

## Combination Calculation

```
total = len(templates) × len(pool_1) × len(pool_2) × ... × len(pool_n)
```

Target ranges:
- Focused profiles: 1-10 billion combinations
- General profiles: 10-500 billion combinations
- Comprehensive profiles: 500 billion+ combinations

## Reference Materials

- **Edit Grounding**: See `references/edit-grounding.md` for complete edit prompt construction rules
- **Example Profiles**: See `assets/example-profiles/` for reference implementations

## Common Patterns

### Character Aesthetic Profiles
Pools: `role`, `outfit`, `expression`, `pose`, `physical_traits`, `environment`, `lighting`, `style_tag`

### Environment/Background Profiles
Pools: `architecture`, `room_type`, `materials`, `lighting`, `season`, `preservation`

### Style Transfer Profiles
Pools: `source_style`, `target_style`, `preservation_elements`, `adaptation_details`

### General Edit Profiles
Pools: `edit_operation`, `integration`, `blending`, `preservation`, `technical_details`

## Edge Cases

- **Sparse source (<20 examples)**: Expand vocabulary through logical variations
- **Highly specific aesthetic**: Preserve exact terminology, don't generalize
- **Conflicting rules**: Prioritize explicit rules over implied patterns
- **Missing categories**: Create templates that work with available pools
