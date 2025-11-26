"""Enhanced concept extraction for mathematical and technical content"""

import re
from typing import List, Set, Dict
from collections import Counter


class ConceptExtractor:
    """Extract technical concepts, symbols, and terms from content"""

    # Greek alphabet (both cases)
    GREEK_LOWER = 'αβγδεζηθικλμνξοπρστυφχψω'
    GREEK_UPPER = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'
    GREEK_ALL = GREEK_LOWER + GREEK_UPPER

    # Common mathematical symbols
    MATH_SYMBOLS = '∀∃∈∉⊂⊃∩∪∧∨¬→↔∫∂∇∆∑∏√∞≈≠≤≥⊕⊗'

    # Domain-specific terms (IGSOA/MBC)
    DOMAIN_TERMS = {
        'Meta-Genesis', 'Meta-Time', 'Meta-Einstein', 'Meta-Math',
        'IGSOA', 'MBC', 'Box Calculus', 'Box Algebra',
        'Deviational Geometry', 'Foundation Layer',
        'Tri-Unity', 'Adjoint Triple',
        'Chromatic Mode', 'Polarity', 'Adjacency',
        'Projection', 'Deviation', 'Curvature',
        'δ-geometry', 'Φ-projection', 'Π-evaluation',
    }

    # Operator/function terms
    OPERATOR_TERMS = {
        'Operator', 'Functor', 'Morphism', 'Transform',
        'Field', 'Mode', 'State', 'Layer',
        'Box', 'Gate', 'Router', 'Classifier',
        'Merge', 'Fork', 'Split', 'Chain',
    }

    # Formal statement markers
    FORMAL_MARKERS = {
        'Axiom', 'Theorem', 'Lemma', 'Corollary', 'Proposition',
        'Definition', 'Proof', 'QED',
    }

    def __init__(self):
        self.greek_pattern = re.compile(f'[{self.GREEK_ALL}]')
        self.math_symbol_pattern = re.compile(f'[{self.MATH_SYMBOLS}]')

    def extract_all(self, content: str, limit: int = 20) -> List[str]:
        """Extract all concepts from content

        Args:
            content: Text to analyze
            limit: Maximum number of concepts to return

        Returns:
            Sorted list of unique concepts
        """
        concepts = set()

        # Extract each category
        concepts.update(self.extract_greek_symbols(content))
        concepts.update(self.extract_math_symbols(content))
        concepts.update(self.extract_domain_terms(content))
        concepts.update(self.extract_operators(content))
        concepts.update(self.extract_title_terms(content))
        concepts.update(self.extract_hyphenated_terms(content))
        concepts.update(self.extract_marked_terms(content))
        concepts.update(self.extract_formal_markers(content))
        concepts.update(self.extract_compound_symbols(content))

        # Sort by importance (frequency, length, etc.)
        scored = self._score_concepts(concepts, content)

        # Return top N
        return [c for c, score in scored[:limit]]

    def extract_greek_symbols(self, content: str) -> Set[str]:
        """Extract Greek letters"""
        return set(self.greek_pattern.findall(content))

    def extract_math_symbols(self, content: str) -> Set[str]:
        """Extract mathematical symbols"""
        return set(self.math_symbol_pattern.findall(content))

    def extract_domain_terms(self, content: str) -> Set[str]:
        """Extract known domain-specific terms"""
        found = set()
        for term in self.DOMAIN_TERMS:
            if term in content:
                found.add(term)
        return found

    def extract_operators(self, content: str) -> Set[str]:
        """Extract operator/function terms"""
        found = set()
        for term in self.OPERATOR_TERMS:
            # Look for term as whole word
            if re.search(rf'\b{re.escape(term)}\b', content):
                found.add(term)
        return found

    def extract_formal_markers(self, content: str) -> Set[str]:
        """Extract formal statement markers"""
        found = set()
        for term in self.FORMAL_MARKERS:
            if re.search(rf'\b{term}\b', content, re.IGNORECASE):
                found.add(term)
        return found

    def extract_title_terms(self, content: str) -> Set[str]:
        """Extract title-cased multi-word terms

        Examples: "Box Algebra", "Meta Genesis", "Foundation Layer"
        """
        # Pattern: Capital + lowercase, followed by one or more similar words
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        matches = re.findall(pattern, content)

        # Filter out common non-concepts
        stopwords = {'The', 'This', 'That', 'These', 'Those', 'A', 'An', 'And', 'Or', 'But'}
        filtered = [m for m in matches if m not in stopwords]

        return set(filtered)

    def extract_hyphenated_terms(self, content: str) -> Set[str]:
        """Extract hyphenated technical terms

        Examples: "Meta-Time", "δ-geometry", "IGSOA-compatible"
        """
        # Pattern: word-word (can include Greek, symbols)
        pattern = r'\b([A-Za-zδΦΠΨΣΩ][A-Za-z0-9δΦΠΨΣΩ]*(?:\-[A-Za-zδΦΠΨΣΩ][A-Za-z0-9δΦΠΨΣΩ]*)+)\b'
        matches = re.findall(pattern, content)

        return set(matches)

    def extract_marked_terms(self, content: str) -> Set[str]:
        """Extract terms in backticks, bold, or italic

        Examples: `Box`, **Operator**, *field*
        """
        terms = set()

        # Backticks
        backtick_pattern = r'`([A-Za-zδΦΠΨ][A-Za-z0-9δΦΠΨ\-]*)`'
        terms.update(re.findall(backtick_pattern, content))

        # Bold (** or __)
        bold_pattern = r'\*\*([A-Za-zδΦΠΨ][A-Za-z0-9δΦΠΨ\-\s]*)\*\*'
        terms.update(re.findall(bold_pattern, content))

        bold_pattern2 = r'__([A-Za-zδΦΠΨ][A-Za-z0-9δΦΠΨ\-\s]*)__'
        terms.update(re.findall(bold_pattern2, content))

        # Filter short or whitespace-heavy terms
        filtered = [t.strip() for t in terms if len(t.strip()) > 2]

        return set(filtered)

    def extract_compound_symbols(self, content: str) -> Set[str]:
        """Extract compound symbols like δΨ₀, Φ-projection, etc."""
        # Pattern: Greek + word or Greek + subscript/superscript
        pattern = r'[δΦΠΨΣΩ][A-Za-z₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹]*'
        matches = re.findall(pattern, content)

        return set(m for m in matches if len(m) > 1)

    def _score_concepts(self, concepts: Set[str], content: str) -> List[tuple]:
        """Score concepts by importance

        Scoring factors:
        - Frequency in content
        - Length (longer = more specific)
        - Domain term (higher score)
        - Formal marker (higher score)
        """
        scored = []

        for concept in concepts:
            score = 0

            # Frequency
            count = content.count(concept)
            score += count * 10

            # Length
            score += len(concept)

            # Domain term
            if concept in self.DOMAIN_TERMS:
                score += 50

            # Operator term
            if concept in self.OPERATOR_TERMS:
                score += 30

            # Formal marker
            if concept in self.FORMAL_MARKERS:
                score += 40

            # Greek or math symbol
            if len(concept) == 1 and (concept in self.GREEK_ALL or concept in self.MATH_SYMBOLS):
                score += 20

            # Hyphenated (usually important)
            if '-' in concept:
                score += 15

            scored.append((concept, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored

    def extract_concept_density(self, content: str) -> Dict[str, any]:
        """Calculate concept density metrics

        Returns:
            Dict with density stats
        """
        words = len(re.findall(r'\b\w+\b', content))
        concepts = self.extract_all(content, limit=100)

        # Count different types
        greek_count = len([c for c in concepts if any(g in c for g in self.GREEK_ALL)])
        math_count = len([c for c in concepts if any(s in c for s in self.MATH_SYMBOLS)])
        domain_count = len([c for c in concepts if c in self.DOMAIN_TERMS])

        return {
            'total_words': words,
            'unique_concepts': len(concepts),
            'concepts_per_word': len(concepts) / words if words > 0 else 0,
            'greek_symbols': greek_count,
            'math_symbols': math_count,
            'domain_terms': domain_count,
            'density_score': (len(concepts) / words * 100) if words > 0 else 0,
        }


if __name__ == "__main__":
    # Test cases
    extractor = ConceptExtractor()

    test_cases = [
        """**Axiom A1 (Deviation Necessity)**: Ψ₀ cannot remain still;
        deviation δ exists: ∃ δ: δΨ₀ ≠ 0.""",

        """The Box Calculus defines operators E and A for semantic expansion
        and aggregation. Meta-Time emerges from δ-geometry through Φ-projection.""",

        """The Tri-Unity Theorem states that δ, Φ, and Π are equivalent
        generators of the Foundation Layer in Meta-Genesis.""",
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test case {i}:")
        print(text[:80] + "...")
        print(f"{'='*60}")

        concepts = extractor.extract_all(text, limit=15)
        print(f"Top concepts: {concepts}")

        density = extractor.extract_concept_density(text)
        print(f"\nDensity metrics:")
        print(f"  Words: {density['total_words']}")
        print(f"  Unique concepts: {density['unique_concepts']}")
        print(f"  Density score: {density['density_score']:.1f}%")
        print(f"  Greek: {density['greek_symbols']}, Math: {density['math_symbols']}, Domain: {density['domain_terms']}")
