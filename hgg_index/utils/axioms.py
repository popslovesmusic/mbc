"""Axiom, theorem, and formal statement detection"""

import re
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class FormalStatement:
    """Represents a detected formal statement (axiom, theorem, etc.)"""
    type: str  # 'axiom', 'theorem', 'lemma', 'corollary', 'proposition', 'definition'
    identifier: Optional[str]  # e.g., 'A1', 'Theorem 3', 'GA-8'
    name: Optional[str]  # e.g., 'Tri-Unity Theorem'
    content: str
    line_start: int
    line_end: int


class AxiomDetector:
    """Detects axioms, theorems, and formal mathematical statements"""

    # Formal statement headers
    STATEMENT_PATTERNS = [
        # Standard format: "Axiom 1:", "Theorem A1:", etc.
        r'^(Axiom|Theorem|Lemma|Corollary|Proposition|Definition|Proof)\s*([A-Z0-9\-\.]+)?\s*[:\(]?\s*(.*)$',

        # Boxed format: "**Axiom A1**", "***Theorem***"
        r'^\*+\s*(Axiom|Theorem|Lemma|Corollary|Proposition|Definition)\s*([A-Z0-9\-\.]+)?\s*[:\(]?\s*(.*?)\*+$',

        # IGSOA format: "GA-8", "A1", "META-PHYSICS AXIOM BOX"
        r'^([A-Z]+\-\d+)[\s:]',

        # Numbered format in parentheses: "(A1)", "(Theorem 3)"
        r'^\(?(Axiom|Theorem|Lemma|Corollary|Proposition)\s*([A-Z0-9\-\.]+)\)?',
    ]

    # Special IGSOA identifiers
    IGSOA_PATTERNS = [
        r'(GA\-\d+)',          # GA-8 (Meta-Einstein)
        r'(A\d+)',             # A1, A2, A3
        r'(META\-[A-Z]+)',     # META-PHYSICS, META-TIME
        r'AXIOM\s+BOX',        # AXIOM BOX
        r'SEALED',             # SEALED AXIOM BOX
    ]

    def __init__(self):
        self.statement_regex = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in self.STATEMENT_PATTERNS]
        self.igsoa_regex = [re.compile(p) for p in self.IGSOA_PATTERNS]

    def detect_formal_statements(self, content: str, start_line: int = 1) -> List[FormalStatement]:
        """Detect all formal statements in content

        Args:
            content: Text content to analyze
            start_line: Starting line number for this content

        Returns:
            List of detected formal statements
        """
        statements = []
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Try each pattern
            for pattern in self.statement_regex:
                match = pattern.match(line)
                if match:
                    stmt_type = match.group(1).lower() if match.group(1) else 'statement'
                    identifier = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                    name = match.group(3) if len(match.groups()) > 2 and match.group(3) else None

                    # Clean up name
                    if name:
                        name = name.strip(' :.()*')

                    # Collect statement content (current line + following lines until blank)
                    stmt_lines = [line]
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line or self._is_new_statement(next_line):
                            break
                        stmt_lines.append(next_line)
                        j += 1

                    statement = FormalStatement(
                        type=stmt_type,
                        identifier=identifier,
                        name=name,
                        content='\n'.join(stmt_lines),
                        line_start=start_line + i,
                        line_end=start_line + j - 1
                    )
                    statements.append(statement)
                    i = j - 1
                    break

            i += 1

        return statements

    def _is_new_statement(self, line: str) -> bool:
        """Check if line starts a new formal statement"""
        for pattern in self.statement_regex:
            if pattern.match(line):
                return True
        return False

    def detect_igsoa_identifiers(self, content: str) -> List[str]:
        """Detect IGSOA-specific identifiers (GA-8, A1, etc.)

        Returns:
            List of unique identifiers found
        """
        identifiers = set()

        for pattern in self.igsoa_regex:
            matches = pattern.findall(content)
            identifiers.update(matches)

        return sorted(list(identifiers))

    def classify_block_type(self, content: str) -> Dict[str, any]:
        """Classify a block and extract formal statement info

        Returns:
            Dict with keys: is_formal, statement_type, identifiers, axiom_count
        """
        statements = self.detect_formal_statements(content)
        identifiers = self.detect_igsoa_identifiers(content)

        # Count axioms specifically
        axiom_count = sum(1 for s in statements if s.type == 'axiom')

        # Determine primary type
        statement_type = None
        if statements:
            # Use most specific type found
            type_priority = ['axiom', 'theorem', 'lemma', 'corollary', 'proposition', 'definition']
            for t in type_priority:
                if any(s.type == t for s in statements):
                    statement_type = t
                    break

        return {
            'is_formal': len(statements) > 0,
            'statement_type': statement_type,
            'statements': statements,
            'identifiers': identifiers,
            'axiom_count': axiom_count,
            'theorem_count': sum(1 for s in statements if s.type == 'theorem'),
            'total_statements': len(statements),
        }


def extract_axiom_tags(content: str) -> List[str]:
    """Extract axiom-related tags for indexing

    Returns:
        List of tags like ['axiom', 'A1', 'deviation-necessity', 'sealed']
    """
    tags = []

    detector = AxiomDetector()
    classification = detector.classify_block_type(content)

    # Add statement type
    if classification['statement_type']:
        tags.append(classification['statement_type'])

    # Add identifiers
    tags.extend(classification['identifiers'])

    # Add special markers
    if 'AXIOM BOX' in content.upper():
        tags.append('axiom-box')
    if 'SEALED' in content.upper():
        tags.append('sealed')
    if 'PROOF' in content.upper():
        tags.append('proof')

    # Extract name-based tags
    for stmt in classification['statements']:
        if stmt.name:
            # Convert name to tag format
            tag = stmt.name.lower()
            tag = re.sub(r'[^\w\s\-]', '', tag)
            tag = re.sub(r'\s+', '-', tag)
            if tag and len(tag) > 3:
                tags.append(tag)

    return list(set(tags))


if __name__ == "__main__":
    # Test cases
    detector = AxiomDetector()

    test_cases = [
        """## Axiom A1 (NOT / Deviation Necessity)

Ψ₀ cannot remain perfectly still; deviation exists:
∃ δ: δΨ₀ ≠ 0.""",

        """**Theorem (Tri-Unity)**: The three operators δ, Φ, Π are equivalent.""",

        """GA-8: The Meta-Einstein Equation

This theorem shows that curvature emerges from δ-geometry.""",

        """***META-PHYSICS AXIOM BOX***

Contains the foundational axioms for Meta-Genesis.""",

        """Some regular text without any formal statements."""
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test case {i}:")
        print(f"{'='*60}")
        print(text[:100] + "...")

        classification = detector.classify_block_type(text)
        print(f"\nClassification:")
        print(f"  Is formal: {classification['is_formal']}")
        print(f"  Type: {classification['statement_type']}")
        print(f"  Axiom count: {classification['axiom_count']}")
        print(f"  Identifiers: {classification['identifiers']}")

        tags = extract_axiom_tags(text)
        print(f"  Tags: {tags}")

        if classification['statements']:
            print(f"\nStatements found:")
            for stmt in classification['statements']:
                print(f"  - {stmt.type.upper()}", end='')
                if stmt.identifier:
                    print(f" {stmt.identifier}", end='')
                if stmt.name:
                    print(f": {stmt.name}", end='')
                print()
