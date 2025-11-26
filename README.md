# MBC - Meta-Genesis Knowledge Base

This repository contains the Meta-Genesis Box Calculus (MBC) knowledge base and semantic indexing tools.

## Contents

- `HGG-/` - Source markdown files (genesis-0 through genesis-20, intake, special)
- `catalog/` - Generated card catalog index (regenerable)
- `hgg_index/` - Indexing and cataloging tools
- `docs/` - Documentation

## Quick Start

### Build the Card Catalog

```bash
python hgg-index.py build
```

This indexes all 81 markdown files and creates ~11,400+ catalog cards.

### Search the Catalog

```bash
# List cards
python hgg-index.py ls --limit 20

# Show card details
python hgg-index.py show GEN0-001

# Search with grep
grep -i "box algebra" catalog/indexes/cards.jsonl

# Query with jq
jq 'select(.heading | contains("Theorem"))' catalog/indexes/cards.jsonl
```

### View Statistics

```bash
python hgg-index.py stats
```

## HTML Catalog Browser

Interactive web interface for browsing the catalog:

```bash
python generate-html-catalog.py
# Opens: catalog-html/index.html
```

Features:
- 📊 **Analytics Dashboard** - Charts and visualizations
- 🔍 **Live Search** - Filter cards in real-time
- 📂 **Directory Navigation** - Browse by source
- 🔗 **Source Links** - Jump to exact line in source files
- 📈 **Metrics Visualization** - Concept frequency, distribution charts

## For AI Agents

**🤖 [AGENT.md](AGENT.md)** - Complete operational instructions for AI assistants

Quick context for agents:
- Data in `catalog/indexes/cards.jsonl` (11,429 entries)
- Sources read-only in `HGG-/`
- Load: `cards = [json.loads(line) for line in open('catalog/indexes/cards.jsonl')]`
- Search: `[c for c in cards if 'axiom' in c['heading'].lower()]`

Also see: `.cursorrules`, `.ai/instructions.md`, `.github/copilot-instructions.md`

## Documentation

- **[User Guide](docs/hgg-index-user-guide.md)** - CLI usage documentation
- **[Enhanced Features](docs/hgg-index-enhanced-features.md)** - Semantic analysis features
- **[HTML Catalog Guide](docs/html-catalog-guide.md)** - Web browser interface
- **[Quick Reference](docs/hgg-index-quick-reference.md)** - Command cheat sheet
- **[Design Document](docs/semantic_indexing_design.md)** - Architecture and vision
- **[Complete Summary](COMPLETE.md)** - Full implementation overview

## Card Catalog Structure

```
catalog/
├── sources.json              # Source file registry
├── indexes/
│   ├── cards.jsonl          # Flat card index (grep-friendly)
│   ├── segments.jsonl       # Full segment data
│   └── location-index.txt   # ID → location mapping
└── cards/
    └── by-source/           # Individual YAML cards
        ├── genesis-0/
        ├── genesis-1/
        ├── ...
        ├── intake/
        └── special/
```

## Location Code Format

Every semantic block has a stable location code:

```
genesis-0/tri-unity-theorem::objects-primitives::b1
│         │                  │                  └─ Block number
│         │                  └─ Heading chain
│         └─ Filename
└─ Directory
```

## CLI Commands

```bash
# Build entire catalog
python hgg-index.py build

# Individual steps
python hgg-index.py ingest      # Scan sources
python hgg-index.py segment     # Create segments
python hgg-index.py cards       # Generate cards

# Query
python hgg-index.py ls          # List cards
python hgg-index.py show ID     # Show card
python hgg-index.py stats       # Statistics

# Generate HTML browser
python generate-html-catalog.py  # Creates catalog-html/
```

## Card Format

Each card is a simple YAML file:

```yaml
id: GEN0-079
location: genesis-0/feynman-rules::0-context::b1
source: genesis-0\-Feynman_Rules__Interaction_Vertices.md
lines: 1163-1188
heading: '**0. Context**'
concepts:
  - δ-connection
  - Meta-Curvature
  - Meta-Ricci
block_type: paragraph
excerpt: 'Deviational geometry defines: 1. The δ-connection...'
```

## Philosophy

The catalog is a **card catalog**, not a database:

- **Sources are sacred** - Original files in `HGG-/` are never modified
- **Cards are ephemeral** - Can be regenerated from sources anytime
- **Simple files** - YAML, JSONL, plain text (grep-friendly, version-controllable)
- **Location codes** - Stable addressing for every semantic block

## Requirements

- Python 3.11+
- PyYAML 6.0+

## License

[Your license here]
