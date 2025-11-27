"""Review contradictions and ambiguities in the catalog"""

import json
from pathlib import Path
from typing import List, Dict, Optional


def load_segments_map() -> Dict[str, Dict]:
    """Load segments indexed by location"""
    segments_file = Path("catalog/indexes/segments.jsonl")

    if not segments_file.exists():
        return {}

    segments_map = {}
    with open(segments_file, 'r', encoding='utf-8') as f:
        for line in f:
            segment = json.loads(line)
            segments_map[segment['location_code']] = segment

    return segments_map


def load_issues(issue_type: str = "contradictions", min_severity: float = 0.0, max_results: int = None) -> List[Dict]:
    """Load cards with contradictions or ambiguity

    Args:
        issue_type: "contradictions" or "ambiguity"
        min_severity: Minimum severity threshold (0.0-1.0)
        max_results: Maximum number of results to return

    Returns:
        List of cards with issues
    """
    cards_file = Path("catalog/indexes/cards-enhanced.jsonl")

    if not cards_file.exists():
        print(f"Enhanced cards not found at {cards_file}")
        return []

    issues = []
    flag_field = 'has_contradictions' if issue_type == "contradictions" else 'has_ambiguity'

    with open(cards_file, 'r', encoding='utf-8') as f:
        for line in f:
            card = json.loads(line)

            if card.get(flag_field) and card.get('max_severity', 0) >= min_severity:
                issues.append(card)

    # Sort by severity (highest first)
    issues.sort(key=lambda c: c.get('max_severity', 0), reverse=True)

    if max_results:
        issues = issues[:max_results]

    return issues


def get_full_content(location: str, segments_map: Dict[str, Dict]) -> Optional[str]:
    """Get full content for a card by looking up its segment"""
    segment = segments_map.get(location)
    if segment:
        return segment.get('content', '')
    return None


def export_review_report(issue_type: str = "contradictions", min_severity: float = 0.3,
                        output_file: str = None, max_items: int = 50):
    """Export issues as markdown report for review

    Args:
        issue_type: "contradictions" or "ambiguity"
        min_severity: Minimum severity to include
        output_file: Output file path
        max_items: Maximum items to include (to keep file size reasonable)
    """
    if output_file is None:
        output_file = f"reports/{issue_type}_review.md"

    # Load data
    issues = load_issues(issue_type=issue_type, min_severity=min_severity, max_results=max_items)
    segments_map = load_segments_map()

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    issue_label = "Contradictions" if issue_type == "contradictions" else "Ambiguous Blocks"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {issue_label} Review Report\n\n")
        f.write(f"**Total {issue_label}** (severity >= {min_severity}): {len(issues)}\n\n")

        # Group by severity
        high = [c for c in issues if c.get('max_severity', 0) > 0.7]
        medium = [c for c in issues if 0.3 < c.get('max_severity', 0) <= 0.7]
        low = [c for c in issues if c.get('max_severity', 0) <= 0.3]

        f.write(f"- **High Severity** (> 0.7): {len(high)}\n")
        f.write(f"- **Medium Severity** (0.3-0.7): {len(medium)}\n")
        f.write(f"- **Low Severity** (< 0.3): {len(low)}\n\n")

        if len(issues) > max_items:
            f.write(f"*Note: Showing top {max_items} by severity*\n\n")

        f.write("---\n\n")

        for i, card in enumerate(issues, 1):
            severity = card.get('max_severity', 0)
            severity_label = "🔴 HIGH" if severity > 0.7 else "🟡 MEDIUM" if severity > 0.3 else "🟢 LOW"

            f.write(f"## {i}. {card['id']} - {severity_label} ({severity:.2f})\n\n")
            f.write(f"**Heading**: {card['heading']}\n\n")
            f.write(f"**Location**: `{card['location']}`\n\n")

            # Extract source file
            source_parts = card['location'].split('::')
            if len(source_parts) >= 1:
                source_file = source_parts[0]
                f.write(f"**Source File**: `HGG-/{source_file}.md`\n\n")

            if card.get('aliases'):
                f.write(f"**Aliases**: {', '.join(card['aliases'])}\n\n")

            if card.get('tags'):
                f.write(f"**Tags**: {', '.join(card.get('tags', []))}\n\n")

            # Show excerpt
            f.write("**Excerpt**:\n\n")
            f.write(f"> {card.get('excerpt', 'No excerpt')}\n\n")

            # Try to get full content from segments
            full_content = get_full_content(card['location'], segments_map)
            if full_content:
                f.write("**Full Content**:\n\n")
                f.write("```\n")
                # Truncate very long content
                if len(full_content) > 1500:
                    f.write(full_content[:1500])
                    f.write("\n... [content truncated - see source file for full text]\n")
                else:
                    f.write(full_content)
                f.write("\n```\n\n")

            # Concepts for context
            if card.get('concepts'):
                concepts = ', '.join(card.get('concepts', [])[:10])
                f.write(f"**Key Concepts**: {concepts}\n\n")

            f.write("**Your Evaluation**:\n\n")
            f.write("- [ ] True issue - needs revision\n")
            f.write("- [ ] False positive - content is fine\n")
            f.write("- [ ] Needs clarification\n\n")
            f.write("**Notes**: _[Add your evaluation notes here]_\n\n")

            f.write("---\n\n")

    print(f"[OK] {issue_label} review report exported to {output_path}")
    print(f"\nReport contains {len(issues)} items for review")
    print(f"\nNext steps:")
    print(f"  1. Open {output_path}")
    print(f"  2. Review each item")
    print(f"  3. Check the boxes and add notes")
    print(f"  4. Use the source file paths to see full context if needed")

    return str(output_path)


def quick_summary():
    """Show quick summary of all issues"""
    print("=== HGG Catalog Quality Issues Summary ===\n")

    # Contradictions
    contradictions = load_issues(issue_type="contradictions", min_severity=0.0)
    contr_high = sum(1 for c in contradictions if c.get('max_severity', 0) > 0.7)
    contr_med = sum(1 for c in contradictions if 0.3 < c.get('max_severity', 0) <= 0.7)
    contr_low = sum(1 for c in contradictions if c.get('max_severity', 0) <= 0.3)

    print(f"Contradictions: {len(contradictions)} total")
    print(f"  - High (> 0.7):   {contr_high}")
    print(f"  - Medium (0.3-0.7): {contr_med}")
    print(f"  - Low (< 0.3):    {contr_low}")

    # Ambiguity
    ambiguity = load_issues(issue_type="ambiguity", min_severity=0.0)
    ambig_high = sum(1 for c in ambiguity if c.get('max_severity', 0) > 0.7)
    ambig_med = sum(1 for c in ambiguity if 0.3 < c.get('max_severity', 0) <= 0.7)
    ambig_low = sum(1 for c in ambiguity if c.get('max_severity', 0) <= 0.3)

    print(f"\nAmbiguous Blocks: {len(ambiguity)} total")
    print(f"  - High (> 0.7):   {ambig_high}")
    print(f"  - Medium (0.3-0.7): {ambig_med}")
    print(f"  - Low (< 0.3):    {ambig_low}")

    print(f"\nRecommendation:")
    print(f"  Review high-severity issues first:")
    print(f"    python review_issues.py contradictions 0.7")
    print(f"    python review_issues.py ambiguity 0.7")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        # No args - show summary
        quick_summary()

    elif sys.argv[1] in ["contradictions", "ambiguity"]:
        issue_type = sys.argv[1]
        min_severity = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
        max_items = int(sys.argv[3]) if len(sys.argv) > 3 else 50

        export_review_report(
            issue_type=issue_type,
            min_severity=min_severity,
            max_items=max_items
        )

    elif sys.argv[1] == "list":
        issue_type = sys.argv[2] if len(sys.argv) > 2 else "contradictions"
        min_severity = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 20

        issues = load_issues(issue_type=issue_type, min_severity=min_severity, max_results=limit)

        issue_label = "Contradictions" if issue_type == "contradictions" else "Ambiguous blocks"
        print(f"\nTop {len(issues)} {issue_label} (severity >= {min_severity}):\n")

        for i, card in enumerate(issues, 1):
            sev = card.get('max_severity', 0)
            heading = card['heading'][:60].encode('ascii', 'replace').decode('ascii')
            source = card['location'].split('::')[0][:20]
            print(f"{i:3}. [{sev:.2f}] {card['id']:12} {source:20} {heading}")

    else:
        print("HGG Catalog Quality Issue Reviewer\n")
        print("Usage:")
        print("  python review_issues.py")
        print("    Show summary of all issues\n")
        print("  python review_issues.py contradictions [min_severity] [max_items]")
        print("    Export contradictions review report (default: severity >= 0.3, max 50 items)\n")
        print("  python review_issues.py ambiguity [min_severity] [max_items]")
        print("    Export ambiguity review report\n")
        print("  python review_issues.py list [contradictions|ambiguity] [min_severity] [limit]")
        print("    List issues to console\n")
        print("Examples:")
        print("  python review_issues.py contradictions 0.7 25")
        print("  python review_issues.py ambiguity 0.5")
        print("  python review_issues.py list contradictions 0.7 10")
