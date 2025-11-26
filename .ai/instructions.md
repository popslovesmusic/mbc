# AI Agent Instructions

**See**: `../AGENT.md` for complete instructions

## System
HGG Semantic Catalog - Knowledge base indexing system for Meta-Genesis theory

## Data Location
- Primary: `catalog/indexes/cards.jsonl` (11,429 cards)
- Full content: `catalog/indexes/segments.jsonl`
- Sources (read-only): `HGG-/`

## Quick Start
```python
import json
cards = [json.loads(line) for line in open('catalog/indexes/cards.jsonl')]
results = [c for c in cards if 'axiom' in c['heading'].lower()]
```

## Rules
- Read-only on HGG-/ directory
- Catalog is regenerable (never critical data loss)
- Always use UTF-8 encoding (Greek symbols: δ, Φ, Π)
- Cite using location codes: `genesis-0/file::heading::b1`
