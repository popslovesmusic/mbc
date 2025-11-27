"""Review contradictions detected in the catalog"""

import json
from pathlib import Path
from typing import List, Dict


def load_contradictions(min_severity: float = 0.0, max_results: int = None) -> List[Dict]:
    """Load cards with contradictions

    Args:
        min_severity: Minimum severity threshold (0.0-1.0)
        max_results: Maximum number of results to return

    Returns:
        List of cards with contradictions
    """
    cards_file = Path("catalog/indexes/cards-enhanced.jsonl")

    if not cards_file.exists():
        print(f"Enhanced cards not found at {cards_file}")
        print("Run: python -c 'from hgg_index.card_enhanced import generate_enhanced_cards; ...'")
        return []

    contradictions = []

    with open(cards_file, 'r', encoding='utf-8') as f:
        for line in f:
            card = json.loads(line)

            if card.get('has_contradictions') and card.get('max_severity', 0) >= min_severity:
                contradictions.append(card)

    # Sort by severity (highest first)
    contradictions.sort(key=lambda c: c.get('max_severity', 0), reverse=True)

    if max_results:
        contradictions = contradictions[:max_results]

    return contradictions


def print_contradiction_card(card: Dict, show_full_content: bool = False):
    """Print a contradiction card in readable format"""

    severity = card.get('max_severity', 0)
    severity_label = "HIGH" if severity > 0.7 else "MEDIUM" if severity > 0.3 else "LOW"

    print(f"\n{'='*80}")
    print(f"ID: {card['id']}")
    print(f"Location: {card['location']}")
    print(f"Heading: {card['heading']}")
    print(f"Severity: {severity:.2f} [{severity_label}]")
    print(f"Tags: {', '.join(card.get('tags', []))}")

    # Show aliases if available
    if card.get('aliases'):
        print(f"Aliases: {', '.join(card.get('aliases', []))}")

    print(f"\n--- Content Preview (first 500 chars) ---")
    content = card.get('content', '')
    preview = content[:500] + "..." if len(content) > 500 else content
    print(preview)

    if show_full_content and len(content) > 500:
        print(f"\n--- Full Content ---")
        print(content)

    # Show source file location for inspection
    source_parts = card['location'].split('::')
    if len(source_parts) >= 1:
        source_file = source_parts[0]
        print(f"\n--- Source ---")
        print(f"File: HGG-/{source_file}.md")
        print(f"Full location: {card['location']}")


def review_contradictions_interactive():
    """Interactive contradiction review"""

    print("=== HGG Catalog Contradiction Review ===\n")

    # Get severity filter
    print("Filter by severity:")
    print("  1. All (>= 0.0)")
    print("  2. Medium+ (>= 0.3)")
    print("  3. High only (>= 0.7)")
    choice = input("\nChoice [1-3] (or Enter for all): ").strip() or "1"

    severity_map = {
        "1": 0.0,
        "2": 0.3,
        "3": 0.7
    }
    min_severity = severity_map.get(choice, 0.0)

    # Load contradictions
    print(f"\nLoading contradictions with severity >= {min_severity}...")
    contradictions = load_contradictions(min_severity=min_severity)

    print(f"\nFound {len(contradictions)} contradictions")

    if not contradictions:
        return

    # Review loop
    current_idx = 0

    while current_idx < len(contradictions):
        card = contradictions[current_idx]

        print(f"\n\n[Card {current_idx + 1} of {len(contradictions)}]")
        print_contradiction_card(card)

        print(f"\n--- Commands ---")
        print("  n/next: Next card")
        print("  p/prev: Previous card")
        print("  f/full: Show full content")
        print("  s/save: Save this card ID to review list")
        print("  q/quit: Exit")

        cmd = input("\nCommand: ").strip().lower()

        if cmd in ['n', 'next', '']:
            current_idx += 1
        elif cmd in ['p', 'prev']:
            current_idx = max(0, current_idx - 1)
        elif cmd in ['f', 'full']:
            print_contradiction_card(card, show_full_content=True)
        elif cmd in ['s', 'save']:
            with open('contradiction_review_list.txt', 'a') as f:
                f.write(f"{card['id']}\t{card['location']}\t{card.get('max_severity', 0):.2f}\t{card['heading']}\n")
            print("[OK] Saved to contradiction_review_list.txt")
        elif cmd in ['q', 'quit']:
            break

    print("\n[OK] Review complete")


def export_contradictions_report(min_severity: float = 0.3, output_file: str = "reports/contradictions.md"):
    """Export contradictions as markdown report"""

    contradictions = load_contradictions(min_severity=min_severity)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Contradiction Review Report\n\n")
        f.write(f"**Total Contradictions** (severity >= {min_severity}): {len(contradictions)}\n\n")

        # Group by severity
        high = [c for c in contradictions if c.get('max_severity', 0) > 0.7]
        medium = [c for c in contradictions if 0.3 < c.get('max_severity', 0) <= 0.7]

        f.write(f"- **High Severity** (> 0.7): {len(high)}\n")
        f.write(f"- **Medium Severity** (0.3-0.7): {len(medium)}\n\n")

        f.write("---\n\n")

        for i, card in enumerate(contradictions, 1):
            severity = card.get('max_severity', 0)
            severity_label = "🔴 HIGH" if severity > 0.7 else "🟡 MEDIUM"

            f.write(f"## {i}. {card['id']} - {severity_label} ({severity:.2f})\n\n")
            f.write(f"**Heading**: {card['heading']}\n\n")
            f.write(f"**Location**: `{card['location']}`\n\n")
            f.write(f"**Source**: `HGG-/{card['location'].split('::')[0]}.md`\n\n")

            if card.get('aliases'):
                f.write(f"**Aliases**: {', '.join(card['aliases'])}\n\n")

            f.write(f"**Tags**: {', '.join(card.get('tags', []))}\n\n")

            f.write("**Content**:\n\n")
            f.write("```\n")
            content = card.get('content', '')
            preview = content[:800] + "\n... [truncated]" if len(content) > 800 else content
            f.write(preview)
            f.write("\n```\n\n")
            f.write("**Evaluation**: _[Add your notes here]_\n\n")
            f.write("---\n\n")

    print(f"[OK] Contradiction report exported to {output_path}")
    print(f"\nYou can now:")
    print(f"  1. Open {output_path} in a text editor")
    print(f"  2. Review each contradiction")
    print(f"  3. Add evaluation notes")

    return str(output_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "export":
            severity = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
            export_contradictions_report(min_severity=severity)
        elif cmd == "list":
            severity = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            contradictions = load_contradictions(min_severity=severity, max_results=limit)

            print(f"\nTop {len(contradictions)} contradictions (severity >= {severity}):\n")
            for i, card in enumerate(contradictions, 1):
                sev = card.get('max_severity', 0)
                heading = card['heading'][:60].encode('ascii', 'replace').decode('ascii')
                print(f"{i:3}. [{sev:.2f}] {card['id']:12} {heading}")
        else:
            print("Unknown command")
            print("\nUsage:")
            print("  python review_contradictions.py              # Interactive review")
            print("  python review_contradictions.py export [min_severity]  # Export report")
            print("  python review_contradictions.py list [min_severity] [limit]  # List contradictions")
    else:
        # Interactive mode
        review_contradictions_interactive()
