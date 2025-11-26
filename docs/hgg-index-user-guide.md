# HGG Index - User Guide

## What Is HGG Index?

HGG Index is a **card catalog system** for your semantic markdown library. It's not a database - it's a collection of simple text files that point to content in your source documents, like index cards in a library card catalog.

**Key Principles:**
- **Sources are sacred**: Original markdown files in `HGG-/` are never modified
- **Cards are ephemeral**: The entire catalog can be regenerated from sources at any time
- **Simple files**: Everything is YAML, JSONL, or plain text - grep-friendly and version-controllable
- **Location codes**: Stable addressing system for every semantic block

## Quick Start

### Build the Complete Catalog

```bash
python hgg-index.py build
```

This scans all `.md` files in `HGG-/`, segments them into semantic blocks, and generates catalog cards.

**Output:**
- `catalog/sources.json` - Registry of source files with checksums
- `catalog/indexes/` - Flat indexes for searching
- `catalog/cards/by-source/` - Individual YAML cards organized by directory

### View Statistics

```bash
python hgg-index.py stats
```

Shows source count, segment count, and cards by directory.

### List Cards

```bash
# List first 20 cards
python hgg-index.py ls --limit 20

# Filter by source directory
python hgg-index.py ls --source genesis-0 --limit 10
```

### Show Card Details

```bash
# Show card metadata
python hgg-index.py show GEN0-001

# Show full content from source
python hgg-index.py show GEN0-001 -v
```

## Understanding the Catalog Structure

### Location Codes

Every semantic block has a stable location code:

```
genesis-0/tri-unity-theorem::objects-primitives::b1
│         │                  │                  │
│         │                  │                  └─ Block sequence (b1, b2, b3...)
│         │                  └─ Heading chain (slugified)
│         └─ Filename slug
└─ Directory name
```

**Example:**
- Source: `HGG-/genesis-0/Tri-Unity_Theorem_Equivalence_of___.md`
- Heading: `## Objects / primitives`
- Location: `genesis-0/tri-unity-theorem::objects-primitives::b1`

### Card IDs

Short, memorable IDs for quick reference:

- `GEN0-001` - First card from genesis-0
- `GEN5-042` - 42nd card from genesis-5
- `INTK-012` - 12th card from intake
- `SPEC-005` - 5th card from special

### Directory Layout

```
catalog/
├── sources.json                    # Source file registry
├── indexes/
│   ├── cards.jsonl                # Flat index (one JSON per line)
│   ├── segments.jsonl             # Full segment data
│   └── location-index.txt         # ID → location mapping
└── cards/
    └── by-source/
        ├── genesis-0/              # Cards from genesis-0/
        │   ├── 0-context__b1.yaml
        │   ├── tri-unity-theorem__b1.yaml
        │   └── ...
        ├── genesis-1/
        ├── intake/
        └── special/
```

## Card Format

Each card is a simple YAML file:

```yaml
id: GEN0-079
location: genesis-0/feynman-rules-interaction-vertices::0-context::b1
source: genesis-0\-Feynman_Rules__Interaction_Vertices.md
lines: 1163-1188
heading: '**0. Context**'
concepts:
  - δ-connection
  - Meta-Curvature
  - Meta-Ricci
  - Deviational Geometry
block_type: paragraph
excerpt: 'Deviational geometry defines: 1. The δ-connection...'
```

**Fields:**
- `id` - Short card ID (e.g., GEN0-079)
- `location` - Full location code
- `source` - Relative path to source file
- `lines` - Line range in source (e.g., 1163-1188)
- `heading` - Immediate heading text
- `parent_heading` - Parent section (if nested)
- `concepts` - Extracted key terms and symbols
- `block_type` - paragraph, list, table, code, equation
- `excerpt` - First ~200 chars of content

## Searching the Catalog

### Using grep

```bash
# Find all cards mentioning "Box"
grep -i "box" catalog/indexes/cards.jsonl

# Find location codes for axioms
grep -i "axiom" catalog/indexes/location-index.txt

# Search card excerpts
grep -i "meta-time" catalog/indexes/cards.jsonl
```

### Using jq (JSON queries)

```bash
# Extract all unique concepts
jq -r '.concepts[]' catalog/indexes/cards.jsonl | sort | uniq

# Count cards by concept
jq -r '.concepts[]' catalog/indexes/cards.jsonl | sort | uniq -c | sort -nr

# Find all cards with "Theorem" in heading
jq 'select(.heading | contains("Theorem"))' catalog/indexes/cards.jsonl

# Get all cards from genesis-0
jq 'select(.source | startswith("genesis-0"))' catalog/indexes/cards.jsonl
```

### Using ripgrep (rg)

```bash
# Search all card files
rg -i "polarity" catalog/cards/

# Search with context
rg -i "box algebra" catalog/cards/ -A 3

# Find cards by block type
rg "block_type: equation" catalog/cards/
```

## CLI Commands Reference

### build
Rebuild the entire catalog from scratch.

```bash
python hgg-index.py build
```

Equivalent to running: `ingest` → `segment` → `cards` in sequence.

### ingest
Scan and register all source markdown files.

```bash
python hgg-index.py ingest
```

Creates `catalog/sources.json` with checksums and metadata.

### segment
Split sources into semantic blocks.

```bash
python hgg-index.py segment
```

Creates `catalog/indexes/segments.jsonl` and `location-index.txt`.

### cards
Generate YAML catalog cards from segments.

```bash
python hgg-index.py cards
```

Creates individual YAML cards in `catalog/cards/by-source/`.

### ls
List catalog cards.

```bash
# List all cards
python hgg-index.py ls

# Limit results
python hgg-index.py ls --limit 50

# Filter by source
python hgg-index.py ls --source genesis-0
python hgg-index.py ls --source intake
```

### show
Display card details.

```bash
# Show card metadata
python hgg-index.py show GEN0-001

# Show full content from source file
python hgg-index.py show GEN0-001 --verbose
python hgg-index.py show GEN0-001 -v
```

You can use either card ID or location code:

```bash
python hgg-index.py show GEN0-079
python hgg-index.py show genesis-0/feynman-rules::0-context::b1
```

### stats
Show catalog statistics.

```bash
python hgg-index.py stats
```

Displays:
- Total source files
- Total segments
- Total cards
- Cards by directory

## Advanced Usage

### Custom Source/Catalog Directories

```bash
python hgg-index.py build --source-dir my-docs --catalog-dir my-catalog
```

### Incremental Updates

To update after modifying sources:

```bash
# Full rebuild (recommended)
python hgg-index.py build

# Or step-by-step
python hgg-index.py ingest    # Re-scan sources
python hgg-index.py segment   # Re-segment changed files
python hgg-index.py cards     # Regenerate cards
```

### Querying by Location Code

Location codes are stable references you can use in other tools:

```bash
# Get source file and line numbers
grep "genesis-0/tri-unity-theorem::objects-primitives::b1" catalog/indexes/segments.jsonl
```

### Concept Extraction

The catalog automatically extracts:
- Greek symbols (δ, Φ, Π, Ψ, Σ, etc.)
- Title-cased multi-word terms (Box Algebra, Meta-Genesis)
- Hyphenated technical terms (Meta-Time, δ-connection)
- Mathematical operators (Box, Operator, Field, Mode)
- Terms in backticks or bold

View all concepts:

```bash
jq -r '.concepts[]' catalog/indexes/cards.jsonl | sort | uniq > all-concepts.txt
```

## How Segmentation Works

### Heading-Based Splitting

Each markdown heading creates a new context:

```markdown
# Chapter 1
Content under chapter 1

## Section 1.1
Content under section 1.1

### Subsection 1.1.1
Content under subsection
```

Creates segments with heading chains:
- `chapter-1::b1`
- `chapter-1::section-1-1::b1`
- `chapter-1::section-1-1::subsection-1-1-1::b1`

### Block Types

Each segment is classified:
- **paragraph** - Regular text blocks
- **list** - Bulleted or numbered lists
- **table** - Markdown tables
- **code** - Code fences (```)
- **equation** - Math blocks ($$)

### Block Sequence Numbers

Blocks under the same heading are numbered sequentially:

```markdown
## My Heading
First paragraph.    → my-heading::b1
Second paragraph.   → my-heading::b2
- List item         → my-heading::b3
Third paragraph.    → my-heading::b4
```

## Catalog Maintenance

### Regenerating the Catalog

The catalog is designed to be disposable:

```bash
# Delete and rebuild
rm -rf catalog
python hgg-index.py build
```

### Checking for Changes

Compare source checksums:

```bash
# Save old checksums
cp catalog/sources.json catalog/sources.json.old

# Rebuild
python hgg-index.py ingest

# Diff
diff catalog/sources.json.old catalog/sources.json
```

### Version Control

The catalog can be committed to git:

```bash
git add catalog/
git commit -m "Update catalog index"
```

Or excluded if you regenerate on demand:

```bash
# .gitignore
catalog/
```

## Tips & Tricks

### Find Cards by Line Number

If you know a source file and line number:

```bash
# Find which card contains line 150 of a file
jq 'select(.source == "genesis-0\\Tri-Unity_Theorem.md") |
    select(.lines | split("-")[0] | tonumber <= 150) |
    select(.lines | split("-")[1] | tonumber >= 150)' \
    catalog/indexes/cards.jsonl
```

### Export to CSV

```bash
# Simple CSV export
jq -r '[.id, .heading, .source, .lines] | @csv' catalog/indexes/cards.jsonl > cards.csv
```

### Count Segments per File

```bash
jq -r '.source' catalog/indexes/segments.jsonl | sort | uniq -c | sort -nr
```

### Find Longest Segments

```bash
jq 'select(.lines) | . + {length: (.lines | split("-") |
    (.[1] | tonumber) - (.[0] | tonumber))} |
    select(.length > 50) | [.id, .heading, .length]' \
    catalog/indexes/segments.jsonl
```

## Troubleshooting

### No cards generated

Check that source files exist:
```bash
ls HGG-/*.md
```

### Unicode errors on Windows

The tool handles Greek symbols and math notation. If you see encoding errors, ensure your terminal supports UTF-8.

### Location codes too long

Very deeply nested headings create long location codes. Consider flattening document structure or using shorter heading text.

### Missing concepts

Concept extraction is pattern-based. To improve:
- Use consistent capitalization for technical terms
- Mark key terms with backticks or bold
- Use standard Greek symbols

## Next Steps

After building your catalog, consider:

1. **Alias mapping** - Add Am154nb2-style IDs to cards
2. **Conversational cleaning** - Filter ChatGPT dialogue patterns
3. **Axiom detection** - Tag theorem/axiom blocks
4. **Semantic clustering** - Group related concepts
5. **Dependency graphs** - Map concept relationships

See `docs/semantic_indexing_design.md` for the full vision.

---

**Questions?** The catalog is just files - explore with `ls`, `grep`, `jq`, or your favorite text tools.
