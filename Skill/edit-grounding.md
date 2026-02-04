# General Instructional EDIT Prompting Grounding

> **Primary Source:** Nano Banana Pro 2026 Official Documentation (Google)  
> **Supplementary Sources:** FLUX.1 Kontext community guidance

---

## Core Philosophy

**Describe the scene, don't just list keywords.**

The model's core strength is deep language understanding. A narrative, descriptive paragraph will almost always produce a better, more coherent image than a list of disconnected words.

This principle applies to both generation and editing. For edits, you describe the *change* narratively rather than issuing terse commands.

---

## Edit Mode Operation

Edit prompts modify existing images. Provide the image alongside descriptive instructions. The model automatically matches the original image's style, lighting, and perspective. Your job is to describe the desired change clearly and specify what should remain unchanged.

---

## Edit Prompt Templates

### Adding and Removing Elements

```
Using the provided image of [subject], please [add/remove/modify] [element]
to/from the scene. Ensure the change is [description of how the change
should integrate].
```

**Example:**
```
Using the provided image of my cat, please add a small, knitted wizard hat
on its head. Make it look like it's sitting comfortably and matches the soft
lighting of the photo.
```

### Inpainting (Semantic Masking)

```
Using the provided image, change only the [specific element] to [new
element/description]. Keep everything else in the image exactly the same,
preserving the original style, lighting, and composition.
```

**Example:**
```
Using the provided image of a living room, change only the blue sofa to be
a vintage, brown leather chesterfield sofa. Keep the rest of the room,
including the pillows on the sofa and the lighting, unchanged.
```

### Style Transfer

```
Transform the provided photograph of [subject] into the artistic style of
[artist/art style]. Preserve the original composition but render it with
[description of stylistic elements].
```

**Example:**
```
Transform the provided photograph of a modern city street at night into the
artistic style of Vincent van Gogh's 'Starry Night'. Preserve the original
composition of buildings and cars, but render all elements with swirling,
impasto brushstrokes and a dramatic palette of deep blues and bright yellows.
```

### Multi-Image Composition

```
Create a new image by combining the elements from the provided images. Take
the [element from image 1] and place it with/on the [element from image 2].
The final image should be a [description of the final scene].
```

### High-Fidelity Detail Preservation

```
Using the provided images, place [element from image 2] onto [element from
image 1]. Ensure that the features of [element from image 1] remain
completely unchanged. The added element should [description of how the
element should integrate].
```

### Sketch to Finished Image

```
Turn this rough [medium] sketch of a [subject] into a [style description]
photo. Keep the [specific features] from the sketch but add [new details/materials].
```

---

## Action Verbs Reference

| Category | Verbs | Use Case |
|----------|-------|----------|
| Modification | change, make, transform, convert | Alter existing attributes |
| Addition | add, include, put, place | Insert new elements |
| Removal | remove, delete, take away | Eliminate elements |
| Replacement | replace, swap, substitute | Exchange one element for another |
| Positioning | move, place, position | Relocate elements |

**Note:** "Change" implies attribute modification; "transform" suggests more dramatic stylistic alteration.

---

## Preservation Clauses

Use these phrases to protect elements from unintended modification:

- `Keep everything else in the image exactly the same`
- `preserving the original style, lighting, and composition`
- `while maintaining [element]`
- `Ensure [element] remain completely unchanged`
- `keeping the person in the exact same position, scale, and pose`

---

## Integration Phrases

Use these to ensure seamless blending:

- `matches the soft lighting of the photo`
- `blends seamlessly with the surrounding environment`
- `follows the natural contours and folds of the surface`
- `casts appropriate shadows consistent with the light source`
- `maintains the same color temperature as the scene`
- `appears naturally integrated with realistic proportions`

---

## Precision Levels

| Level | Description | Example |
|-------|-------------|---------|
| **Simple** | Direct, minimal instruction | `Change to nighttime.` |
| **Controlled** | Adds preservation clauses | `Change to nighttime while maintaining the style of the painting.` |
| **Complex** | Multiple specified changes with full preservation | `Change setting to nighttime, add streetlights illuminating the road, while maintaining the car's design and color.` |

Start simple. Add complexity only when results require more control.

---

## Common Failure Modes and Fixes

### Character Identity Drift
**Problem:** Subject's appearance changes across edits.  
**Fix:** Describe the subject explicitly: *"the woman with brown hair, blue eyes, and a neutral expression."* Add preservation: *"Ensure the woman's face and features remain completely unchanged."*

### Composition Shift
**Problem:** Subject moves or rescales unexpectedly.  
**Fix:** Add position anchoring: *"keeping the person in the exact same position, scale, and pose."*

### Over-Modification
**Problem:** Model changes more than requested.  
**Fix:** Add blanket preservation: *"Keep everything else in the image exactly the same, preserving the original style, lighting, and composition."*

### Style Transfer Loses Detail
**Problem:** Applying a style erases important scene information.  
**Fix:** Describe the style's visual characteristics: *"swirling, impasto brushstrokes and a dramatic palette of deep blues and bright yellows."* Specify what to preserve: *"Preserve the original composition of buildings and cars."*

---

## Best Practices for Profile Creation

### Be Hyper-Specific in Pool Entries
Instead of "fantasy armor," use: *"ornate elven plate armor, etched with silver leaf patterns, with a high collar and pauldrons shaped like falcon wings."*

### Provide Context in Templates
Include purpose framing: *"Using the provided image"* yields better results than bare commands.

### Use Complete Phrases for edit_operation Pools
Rather than assembling from parts, use complete edit instructions:
```
"add a small knitted wizard hat on the subject's head, positioned naturally between the ears"
"change the background to a moody urban nightscape with neon lights"
"remove the person visible in the background, naturally reconstructing the obscured area"
```

### Include Semantic Negative Intent
Instead of listing what NOT to do, describe the desired state positively.

---

## Pool Design Guidelines

### edit_operation Pool
- Complete edit instructions as single entries
- Include target, action, and basic integration in one phrase
- 40-80 entries for comprehensive coverage

### preservation Pool
- Blanket preservation statements
- Element-specific preservation
- 10-20 entries covering common cases

### integration Pool
- Lighting matching phrases
- Style continuity statements
- Material/texture consistency
- 10-15 entries

### Domain-Specific Pools
- Extract exact terminology from source material
- Preserve stylistic language
- Include all approved variants

---

## Target Word Counts

| Edit Type | Target Words |
|-----------|--------------|
| Simple edit | 40-60 words |
| Standard edit | 60-90 words |
| Complex edit | 90-120 words |
| Multi-image composite | 100-150 words |

Templates should produce output in the 60-100 word range for most use cases.

---

*Primary source: Nano Banana Pro 2026 Official Documentation. Supplementary patterns from FLUX.1 Kontext community guidance.*
