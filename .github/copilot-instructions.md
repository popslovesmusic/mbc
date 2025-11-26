# GitHub Copilot Instructions

This repository contains a semantic catalog system for Meta-Genesis physics theory.

## Context
- 81 markdown source files in `HGG-/` (ChatGPT transcripts)
- 11,429 semantic blocks indexed in `catalog/`
- Python-based indexing system in `hgg_index/`

## Key Information
- **Never modify** files in `HGG-/` directory (sacred sources)
- Catalog data in `catalog/indexes/*.jsonl` (JSONL format)
- HTML browser in `catalog-html/index.html`

## Common Operations
```python
# Load all cards
import json
with open('catalog/indexes/cards.jsonl') as f:
    cards = [json.loads(line) for line in f]

# Search by concept
results = [c for c in cards if 'Meta-Time' in c.get('concepts', [])]
```

## Documentation
See `AGENT.md` for complete agent instructions and examples.

## Content Domain
Mathematical physics, δ-geometry, Box Calculus, quantum field theory projections, Meta-Time ontology.
