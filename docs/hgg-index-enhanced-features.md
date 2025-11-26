# HGG Index - Enhanced Features Documentation

## Overview

The enhanced card generation system adds deep semantic analysis to every segment in your catalog. This includes:

1. **Conversational Text Detection** - Identifies ChatGPT dialogue patterns
2. **Axiom & Theorem Detection** - Recognizes formal mathematical statements
3. **Alias Generation** - Creates stable Am154nb2-format identifiers
4. **Enhanced Concept Extraction** - Extracts technical terms, symbols, and domain concepts
5. **Contradiction & Ambiguity Detection** - Flags inconsistencies and uncertain language

## Enhanced Card Fields

Each enhanced card contains the following metrics:

### Basic Fields
- `id` - Card ID (e.g., GEN0-001)
- `location` - Full location code
- `source` - Relative path to source file
- `lines` - Line range (e.g., "150-175")
- `heading` - Section heading
- `parent_heading` - Parent section (if nested)
- `block_type` - paragraph, list, table, code, equation
- `excerpt` - First ~200 chars

### Semantic Metrics
- `concepts` - List of extracted concepts (up to 15)
- `aliases` - Am154nb2-format stable identifiers
- `tags` - Semantic tags (axiom, sealed, definitive, ambiguous, etc.)
- `concept_density` - Concepts per 100 words

### Formal Statement Detection
- `is_formal` - Boolean: contains axiom/theorem/etc
- `statement_type` - axiom, theorem, lemma, corollary, proposition, definition
- `axiom_count` - Number of axioms in block
- `theorem_count` - Number of theorems in block
- `identifiers` - List of formal IDs (A1, GA-8, etc.)

### Quality Metrics
- `conversational_score` - 0.0 = technical, 1.0 = very conversational
- `is_technical` - Boolean: contains equations, proofs, formal notation
- `has_contradictions` - Boolean: contains conflicting statements
- `has_ambiguity` - Boolean: contains uncertain/ambiguous language
- `is_definitive` - Boolean: strong, unqualified statement
- `max_severity` - 0.0 = certain, 1.0 = very uncertain

## Feature Details

### 1. Conversational Text Detection

Identifies patterns common in ChatGPT transcripts:

**Detected Patterns:**
- **ChatGPT Openings**: "Here's", "Let's", "I'll", "I'm", "You can"
- **Dialogue Markers**: "User:", "Assistant:", "Q:", "A:"
- **Meta-Commentary**: "note to self", "TODO", "please see"
- **Instructional**: "Let me explain", "Consider", "Think about"
- **Rhetorical Questions**: Questions directed at reader

**Conversational Score:**
- `0.0` - Pure technical content
- `0.3` - Minor conversational elements
- `0.6` - Mixed technical/conversational
- `1.0` - Highly conversational

**Example:**
```markdown
Block: "Here's how δ-geometry works: Let me explain..."
  → conversational_score: 0.8
  → is_technical: True (has Greek symbols)
```

### 2. Axiom & Theorem Detection

Recognizes formal mathematical statements:

**Detected Formats:**
- Standard: `Axiom A1:`, `Theorem 3:`, `Definition:`
- Boxed: `**Axiom A1**`, `***Theorem***`
- IGSOA: `GA-8`, `META-PHYSICS AXIOM BOX`, `SEALED`
- Parenthetical: `(A1)`, `(Theorem 3)`

**Identifiers Extracted:**
- `A1`, `A2`, `A3` - Axiom numbers
- `GA-8` - Meta-Einstein equation
- `META-TIME`, `META-PHYSICS` - IGSOA patterns

**Tags Generated:**
- `axiom`, `theorem`, `lemma`, `corollary`, `proposition`
- `axiom-box` - Boxed axiom format
- `sealed` - Sealed axiom box
- `proof` - Contains proof

**Example:**
```yaml
heading: "Axiom A1 (Deviation Necessity)"
is_formal: true
statement_type: axiom
axiom_count: 1
identifiers: ['A1']
tags: ['axiom', 'deviation-necessity']
aliases: ['Am001nb2']
```

### 3. Alias Generation

Creates stable identifiers in Am154nb2 format:

**Format Breakdown:**
```
Am154nb2
││└┴┘ └─ Version number (optional)
││ └─── 2-3 char fingerprint
│└───── 3-digit hash
└────── Prefix (Am=axiom, Th=theorem, Cn=concept, Bk=block)
```

**Prefixes:**
- `Am` - Axiom
- `Th` - Theorem
- `Lm` - Lemma
- `Cr` - Corollary
- `Pr` - Proposition
- `Df` - Definition
- `Cn` - Concept
- `Bk` - Generic block

**Generation Methods:**
1. **From Identifier**: `A1` → `Am001a1`
2. **From Content Hash**: SHA256 hash → `Bk892xk`
3. **From Fingerprint**: First letters of key words → `Cn445bo` (Box)

**Existing Aliases:**
The system also extracts any existing aliases from content (e.g., `Am154nb2` mentioned in text).

### 4. Enhanced Concept Extraction

Extracts multiple types of concepts:

**Greek Symbols:**
- Single: `δ`, `Φ`, `Π`, `Ψ`, `Σ`
- Compound: `δΨ₀`, `Φ-projection`, `Π-evaluation`

**Math Symbols:**
- `∀`, `∃`, `∈`, `∉`, `⊂`, `⊃`, `∫`, `∂`, `∇`, `∆`, `∑`, `∏`

**Domain Terms:**
- Multi-word: `Box Calculus`, `Meta-Genesis`, `Foundation Layer`
- Hyphenated: `Meta-Time`, `δ-geometry`, `Chromatic Mode`

**Operators:**
- `Operator`, `Functor`, `Transform`, `Field`, `Mode`, `Box`, `Gate`

**Formal Markers:**
- `Axiom`, `Theorem`, `Lemma`, `Proof`

**Marked Terms:**
- In backticks: `` `Box` ``
- In bold: `**Operator**`
- In italic: `*field*`

**Scoring:**
Concepts are scored and sorted by:
- Frequency in content
- Length (longer = more specific)
- Category (domain term > operator > symbol)
- Context (hyphenated terms ranked higher)

### 5. Contradiction & Ambiguity Detection

Flags inconsistent or uncertain language:

**Negation Patterns:**
- Words: not, no, none, never, cannot, won't, don't
- Symbols: ¬, ~, `\neg`

**Conflict Detection:**
Finds opposing terms in same block:
- `always` vs `sometimes`
- `all` vs `some`
- `unique` vs `multiple`
- `equivalent` vs `different`
- `constant` vs `variable`

**Ambiguity Markers:**
- maybe, perhaps, possibly, probably
- seems, appears, might be
- unclear, ambiguous, uncertain
- roughly, approximately, about

**Qualifiers:**
- generally, typically, usually
- in most cases, by default
- somewhat, rather, fairly
- essentially, basically

**Contradiction Indicators:**
- however, but, although, despite
- on the other hand, conversely
- except, unless, without

**Severity Scores:**
- `0.0` - Certain, definitive
- `0.2` - Minor qualifiers
- `0.5` - Ambiguous language
- `0.7` - Conflicting terms
- `1.0` - High uncertainty

**Tags Generated:**
- `conflicted` - Contains contradictions
- `ambiguous` - Uncertain language
- `qualified` - Hedging language
- `definitive` - Strong, unqualified
- `high-uncertainty` - Severity > 0.7
- `low-uncertainty` - Severity < 0.2

**Examples:**
```markdown
"The operator is always commutative but sometimes associative."
  → has_contradictions: True
  → max_severity: 0.7
  → tags: ['conflicted']

"Axiom A1: δΨ₀ ≠ 0"
  → has_ambiguity: False
  → is_definitive: True
  → max_severity: 0.0
  → tags: ['definitive', 'low-uncertainty']
```

## Using Enhanced Cards

### Generate Enhanced Cards

```bash
# Generate enhanced cards for all segments
python -c "
from hgg_index.segment import Segment
from hgg_index.card_enhanced import generate_enhanced_cards
import json

# Load segments
segments = []
with open('catalog/indexes/segments.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        seg = Segment(**json.loads(line))
        segments.append(seg)

# Generate enhanced cards
generate_enhanced_cards(segments)
"
```

This creates:
- `catalog/cards/by-source/*/` - Enhanced YAML cards
- `catalog/indexes/cards-enhanced.jsonl` - Enhanced flat index

### Query Enhanced Cards

```bash
# Find all axioms
jq 'select(.statement_type == "axiom")' catalog/indexes/cards-enhanced.jsonl

# Find contradictions
jq 'select(.has_contradictions == true)' catalog/indexes/cards-enhanced.jsonl

# Find ambiguous statements
jq 'select(.has_ambiguity == true)' catalog/indexes/cards-enhanced.jsonl

# Find definitive statements (high certainty)
jq 'select(.is_definitive == true)' catalog/indexes/cards-enhanced.jsonl

# Find conversational blocks
jq 'select(.conversational_score > 0.5)' catalog/indexes/cards-enhanced.jsonl

# Find formal, technical blocks
jq 'select(.is_formal == true and .is_technical == true)' catalog/indexes/cards-enhanced.jsonl

# Get all aliases
jq -r '.aliases[]' catalog/indexes/cards-enhanced.jsonl | sort | uniq

# Find by tag
jq 'select(.tags[] | contains("axiom"))' catalog/indexes/cards-enhanced.jsonl

# Find high-uncertainty blocks
jq 'select(.max_severity > 0.7)' catalog/indexes/cards-enhanced.jsonl

# Count by statement type
jq -r '.statement_type' catalog/indexes/cards-enhanced.jsonl | sort | uniq -c
```

### Example Enhanced Card

```yaml
id: GEN0-168
location: genesis-0/tri-unity-theorem::tiny-intuition-translation::b1
source: genesis-0\Tri-Unity_Theorem_Equivalence_of___.md
lines: 150-175
heading: Tiny intuition translation (for outreach layer)
parent_heading: Tri-Unity Theorem

# Content
block_type: paragraph
excerpt: "δ says: 'something must happen.' Φ says: 'what happens forms..."

# Semantic
concepts:
  - Axiom
  - Box
  - Classical Physics
  - Tri-Unity
  - Unity Axiom Box
  - Π
  - Φ
  - δ
aliases:
  - Cn427tu
  - Am154nb2  # Found in text
tags:
  - definitive
  - low-uncertainty

# Formal
is_formal: false
statement_type: null
axiom_count: 0
theorem_count: 0
identifiers: []

# Quality
conversational_score: 0.40
is_technical: true
concept_density: 12.5
has_contradictions: false
has_ambiguity: false
is_definitive: true
max_severity: 0.15
```

## Performance Notes

Enhanced card generation takes ~3-5x longer than basic cards due to deep analysis:

- **Basic cards**: ~0.01s per card
- **Enhanced cards**: ~0.03-0.05s per card

For 11,429 cards:
- **Basic**: ~2 minutes
- **Enhanced**: ~5-10 minutes

## Next Steps

With enhanced cards, you can:

1. **Filter conversational noise**: Focus on technical blocks
2. **Find formal statements**: Build axiom/theorem index
3. **Track aliases**: Cross-reference concepts
4. **Detect contradictions**: Find inconsistencies
5. **Assess certainty**: Prioritize definitive statements
6. **Build dependency graphs**: Link related concepts via aliases

See `hgg-index-user-guide.md` for general catalog usage.
