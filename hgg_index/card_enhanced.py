"""Enhanced card generation with semantic metrics"""

import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from hgg_index.segment import Segment
from hgg_index.utils.concepts import ConceptExtractor
from hgg_index.utils.axioms import AxiomDetector, extract_axiom_tags
from hgg_index.utils.aliases import AliasGenerator, extract_existing_aliases
from hgg_index.utils.cleaning import ConversationalDetector, is_technical_content
from hgg_index.utils.consistency import ConsistencyAnalyzer, get_consistency_tags


@dataclass
class EnhancedCard:
    """Enhanced catalog card with semantic metrics"""
    # Basic identification
    id: str
    location: str
    source: str
    lines: str

    # Content structure
    heading: str
    parent_heading: Optional[str]
    block_type: str
    excerpt: str

    # Semantic metrics
    concepts: List[str]
    aliases: List[str]  # Am154nb2 format identifiers
    tags: List[str]  # axiom, theorem, sealed, etc.

    # Formal statement info
    is_formal: bool
    statement_type: Optional[str]  # axiom, theorem, etc.
    axiom_count: int
    theorem_count: int

    # Quality metrics
    conversational_score: float  # 0.0 = technical, 1.0 = very conversational
    is_technical: bool
    concept_density: float  # concepts per 100 words

    # Consistency metrics
    has_contradictions: bool
    has_ambiguity: bool
    is_definitive: bool
    max_severity: float  # 0.0 = certain, 1.0 = very uncertain

    # Optional identifiers from content
    identifiers: List[str]  # A1, GA-8, etc.


class EnhancedCardGenerator:
    """Generate cards with full semantic analysis"""

    def __init__(self, catalog_dir: str = "catalog"):
        self.catalog_dir = Path(catalog_dir)
        self.cards_dir = self.catalog_dir / "cards" / "by-source"

        # Initialize analyzers
        self.concept_extractor = ConceptExtractor()
        self.axiom_detector = AxiomDetector()
        self.alias_generator = AliasGenerator()
        self.conv_detector = ConversationalDetector()
        self.consistency_analyzer = ConsistencyAnalyzer()

    def generate_card(self, segment: Segment) -> EnhancedCard:
        """Generate an enhanced card from a segment"""

        content = segment.content

        # Extract concepts
        concepts = self.concept_extractor.extract_all(content, limit=15)

        # Detect formal statements
        formal_info = self.axiom_detector.classify_block_type(content)

        # Generate alias
        alias_str = self.alias_generator.generate(
            content=content,
            block_type=formal_info.get('statement_type') or segment.block_type,
            identifier=formal_info['identifiers'][0] if formal_info['identifiers'] else None
        )

        # Extract existing aliases
        existing_aliases = extract_existing_aliases(content)
        all_aliases = list(set([alias_str] + existing_aliases))

        # Extract tags
        tags = extract_axiom_tags(content)

        # Conversational detection
        conv_score = self.conv_detector.get_conversational_score(content)
        is_tech = is_technical_content(content)

        # Concept density
        density_info = self.concept_extractor.extract_concept_density(content)

        # Consistency analysis
        consistency_info = self.consistency_analyzer.analyze_block(content)
        consistency_tags = get_consistency_tags(content)
        tags.extend(consistency_tags)
        tags = list(set(tags))  # Deduplicate

        # Get parent heading
        parent_heading = None
        if len(segment.heading_chain) > 1:
            parent_heading = segment.heading_chain[-2]

        # Create excerpt
        excerpt = self._create_excerpt(content)

        card = EnhancedCard(
            # Basic
            id=segment.id,
            location=segment.location_code,
            source=segment.source_relative,
            lines=f"{segment.start_line}-{segment.end_line}",
            heading=segment.heading,
            parent_heading=parent_heading,
            block_type=segment.block_type,
            excerpt=excerpt,

            # Semantic
            concepts=concepts,
            aliases=all_aliases,
            tags=tags,

            # Formal
            is_formal=formal_info['is_formal'],
            statement_type=formal_info['statement_type'],
            axiom_count=formal_info['axiom_count'],
            theorem_count=formal_info['theorem_count'],
            identifiers=formal_info['identifiers'],

            # Quality
            conversational_score=conv_score,
            is_technical=is_tech,
            concept_density=density_info['density_score'],

            # Consistency
            has_contradictions=consistency_info['has_contradictions'],
            has_ambiguity=consistency_info['has_ambiguity'],
            is_definitive=consistency_info['is_definitive'],
            max_severity=consistency_info['max_severity'],
        )

        return card

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

    def save_card(self, card: EnhancedCard, segment: Segment):
        """Save an enhanced card as YAML"""

        # Determine subdirectory
        source_path = Path(segment.source_relative)
        source_parts = source_path.parts

        if len(source_parts) > 1:
            subdir = self.cards_dir / source_parts[0]
        else:
            subdir = self.cards_dir / "root"

        subdir.mkdir(parents=True, exist_ok=True)

        # Create filename
        location_parts = segment.location_code.split('::')
        if len(location_parts) >= 2:
            filename = f"{location_parts[-2]}__{location_parts[-1]}.yaml"
        else:
            filename = f"{segment.id}.yaml"

        filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
        filepath = subdir / filename

        # Convert to dict (filter Nones and empty lists)
        card_dict = asdict(card)
        card_dict = {k: v for k, v in card_dict.items() if v is not None and v != []}

        # Write YAML
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(card_dict, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return filepath

    def generate_all(self, segments: List[Segment]):
        """Generate enhanced cards for all segments"""
        print(f"\nGenerating {len(segments)} enhanced catalog cards...")

        cards_generated = 0

        for segment in segments:
            card = self.generate_card(segment)
            filepath = self.save_card(card, segment)
            cards_generated += 1

            if cards_generated % 50 == 0:
                print(f"  Generated {cards_generated} cards...")

        print(f"\n[OK] Generated {cards_generated} enhanced cards in {self.cards_dir}")

    def save_card_index(self, segments: List[Segment]):
        """Save flat JSONL index of enhanced cards"""
        import json

        index_file = self.catalog_dir / "indexes" / "cards-enhanced.jsonl"
        index_file.parent.mkdir(parents=True, exist_ok=True)

        with open(index_file, 'w', encoding='utf-8') as f:
            for segment in segments:
                card = self.generate_card(segment)

                # Create compact index entry
                card_dict = {
                    'id': card.id,
                    'location': card.location,
                    'source': card.source,
                    'heading': card.heading,
                    'concepts': card.concepts,
                    'aliases': card.aliases,
                    'tags': card.tags,
                    'is_formal': card.is_formal,
                    'statement_type': card.statement_type,
                    'conversational_score': round(card.conversational_score, 2),
                    'is_technical': card.is_technical,
                    'has_contradictions': card.has_contradictions,
                    'has_ambiguity': card.has_ambiguity,
                    'is_definitive': card.is_definitive,
                    'max_severity': round(card.max_severity, 2),
                    'excerpt': card.excerpt
                }

                json.dump(card_dict, f, ensure_ascii=False)
                f.write('\n')

        print(f"Enhanced card index saved to {index_file}")


def generate_enhanced_cards(segments: List[Segment], catalog_dir: str = "catalog"):
    """Generate enhanced catalog cards from segments

    Args:
        segments: List of segments
        catalog_dir: Catalog directory

    Returns:
        EnhancedCardGenerator instance
    """
    generator = EnhancedCardGenerator(catalog_dir=catalog_dir)
    generator.generate_all(segments)
    generator.save_card_index(segments)

    return generator


if __name__ == "__main__":
    # Test enhanced card generation
    import json
    from pathlib import Path
    from hgg_index.segment import Segment

    # Load segments
    segments_file = Path("catalog/indexes/segments.jsonl")
    if segments_file.exists():
        segments = []
        with open(segments_file, 'r', encoding='utf-8') as f:
            for line in f:
                seg_data = json.loads(line)
                segment = Segment(**seg_data)
                segments.append(segment)

        # Generate first 10 as test
        test_segments = segments[:10]
        generate_enhanced_cards(test_segments)
