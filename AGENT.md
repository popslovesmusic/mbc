# Agent Instructions - HGG Semantic Catalog

> **Purpose**: This document provides context and operational instructions for AI agents working with the HGG (Meta-Genesis/Box Calculus) semantic knowledge catalog.

## System Overview

**What This Is**: A semantic card catalog indexing 81 markdown documents (11,429+ blocks) containing Meta-Genesis physics theory, Box Calculus, and IGSOA content.

**Data Format**: File-based catalog (YAML, JSONL, HTML) - NO database. All data is in simple text files.

**Philosophy**:
- Sources are sacred (never modify `HGG-/` files)
- Catalog is regenerable (can rebuild anytime)
- Multiple interfaces (CLI, files, HTML)

## Quick Context

### What's Indexed
- **81 markdown files** from ChatGPT conversations about Meta-Genesis theory
- **11,429 semantic blocks** (paragraphs, lists, axioms, theorems, equations)
- **Content**: Mathematical physics, δ-geometry, Box Calculus, Meta-Time, formal axioms

### Key Concepts to Know
- **δ (delta)**: Deviation operator, fundamental primitive
- **Φ (Phi)**: Chromatic/potential field
- **Π (Pi)**: Projection functor (Meta-Time → spacetime)
- **Box Calculus**: Semantic operator algebra (E, A, polarity, routers)
- **Meta-Genesis**: Ontological framework for physics
- **IGSOA**: Information Geometry State Operator Algebra

## Data Locations

### Primary Data Files
```
catalog/
├── sources.json              # Registry of 81 source files
├── indexes/
│   ├── segments.jsonl       # 11,429 segments (full data)
│   ├── cards.jsonl          # 11,429 cards (basic)
│   └── location-index.txt   # ID → location mapping
└── cards/by-source/         # 11,429 YAML cards

catalog-html/
├── index.html               # Browse in web browser
├── analytics.html           # Charts & visualizations
└── sources/*.html           # HTML-formatted sources
```

### Source Files (READ-ONLY)
```
HGG-/
├── genesis-0/ to genesis-20/  # 21 topic directories
├── intake/                     # Meta-documents
└── special/                    # Utility files
```

## How to Query the Catalog

### Method 1: Read JSONL Indexes (RECOMMENDED)

**Load all cards**:
```python
import json
from pathlib import Path

cards = []
with open('catalog/indexes/cards.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        card = json.loads(line)
        cards.append(card)
```

**Card structure** (basic):
```json
{
  "id": "GEN0-001",
  "location": "genesis-0/file::heading::b1",
  "source": "genesis-0\\filename.md",
  "heading": "Section Title",
  "concepts": ["δ", "Meta-Time", "Box"],
  "block_type": "paragraph",
  "lines": "150-175",
  "excerpt": "First 200 chars of content..."
}
```

### Method 2: Read Segments (Full Content)

**Get full block content**:
```python
segments = []
with open('catalog/indexes/segments.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        seg = json.loads(line)
        segments.append(seg)

# Segment includes full 'content' field
print(seg['content'])  # Full markdown text
```

### Method 3: Read YAML Cards

**Individual card files**:
```python
import yaml

with open('catalog/cards/by-source/genesis-0/axioms__b1.yaml', 'r', encoding='utf-8') as f:
    card = yaml.safe_load(f)
```

### Method 4: Read Source Files Directly

**Original markdown**:
```python
with open('HGG-/genesis-0/Tri-Unity_Theorem.md', 'r', encoding='utf-8') as f:
    content = f.read()
```

## Common Agent Tasks

### Task: Find Axioms

```python
import json

axioms = []
with open('catalog/indexes/cards.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        card = json.loads(line)
        # Check heading for axiom markers
        if any(word in card['heading'].lower() for word in ['axiom', 'theorem', 'lemma']):
            axioms.append(card)

print(f"Found {len(axioms)} formal statements")
```

### Task: Search by Concept

```python
import json

query = "Meta-Time"
results = []

with open('catalog/indexes/cards.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        card = json.loads(line)
        if query in card.get('concepts', []):
            results.append(card)
        elif query.lower() in card.get('heading', '').lower():
            results.append(card)
        elif query.lower() in card.get('excerpt', '').lower():
            results.append(card)

print(f"Found {len(results)} cards about {query}")
```

### Task: Get All Concepts

```python
import json
from collections import Counter

all_concepts = []
with open('catalog/indexes/cards.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        card = json.loads(line)
        all_concepts.extend(card.get('concepts', []))

concept_freq = Counter(all_concepts)
top_20 = concept_freq.most_common(20)

print("Top 20 concepts:")
for concept, count in top_20:
    print(f"  {concept}: {count}")
```

### Task: Find Related Blocks

```python
import json

def find_related(location_code_prefix):
    """Find all blocks under a heading"""
    related = []
    with open('catalog/indexes/cards.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            card = json.loads(line)
            if card['location'].startswith(location_code_prefix):
                related.append(card)
    return related

# Example: All blocks under "tri-unity-theorem" heading
results = find_related("genesis-0/tri-unity-theorem")
```

### Task: Get Block Content by ID

```python
import json

def get_block_content(card_id):
    """Get full content for a card ID"""
    with open('catalog/indexes/segments.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            seg = json.loads(line)
            if seg['id'] == card_id:
                return seg['content']
    return None

content = get_block_content("GEN0-001")
print(content)
```

## Location Code Format

**Structure**: `directory/filename::heading-chain::block-number`

**Example**: `genesis-0/tri-unity-theorem::objects-primitives::b1`

**Parts**:
- `genesis-0` - Source directory
- `tri-unity-theorem` - Filename (slugified)
- `objects-primitives` - Heading chain (can be nested: `h1::h2::h3`)
- `b1` - Block sequence number

**Usage**: Use location codes to reference specific blocks across conversations.

## Card ID Format

**Structure**: `DIR#-NNN`

**Examples**:
- `GEN0-001` - genesis-0, card #1
- `GEN5-042` - genesis-5, card #42
- `INTK-012` - intake, card #12
- `SPEC-005` - special, card #5

**Usage**: Short references for quick lookup.

## Important Constraints

### ⚠️ DO NOT Modify
- **Never** write to `HGG-/` directory (source files are read-only)
- **Never** modify existing catalog files without explicit user request

### ✅ Safe Operations
- Reading any file in `catalog/` or `catalog-html/`
- Reading source files from `HGG-/`
- Running CLI commands: `python hgg-index.py [command]`
- Generating reports, summaries, analysis

### 🔄 Regeneration
If catalog seems outdated:
```bash
python hgg-index.py build        # Rebuild from sources
python generate-html-catalog.py  # Rebuild HTML
```

## CLI Commands Reference

```bash
# Query catalog
python hgg-index.py stats              # Show statistics
python hgg-index.py ls --limit 20      # List cards
python hgg-index.py show GEN0-001      # Show card details

# Rebuild catalog
python hgg-index.py build              # Full rebuild

# Generate HTML
python generate-html-catalog.py        # Create browser interface
```

## Semantic Metadata Available

### If Enhanced Cards Exist (`cards-enhanced.jsonl`)

Additional fields available:
```json
{
  "aliases": ["Am154nb2"],              // Stable identifiers
  "tags": ["axiom", "definitive"],      // Semantic tags
  "is_formal": true,                    // Contains axiom/theorem
  "statement_type": "axiom",            // Type of formal statement
  "axiom_count": 1,                     // Count in block
  "identifiers": ["A1"],                // Formal IDs (A1, GA-8, etc.)
  "conversational_score": 0.0,          // 0=technical, 1=conversational
  "is_technical": true,                 // Has math/symbols
  "has_contradictions": false,          // Conflicting statements
  "has_ambiguity": false,               // Uncertain language
  "is_definitive": true,                // Clear, unqualified
  "max_severity": 0.15,                 // 0=certain, 1=uncertain
  "concept_density": 12.5               // Concepts per 100 words
}
```

## Expected Response Patterns

### When Asked About Content

1. **Search the catalog first** using JSONL queries
2. **Read the source** if full context needed
3. **Cite location codes** when referencing blocks
4. **Link to HTML** if user might want to browse: `catalog-html/index.html`

### When Asked to Find Something

1. **Query cards.jsonl** for metadata
2. **Show card IDs and locations** in results
3. **Offer to show full content** if needed
4. **Suggest filters** (by directory, concept, type)

### When Asked for Analysis

1. **Load all cards** from JSONL
2. **Aggregate statistics** (concept frequency, distribution)
3. **Point to analytics.html** for visual charts
4. **Suggest jq queries** for advanced filtering

## Example Agent Workflow

**User**: "Find all axioms about Meta-Time"

**Agent Response**:
```python
import json

results = []
with open('catalog/indexes/cards.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        card = json.loads(line)
        is_axiom = 'axiom' in card['heading'].lower()
        has_metatime = 'Meta-Time' in card.get('concepts', [])

        if is_axiom and has_metatime:
            results.append({
                'id': card['id'],
                'heading': card['heading'],
                'location': card['location'],
                'excerpt': card['excerpt']
            })

# Found 3 axioms about Meta-Time:
# - GEN0-042: Axiom A5 (Meta-Time Emergence)
# - GEN8-015: Meta-Time Geometry Axiom
# - GEN18-087: Temporal Projection Axiom
```

## Useful jq Queries

```bash
# Find all axioms
jq 'select(.heading | contains("Axiom"))' catalog/indexes/cards.jsonl

# Get concept frequency
jq -r '.concepts[]' catalog/indexes/cards.jsonl | sort | uniq -c | sort -nr

# Find by directory
jq 'select(.source | startswith("genesis-0"))' catalog/indexes/cards.jsonl

# Count by block type
jq -r '.block_type' catalog/indexes/cards.jsonl | sort | uniq -c
```

## Context for Understanding Content

### Domain Background
This catalog indexes research on **Meta-Genesis**, a theoretical physics framework proposing that:
- Physical reality emerges from δ (deviation) as a primitive
- Spacetime is a projection (Π) of a deeper Meta-Time layer
- Standard physics (QFT, GR) emerge as projections of δ-geometry
- Box Calculus provides the semantic/operator algebra

### Typical Content Types
- **Axioms**: Foundational statements (A1, A2, GA-8)
- **Theorems**: Derived results (Tri-Unity, Meta-Einstein)
- **Technical derivations**: Math proofs, calculations
- **Conceptual explanations**: Intuitive descriptions
- **Conversational Q/A**: ChatGPT dialogue (marked for filtering)

### Key Files to Know
- `genesis-0/` - Foundation axioms
- `genesis-1/` - Core geometry
- `genesis-5/` - Meta-Einstein equation
- `intake/BOX_CALCULUS*.md` - Box Calculus technical intro
- `intake/Volume_I*.md`, `Volume_II*.md` - Summaries

## Output Formatting

### When Showing Cards
```
Card: GEN0-042
Heading: Axiom A5 (Meta-Time Emergence)
Location: genesis-0/axioms::a5::b1
Source: genesis-0\Foundation_Axioms.md (lines 245-267)
Concepts: Meta-Time, δ, Φ, emergence, temporal
```

### When Showing Queries
```python
# Results: 5 cards found

GEN0-042 | Axiom A5 (Meta-Time Emergence)
  → genesis-0/axioms::a5::b1

GEN8-015 | Meta-Time Geometry Axiom
  → genesis-8/meta-time::geometry::b3

[...]
```

## Error Handling

### If File Not Found
```python
from pathlib import Path

cards_file = Path('catalog/indexes/cards.jsonl')
if not cards_file.exists():
    print("Catalog not built yet. Run: python hgg-index.py build")
```

### If Encoding Issues
```python
# Always use UTF-8 (Greek symbols, math)
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()
```

## Version Info

**Catalog Version**: Generated from HGG Index v0.1.0
**Total Cards**: 11,429
**Last Built**: Check `catalog/sources.json` timestamp
**Python Required**: 3.11+

## Getting Help

**Documentation**:
- `docs/hgg-index-user-guide.md` - CLI usage
- `docs/hgg-index-enhanced-features.md` - Semantic features
- `docs/html-catalog-guide.md` - Web interface
- `COMPLETE.md` - Full feature list

**Regenerate Catalog**:
```bash
python hgg-index.py build
```

**Open Browser Interface**:
```
file:///path/to/catalog-html/index.html
```

---

## TL;DR for Agents

**Data Location**: `catalog/indexes/cards.jsonl` (11,429 entries)

**Load Cards**:
```python
import json
cards = [json.loads(line) for line in open('catalog/indexes/cards.jsonl')]
```

**Search**:
```python
results = [c for c in cards if 'axiom' in c['heading'].lower()]
```

**Get Content**:
```python
segments = [json.loads(line) for line in open('catalog/indexes/segments.jsonl')]
content = next(s['content'] for s in segments if s['id'] == 'GEN0-001')
```

**Rules**: Read-only on `HGG-/`, catalog is regenerable, cite location codes

**Context**: Meta-Genesis physics theory, 81 ChatGPT transcripts, 11k+ blocks

---

*This catalog is optimized for semantic search, concept extraction, and knowledge navigation. All data is local, no API calls needed.*
