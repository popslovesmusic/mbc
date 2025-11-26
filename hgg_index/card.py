"""Card generation - create YAML catalog cards from segments"""

import re
import yaml
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass

from .segment import Segment


@dataclass
class Card:
    """Represents a catalog card"""
    id: str
    location: str
    source: str
    lines: str  # "start-end"
    heading: str
    parent_heading: str or None
    concepts: List[str]
    block_type: str
    excerpt: str  # First few lines of content


class CardGenerator:
    """Generates YAML catalog cards from segments"""

    def __init__(self, catalog_dir: str = "catalog"):
        self.catalog_dir = Path(catalog_dir)
        self.cards_dir = self.catalog_dir / "cards" / "by-source"

    def generate_card(self, segment: Segment) -> Card:
        """Generate a card from a segment"""

        # Extract concepts (capitalized terms, math symbols, technical terms)
        concepts = self._extract_concepts(segment.content)

        # Get parent heading (second to last in chain)
        parent_heading = None
        if len(segment.heading_chain) > 1:
            parent_heading = segment.heading_chain[-2]

        # Create excerpt (first 200 chars or 3 lines)
        excerpt = self._create_excerpt(segment.content)

        card = Card(
            id=segment.id,
            location=segment.location_code,
            source=segment.source_relative,
            lines=f"{segment.start_line}-{segment.end_line}",
            heading=segment.heading,
            parent_heading=parent_heading,
            concepts=concepts,
            block_type=segment.block_type,
            excerpt=excerpt
        )

        return card

    def _extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts from content

        Looks for:
        - Greek symbols (δ, Φ, Π, Ψ, etc.)
        - Capitalized technical terms
        - Mathematical operators
        - Quoted terms
        """
        concepts = set()

        # Greek letters and math symbols
        greek_pattern = r'[δΦΠΨΣΩΛΓΘαβγλμνωηξζρστ]'
        for match in re.finditer(greek_pattern, content):
            concepts.add(match.group())

        # Capitalized terms (2+ words, title case)
        # e.g., "Box Algebra", "Meta-Genesis", "Foundation Layer"
        title_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        for match in re.finditer(title_pattern, content):
            term = match.group(1)
            # Skip common non-concepts
            if term not in ['The', 'This', 'That', 'These', 'Those', 'A', 'An']:
                concepts.add(term)

        # Hyphenated technical terms
        hyphen_pattern = r'\b([A-Z][a-z]+(?:-[A-Z][a-z]+)+)\b'
        for match in re.finditer(hyphen_pattern, content):
            concepts.add(match.group(1))

        # Single capitalized technical words (if followed by specific patterns)
        # e.g., "Box", "Operator", "Layer"
        single_cap_pattern = r'\b(Box|Operator|Layer|Field|Mode|Axiom|Theorem|Lemma|Corollary)\b'
        for match in re.finditer(single_cap_pattern, content):
            concepts.add(match.group(1))

        # Terms in backticks or bold
        marked_pattern = r'[`*]+([A-Za-z0-9δΦΠΨ\-]+)[`*]+'
        for match in re.finditer(marked_pattern, content):
            term = match.group(1)
            if len(term) > 2:  # Skip very short terms
                concepts.add(term)

        return sorted(list(concepts))[:15]  # Limit to top 15 concepts

    def _create_excerpt(self, content: str, max_chars: int = 200) -> str:
        """Create a short excerpt from content"""
        lines = content.split('\n')

        # Take first 3 non-empty lines
        excerpt_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('|'):  # Skip table rows
                excerpt_lines.append(line)
                if len(excerpt_lines) >= 3:
                    break

        excerpt = ' '.join(excerpt_lines)

        # Truncate to max_chars
        if len(excerpt) > max_chars:
            excerpt = excerpt[:max_chars] + '...'

        return excerpt

    def save_card(self, card: Card, segment: Segment):
        """Save a card as a YAML file"""

        # Determine subdirectory based on source path
        # e.g., genesis-0/tri-unity-theorem/objects-primitives__b1.yaml
        source_path = Path(segment.source_relative)
        source_parts = source_path.parts

        # Create directory structure
        if len(source_parts) > 1:
            subdir = self.cards_dir / source_parts[0]
        else:
            subdir = self.cards_dir / "root"

        subdir.mkdir(parents=True, exist_ok=True)

        # Create filename from location code
        # Replace :: with / for directory structure
        location_parts = segment.location_code.split('::')

        # Use last two parts for filename: heading__block
        if len(location_parts) >= 2:
            filename = f"{location_parts[-2]}__{location_parts[-1]}.yaml"
        else:
            filename = f"{segment.id}.yaml"

        # Remove invalid filename characters
        filename = re.sub(r'[<>:"/\\|?*]', '-', filename)

        filepath = subdir / filename

        # Convert card to dict
        card_dict = {
            'id': card.id,
            'location': card.location,
            'source': card.source,
            'lines': card.lines,
            'heading': card.heading,
            'concepts': card.concepts,
            'block_type': card.block_type,
            'excerpt': card.excerpt
        }

        if card.parent_heading:
            card_dict['parent_heading'] = card.parent_heading

        # Write YAML
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(card_dict, f, default_flow_style=False, allow_unicode=True)

        return filepath

    def generate_all(self, segments: List[Segment]):
        """Generate cards for all segments"""
        print(f"\nGenerating {len(segments)} catalog cards...")

        cards_generated = 0

        for segment in segments:
            card = self.generate_card(segment)
            filepath = self.save_card(card, segment)
            cards_generated += 1

            if cards_generated % 50 == 0:
                print(f"  Generated {cards_generated} cards...")

        print(f"\n[OK] Generated {cards_generated} cards in {self.cards_dir}")

    def save_card_index(self, segments: List[Segment]):
        """Save a flat JSONL index of all cards"""
        import json

        index_file = self.catalog_dir / "indexes" / "cards.jsonl"
        index_file.parent.mkdir(parents=True, exist_ok=True)

        with open(index_file, 'w', encoding='utf-8') as f:
            for segment in segments:
                card = self.generate_card(segment)
                card_dict = {
                    'id': card.id,
                    'location': card.location,
                    'source': card.source,
                    'heading': card.heading,
                    'concepts': card.concepts,
                    'excerpt': card.excerpt
                }
                json.dump(card_dict, f)
                f.write('\n')

        print(f"Card index saved to {index_file}")


def generate_cards(segments: List[Segment], catalog_dir: str = "catalog"):
    """Generate catalog cards from segments

    Args:
        segments: List of segments to generate cards from
        catalog_dir: Directory to store catalog

    Returns:
        CardGenerator instance
    """
    generator = CardGenerator(catalog_dir=catalog_dir)
    generator.generate_all(segments)
    generator.save_card_index(segments)

    return generator


if __name__ == "__main__":
    # Test card generation
    import json
    from pathlib import Path

    # Load segments
    segments_file = Path("catalog/indexes/segments.jsonl")
    if segments_file.exists():
        segments = []
        with open(segments_file, 'r', encoding='utf-8') as f:
            for line in f:
                seg_data = json.loads(line)
                segment = Segment(**seg_data)
                segments.append(segment)

        generate_cards(segments)
