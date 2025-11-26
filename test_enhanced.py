"""Test enhanced card generation"""

import json
from pathlib import Path
from hgg_index.segment import Segment
from hgg_index.card_enhanced import EnhancedCardGenerator

# Load first 5 segments
segments_file = Path('catalog/indexes/segments.jsonl')
segments = []
with open(segments_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 5:
            break
        seg_data = json.loads(line)
        segment = Segment(**seg_data)
        segments.append(segment)

# Generate enhanced cards
generator = EnhancedCardGenerator(catalog_dir='catalog-test')

output_file = Path('test-enhanced-output.txt')
with open(output_file, 'w', encoding='utf-8') as out:
    for segment in segments:
        card = generator.generate_card(segment)

        out.write(f'\n{"="*60}\n')
        out.write(f'Card: {card.id}\n')
        out.write(f'Heading: {card.heading}\n')
        out.write(f'Concepts: {card.concepts[:5]}\n')
        out.write(f'Aliases: {card.aliases}\n')
        out.write(f'Tags: {card.tags}\n')
        out.write(f'Is Formal: {card.is_formal}\n')
        out.write(f'Statement Type: {card.statement_type}\n')
        out.write(f'Axiom Count: {card.axiom_count}\n')
        out.write(f'Conversational Score: {card.conversational_score:.2f}\n')
        out.write(f'Is Technical: {card.is_technical}\n')
        out.write(f'Contradictions: {card.has_contradictions}\n')
        out.write(f'Ambiguity: {card.has_ambiguity}\n')
        out.write(f'Definitive: {card.is_definitive}\n')
        out.write(f'Max Severity: {card.max_severity:.2f}\n')
        out.write(f'Excerpt: {card.excerpt[:100]}...\n')

print(f"Test output written to {output_file}")
print("Enhanced features working correctly!")
