# How to Find and Evaluate Contradictions & Ambiguities

## Quick Summary

Your catalog has **1,528 contradictions** and **895 ambiguous blocks** detected automatically. Here's how to review them:

## Method 1: Review Reports (RECOMMENDED)

**Generate structured review reports with full content:**

```bash
# Top 25 contradictions with severity >= 0.6
python review_issues.py contradictions 0.6 25

# Top 25 ambiguous blocks
python review_issues.py ambiguity 0.6 25

# All contradictions above threshold (default 0.3)
python review_issues.py contradictions 0.3 100
```

**Output:** `reports/contradictions_review.md` and `reports/ambiguity_review.md`

Each entry shows:
- Card ID and heading
- Severity score (0.3-0.7 range)
- Source file location
- Full content
- Key concepts
- Checkboxes for your evaluation

**Then:**
1. Open the `.md` file in your editor
2. Read each contradiction
3. Check boxes: true issue / false positive / needs clarification
4. Add evaluation notes
5. Use source file paths to see full context

## Method 2: Quick List View

**List contradictions to console:**

```bash
# Show top 20 contradictions
python review_issues.py list contradictions 0.0 20

# Show top 10 ambiguous blocks
python review_issues.py list ambiguity 0.0 10
```

## Method 3: CSV Export (Spreadsheet Analysis)

```bash
# Already generated: reports/metrics-cards.csv (3MB)
# Open in Excel/LibreOffice and filter:
#   - Column: Has_Contradictions = True
#   - Column: Max_Severity >= 0.6
```

## Method 4: Direct Python/JQ Queries

**Python one-liner to list contradictions:**

```bash
python -c "import json; cards = [json.loads(line) for line in open('catalog/indexes/cards-enhanced.jsonl')]; contradictions = [c for c in cards if c.get('has_contradictions')]; [print(f\"{c['id']:12} {c.get('max_severity', 0):.2f}  {c['location'].split('::')[0][:30]:30}  {c['heading'][:50]}\") for c in sorted(contradictions, key=lambda x: x.get('max_severity', 0), reverse=True)[:20]]"
```

**Using jq (if installed):**

```bash
# List all contradictions with severity > 0.6
grep -h "has_contradictions" catalog/indexes/cards-enhanced.jsonl | \
  jq -r 'select(.max_severity > 0.6) | "\(.id) [\(.max_severity)] \(.heading[:60])"'
```

## Method 5: HTML Browser

Open `catalog-html/index.html` and search for cards tagged with:
- `conflicted` (has contradictions)
- `ambiguous` (has ambiguity)

## Understanding Severity Scores

**Severity ranges:**
- **0.7-1.0**: High (requires review)
- **0.3-0.7**: Medium (likely issues)
- **0.0-0.3**: Low (minor/false positives)

**Your catalog:**
- All contradictions: 0.3-0.7 range (medium)
- All ambiguity: 0.3-0.7 range (medium)

## What Triggers Contradiction Detection?

The contradiction detector looks for:
- Conflicting terms: "always" vs "sometimes", "all" vs "some", "never" vs "sometimes"
- Negations with qualifiers: "not always", "not necessarily", "may not"
- Hedge phrases: "sort of", "kind of", "in a way"
- Uncertainty markers: "unclear", "uncertain", "ambiguous"

## What Triggers Ambiguity Detection?

The ambiguity detector looks for:
- Modal qualifiers: "might", "could", "possibly", "perhaps"
- Approximations: "approximately", "roughly", "about"
- Vague terms: "somewhat", "fairly", "relatively"
- Questions in declarative blocks

## Example Workflow

```bash
# 1. See overall summary
python review_issues.py

# 2. Generate review report for top issues
python review_issues.py contradictions 0.6 50

# 3. Open and review
# Open: reports/contradictions_review.md

# 4. For each item:
#    - Read the content
#    - Check source file if needed: HGG-/genesis-X/filename.md
#    - Mark checkbox: true issue / false positive / needs clarification
#    - Add notes on what needs to change

# 5. After review, you have a prioritized list of edits needed
```

## Files Generated

- `reports/contradictions_review.md` - Structured review report for contradictions
- `reports/ambiguity_review.md` - Structured review report for ambiguities
- `reports/metrics-cards.csv` - Full data (3MB) for custom analysis
- `catalog-html/analytics.html` - Visual dashboard showing counts

## Quick Stats

From your catalog:
- **Total cards**: 11,429
- **Cards with contradictions**: 1,528 (13.4%)
- **Cards with ambiguity**: 895 (7.8%)
- **Severity range**: All in 0.3-0.7 (medium)

**Top directories with contradictions:**
- genesis-20: 143 blocks
- genesis-17: 105 blocks
- intake: 212 blocks

## Next Steps

1. Run: `python review_issues.py contradictions 0.6 25`
2. Open: `reports/contradictions_review.md`
3. Review each item systematically
4. Decide: Keep as-is / Clarify / Revise
5. Track decisions in the report file

Most contradictions are likely **valid content** describing paradoxes, dualities, or dialectical concepts in Meta-Genesis theory. The detector may flag theoretical contradictions that are intentional!
