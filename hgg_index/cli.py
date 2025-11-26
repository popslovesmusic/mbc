#!/usr/bin/env python3
"""HGG Index CLI - Card catalog for semantic markdown library"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from hgg_index.ingest import ingest_sources, SourceRegistry
from hgg_index.segment import segment_sources, Segment
from hgg_index.card import generate_cards


def cmd_ingest(args):
    """Ingest source markdown files"""
    print("=== HGG Index: Ingest Sources ===\n")

    registry = ingest_sources(
        base_dir=args.source_dir,
        catalog_dir=args.catalog_dir
    )

    print(f"\n[OK] Ingested {len(registry.sources)} source files")


def cmd_segment(args):
    """Segment sources into blocks"""
    print("=== HGG Index: Segment Sources ===\n")

    # Load source registry
    registry = SourceRegistry(
        base_dir=args.source_dir,
        catalog_dir=args.catalog_dir
    )
    sources = registry.load()

    if not sources:
        print("No sources found. Run 'ingest' first.")
        return

    # Segment all files
    source_paths = [s.path for s in sources]
    segmenter = segment_sources(
        source_paths,
        base_dir=args.source_dir,
        catalog_dir=args.catalog_dir
    )

    print(f"\n[OK] Created {len(segmenter.segments)} segments")


def cmd_cards(args):
    """Generate catalog cards from segments"""
    print("=== HGG Index: Generate Cards ===\n")

    # Load segments
    segments_file = Path(args.catalog_dir) / "indexes" / "segments.jsonl"

    if not segments_file.exists():
        print(f"Segments not found at {segments_file}")
        print("Run 'segment' first.")
        return

    segments = []
    with open(segments_file, 'r', encoding='utf-8') as f:
        for line in f:
            seg_data = json.loads(line)
            segment = Segment(**seg_data)
            segments.append(segment)

    # Generate cards
    generate_cards(segments, catalog_dir=args.catalog_dir)

    print(f"\n[OK] Generated cards for {len(segments)} segments")


def cmd_build(args):
    """Build entire catalog from scratch (ingest + segment + cards)"""
    print("=== HGG Index: Build Complete Catalog ===\n")

    # Run all steps
    cmd_ingest(args)
    print("\n" + "="*60 + "\n")

    cmd_segment(args)
    print("\n" + "="*60 + "\n")

    cmd_cards(args)

    print("\n" + "="*60)
    print("[OK] Catalog build complete!")


def cmd_ls(args):
    """List cards"""
    print("=== HGG Index: List Cards ===\n")

    # Load card index
    cards_file = Path(args.catalog_dir) / "indexes" / "cards.jsonl"

    if not cards_file.exists():
        print(f"Cards not found at {cards_file}")
        print("Run 'cards' first.")
        return

    # Read and display cards
    cards = []
    with open(cards_file, 'r', encoding='utf-8') as f:
        for line in f:
            card = json.loads(line)
            cards.append(card)

    # Filter by source if specified
    if args.source:
        cards = [c for c in cards if args.source.lower() in c['source'].lower()]

    # Limit output
    limit = args.limit if args.limit else len(cards)
    cards_to_show = cards[:limit]

    print(f"Showing {len(cards_to_show)} of {len(cards)} cards\n")

    for card in cards_to_show:
        concepts_str = ', '.join(card['concepts'][:5])
        print(f"{card['id']}: {card['heading']}")
        print(f"  Location: {card['location']}")
        print(f"  Source: {card['source']}")
        if concepts_str:
            print(f"  Concepts: {concepts_str}")
        print()


def cmd_show(args):
    """Show details of a specific card"""
    print(f"=== HGG Index: Show Card {args.card_id} ===\n")

    # Load card index
    cards_file = Path(args.catalog_dir) / "indexes" / "cards.jsonl"

    if not cards_file.exists():
        print(f"Cards not found at {cards_file}")
        return

    # Find card
    card = None
    with open(cards_file, 'r', encoding='utf-8') as f:
        for line in f:
            c = json.loads(line)
            if c['id'] == args.card_id or c['location'] == args.card_id:
                card = c
                break

    if not card:
        print(f"Card '{args.card_id}' not found")
        return

    # Display card
    print(f"ID: {card['id']}")
    print(f"Location: {card['location']}")
    print(f"Source: {card['source']}")
    print(f"Heading: {card['heading']}")
    print(f"Concepts: {', '.join(card['concepts'])}")
    print(f"\nExcerpt:")
    print(f"  {card['excerpt']}")

    # If verbose, show full content from segment
    if args.verbose:
        segments_file = Path(args.catalog_dir) / "indexes" / "segments.jsonl"
        if segments_file.exists():
            with open(segments_file, 'r', encoding='utf-8') as f:
                for line in f:
                    seg = json.loads(line)
                    if seg['id'] == card['id']:
                        print(f"\nFull Content (lines {seg['start_line']}-{seg['end_line']}):")
                        print("-" * 60)
                        print(seg['content'])
                        print("-" * 60)
                        break


def cmd_stats(args):
    """Show catalog statistics"""
    print("=== HGG Index: Statistics ===\n")

    catalog_dir = Path(args.catalog_dir)

    # Load sources
    sources_file = catalog_dir / "sources.json"
    if sources_file.exists():
        with open(sources_file, 'r', encoding='utf-8') as f:
            sources_data = json.load(f)
        print(f"Sources: {sources_data['source_count']}")
    else:
        print("Sources: Not built")

    # Load segments
    segments_file = catalog_dir / "indexes" / "segments.jsonl"
    if segments_file.exists():
        segment_count = sum(1 for _ in open(segments_file, 'r', encoding='utf-8'))
        print(f"Segments: {segment_count}")
    else:
        print("Segments: Not built")

    # Load cards
    cards_file = catalog_dir / "indexes" / "cards.jsonl"
    if cards_file.exists():
        card_count = sum(1 for _ in open(cards_file, 'r', encoding='utf-8'))
        print(f"Cards: {card_count}")

        # Count by directory
        dir_counts = {}
        with open(cards_file, 'r', encoding='utf-8') as f:
            for line in f:
                card = json.loads(line)
                source_dir = card['source'].split('/')[0] if '/' in card['source'] else 'root'
                dir_counts[source_dir] = dir_counts.get(source_dir, 0) + 1

        print("\nCards by directory:")
        for dir_name in sorted(dir_counts.keys()):
            print(f"  {dir_name}: {dir_counts[dir_name]}")
    else:
        print("Cards: Not built")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="HGG Index - Card catalog for semantic markdown library"
    )
    parser.add_argument(
        '--source-dir',
        default='HGG-',
        help='Source directory containing markdown files (default: HGG-)'
    )
    parser.add_argument(
        '--catalog-dir',
        default='catalog',
        help='Catalog output directory (default: catalog)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Ingest command
    parser_ingest = subparsers.add_parser('ingest', help='Ingest source markdown files')

    # Segment command
    parser_segment = subparsers.add_parser('segment', help='Segment sources into blocks')

    # Cards command
    parser_cards = subparsers.add_parser('cards', help='Generate catalog cards')

    # Build command (all-in-one)
    parser_build = subparsers.add_parser('build', help='Build complete catalog (ingest + segment + cards)')

    # List command
    parser_ls = subparsers.add_parser('ls', help='List cards')
    parser_ls.add_argument('--source', help='Filter by source file pattern')
    parser_ls.add_argument('--limit', type=int, help='Limit number of results')

    # Show command
    parser_show = subparsers.add_parser('show', help='Show card details')
    parser_show.add_argument('card_id', help='Card ID or location code')
    parser_show.add_argument('-v', '--verbose', action='store_true', help='Show full content')

    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show catalog statistics')

    args = parser.parse_args()

    # Dispatch commands
    if args.command == 'ingest':
        cmd_ingest(args)
    elif args.command == 'segment':
        cmd_segment(args)
    elif args.command == 'cards':
        cmd_cards(args)
    elif args.command == 'build':
        cmd_build(args)
    elif args.command == 'ls':
        cmd_ls(args)
    elif args.command == 'show':
        cmd_show(args)
    elif args.command == 'stats':
        cmd_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
