# HGG Index - Quick Reference

## One-Line Commands

```bash
# Build everything
python hgg-index.py build

# View stats
python hgg-index.py stats

# List 20 cards
python hgg-index.py ls --limit 20

# Show card
python hgg-index.py show GEN0-001

# Show with full content
python hgg-index.py show GEN0-001 -v
```

## Grep Patterns

```bash
# Find cards about Box
grep -i "box" catalog/indexes/cards.jsonl

# Find axioms
grep -i "axiom" catalog/indexes/cards.jsonl

# Find by location
grep "genesis-0" catalog/indexes/location-index.txt

# Find equations
grep "block_type: equation" catalog/cards/by-source/**/*.yaml
```

## JQ Queries

```bash
# All unique concepts
jq -r '.concepts[]' catalog/indexes/cards.jsonl | sort | uniq

# Concept frequency
jq -r '.concepts[]' catalog/indexes/cards.jsonl | sort | uniq -c | sort -nr | head -20

# Cards with "Theorem"
jq 'select(.heading | contains("Theorem"))' catalog/indexes/cards.jsonl

# Cards from genesis-0
jq 'select(.source | startswith("genesis-0"))' catalog/indexes/cards.jsonl

# Export to CSV
jq -r '[.id, .heading, .source] | @csv' catalog/indexes/cards.jsonl > cards.csv
```

## Card ID Patterns

- `GEN0-001` = genesis-0, card #1
- `GEN5-042` = genesis-5, card #42
- `INTK-012` = intake, card #12
- `SPEC-005` = special, card #5

## Location Code Format

```
genesis-0/tri-unity-theorem::objects-primitives::b1
├─ Directory: genesis-0
├─ File: tri-unity-theorem
├─ Heading chain: objects-primitives
└─ Block: b1
```

## File Locations

- Sources: `HGG-/**/*.md`
- Cards: `catalog/cards/by-source/**/*.yaml`
- Flat index: `catalog/indexes/cards.jsonl`
- Segments: `catalog/indexes/segments.jsonl`
- Locations: `catalog/indexes/location-index.txt`
- Registry: `catalog/sources.json`

## Rebuild Workflow

```bash
rm -rf catalog               # Delete old catalog
python hgg-index.py build    # Rebuild from sources
git add catalog              # (Optional) commit to git
```
