"""Contradiction detection and ambiguity flagging"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ContradictionFlag:
    """Represents a potential contradiction"""
    text: str
    type: str  # 'negation', 'conflict', 'ambiguity', 'qualifier'
    severity: float  # 0.0 = minor, 1.0 = definite contradiction
    reason: str


class ConsistencyAnalyzer:
    """Detect contradictions, ambiguities, and qualifiers"""

    # Negation patterns
    NEGATION_PATTERNS = [
        r'\bnot\b',
        r'\bno\b',
        r'\bnone\b',
        r'\bneither\b',
        r'\bnor\b',
        r'\bnever\b',
        r'\bcannot\b',
        r'\bcan\'?t\b',
        r'\bwon\'?t\b',
        r'\bdon\'?t\b',
        r'\bdoesn\'?t\b',
        r'\bisn\'?t\b',
        r'\baren\'?t\b',
        r'\bwasn\'?t\b',
        r'\bweren\'?t\b',
        r'[¬~]',  # Logic symbols for negation
        r'\\neg',  # LaTeX negation
    ]

    # Conflicting statement pairs
    CONFLICT_PATTERNS = [
        (r'\b(always|must|necessarily|required|essential)\b', r'\b(sometimes|may|optional|possible|might)\b'),
        (r'\b(all|every|each)\b', r'\b(some|certain|particular)\b'),
        (r'\b(unique|only|sole|single)\b', r'\b(multiple|many|various|several)\b'),
        (r'\b(equivalent|same|identical)\b', r'\b(different|distinct|separate)\b'),
        (r'\b(constant|fixed|invariant)\b', r'\b(variable|changing|dynamic)\b'),
    ]

    # Ambiguity markers
    AMBIGUITY_PATTERNS = [
        r'\b(maybe|perhaps|possibly|probably|likely)\b',
        r'\b(seems|appears|looks like|might be)\b',
        r'\b(unclear|ambiguous|uncertain|unknown)\b',
        r'\b(roughly|approximately|about|around)\b',
        r'\b(some|certain|various)\b',
        r'\b(could be|may be|might be)\b',
        r'\b(or)\b.*\b(or)\b',  # Multiple alternatives
        r'\?',  # Question marks
    ]

    # Qualifier patterns (hedging language)
    QUALIFIER_PATTERNS = [
        r'\b(generally|typically|usually|often)\b',
        r'\b(in most cases|in general|by default)\b',
        r'\b(tends to|inclined to)\b',
        r'\b(somewhat|rather|fairly|quite)\b',
        r'\b(essentially|basically|fundamentally)\b',
        r'\b(assumed|supposed|presumed)\b',
    ]

    # Contradiction indicator phrases
    CONTRADICTION_INDICATORS = [
        r'\b(however|but|although|though|despite|nevertheless)\b',
        r'\b(on the other hand|conversely|in contrast|whereas)\b',
        r'\b(except|unless|without)\b',
    ]

    def __init__(self):
        self.negation_regex = re.compile('|'.join(self.NEGATION_PATTERNS), re.IGNORECASE)
        self.ambiguity_regex = re.compile('|'.join(self.AMBIGUITY_PATTERNS), re.IGNORECASE)
        self.qualifier_regex = re.compile('|'.join(self.QUALIFIER_PATTERNS), re.IGNORECASE)
        self.contradiction_regex = re.compile('|'.join(self.CONTRADICTION_INDICATORS), re.IGNORECASE)

    def analyze_block(self, content: str) -> Dict[str, any]:
        """Analyze a block for contradictions and ambiguities

        Returns:
            Dict with analysis results
        """
        flags = []

        # Check for negations
        negation_flags = self._detect_negations(content)
        flags.extend(negation_flags)

        # Check for conflicts
        conflict_flags = self._detect_conflicts(content)
        flags.extend(conflict_flags)

        # Check for ambiguities
        ambiguity_flags = self._detect_ambiguities(content)
        flags.extend(ambiguity_flags)

        # Check for qualifiers
        qualifier_flags = self._detect_qualifiers(content)
        flags.extend(qualifier_flags)

        # Check for contradiction indicators
        contradiction_flags = self._detect_contradiction_indicators(content)
        flags.extend(contradiction_flags)

        # Calculate scores
        has_contradictions = any(f.type == 'conflict' for f in flags)
        has_ambiguity = any(f.type == 'ambiguity' for f in flags)
        has_qualifiers = any(f.type == 'qualifier' for f in flags)

        max_severity = max([f.severity for f in flags], default=0.0)

        return {
            'flags': flags,
            'has_contradictions': has_contradictions,
            'has_ambiguity': has_ambiguity,
            'has_qualifiers': has_qualifiers,
            'max_severity': max_severity,
            'flag_count': len(flags),
            'is_definitive': max_severity < 0.3 and not has_ambiguity,  # Strong, clear statement
        }

    def _detect_negations(self, content: str) -> List[ContradictionFlag]:
        """Detect negation patterns"""
        flags = []

        matches = self.negation_regex.finditer(content)
        for match in matches:
            # Extract context (30 chars before and after)
            start = max(0, match.start() - 30)
            end = min(len(content), match.end() + 30)
            context = content[start:end]

            flags.append(ContradictionFlag(
                text=match.group(),
                type='negation',
                severity=0.3,
                reason=f"Negation pattern: {context}"
            ))

        return flags[:3]  # Limit to first 3

    def _detect_conflicts(self, content: str) -> List[ContradictionFlag]:
        """Detect conflicting statements"""
        flags = []

        for pattern1, pattern2 in self.CONFLICT_PATTERNS:
            match1 = re.search(pattern1, content, re.IGNORECASE)
            match2 = re.search(pattern2, content, re.IGNORECASE)

            if match1 and match2:
                flags.append(ContradictionFlag(
                    text=f"{match1.group()} vs {match2.group()}",
                    type='conflict',
                    severity=0.7,
                    reason=f"Conflicting terms found in same block"
                ))

        return flags

    def _detect_ambiguities(self, content: str) -> List[ContradictionFlag]:
        """Detect ambiguous language"""
        flags = []

        matches = self.ambiguity_regex.finditer(content)
        for match in matches:
            start = max(0, match.start() - 20)
            end = min(len(content), match.end() + 20)
            context = content[start:end]

            flags.append(ContradictionFlag(
                text=match.group(),
                type='ambiguity',
                severity=0.5,
                reason=f"Ambiguous language: {context}"
            ))

        return flags[:2]  # Limit

    def _detect_qualifiers(self, content: str) -> List[ContradictionFlag]:
        """Detect hedging/qualifier language"""
        flags = []

        matches = self.qualifier_regex.finditer(content)
        for match in matches:
            flags.append(ContradictionFlag(
                text=match.group(),
                type='qualifier',
                severity=0.2,
                reason="Hedging/qualifying language"
            ))

        return flags[:2]

    def _detect_contradiction_indicators(self, content: str) -> List[ContradictionFlag]:
        """Detect explicit contradiction indicators"""
        flags = []

        matches = self.contradiction_regex.finditer(content)
        for match in matches:
            start = max(0, match.start() - 30)
            end = min(len(content), match.end() + 30)
            context = content[start:end]

            flags.append(ContradictionFlag(
                text=match.group(),
                type='conflict',
                severity=0.6,
                reason=f"Contradiction indicator: {context}"
            ))

        return flags[:2]

    def compare_blocks(self, block1: str, block2: str) -> Optional[ContradictionFlag]:
        """Compare two blocks for contradictions

        Returns:
            ContradictionFlag if contradiction found, else None
        """
        # Simple keyword overlap + negation check
        words1 = set(re.findall(r'\b\w{4,}\b', block1.lower()))
        words2 = set(re.findall(r'\b\w{4,}\b', block2.lower()))

        overlap = words1 & words2
        if len(overlap) < 3:
            return None  # Not related enough

        # Check if one has negation and other doesn't
        has_neg1 = bool(self.negation_regex.search(block1))
        has_neg2 = bool(self.negation_regex.search(block2))

        if has_neg1 != has_neg2:
            return ContradictionFlag(
                text=f"Related blocks with different negation: {list(overlap)[:5]}",
                type='conflict',
                severity=0.8,
                reason="Same concepts but one negated"
            )

        return None


def get_consistency_tags(content: str) -> List[str]:
    """Extract consistency-related tags

    Returns:
        List of tags like ['ambiguous', 'qualified', 'conflicted', 'definitive']
    """
    analyzer = ConsistencyAnalyzer()
    analysis = analyzer.analyze_block(content)

    tags = []

    if analysis['has_contradictions']:
        tags.append('conflicted')
    if analysis['has_ambiguity']:
        tags.append('ambiguous')
    if analysis['has_qualifiers']:
        tags.append('qualified')
    if analysis['is_definitive']:
        tags.append('definitive')

    if analysis['max_severity'] > 0.7:
        tags.append('high-uncertainty')
    elif analysis['max_severity'] < 0.2:
        tags.append('low-uncertainty')

    return tags


if __name__ == "__main__":
    # Test cases
    analyzer = ConsistencyAnalyzer()

    test_cases = [
        """Axiom A1: Ψ₀ cannot remain perfectly still; deviation necessarily exists.""",

        """The operator may be commutative, but it's not always associative.
        However, in some cases it could be both.""",

        """This is generally true, though there are exceptions.
        It seems to work in most cases, but we're not entirely certain.""",

        """The three operators are equivalent. δ, Φ, and Π generate the same structure.""",

        """All axioms must hold, but some are optional depending on context.""",
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test case {i}:")
        print(text[:80])
        print(f"{'='*60}")

        analysis = analyzer.analyze_block(text)

        print(f"Contradictions: {analysis['has_contradictions']}")
        print(f"Ambiguity: {analysis['has_ambiguity']}")
        print(f"Qualifiers: {analysis['has_qualifiers']}")
        print(f"Definitive: {analysis['is_definitive']}")
        print(f"Max severity: {analysis['max_severity']:.2f}")

        if analysis['flags']:
            print(f"\nFlags:")
            for flag in analysis['flags'][:5]:
                print(f"  [{flag.type}] {flag.text} (severity: {flag.severity:.2f})")

        tags = get_consistency_tags(text)
        print(f"\nTags: {tags}")
