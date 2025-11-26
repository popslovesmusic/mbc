"""Alias generation for stable block identifiers (Am154nb2 format)"""

import hashlib
import re
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Alias:
    """Represents a stable alias for a content block"""
    alias: str  # e.g., "Am154nb2"
    type: str  # 'axiom', 'theorem', 'concept', 'block'
    basis: str  # What the alias is based on (heading, identifier, content hash)


class AliasGenerator:
    """Generates stable aliases in Am154nb2 format

    Format breakdown:
    - Prefix: Am (axiom), Th (theorem), Df (definition), Cn (concept), Bk (block)
    - Number: 3-digit hash-based identifier
    - Letters: 2-3 char content fingerprint
    - Optional suffix: version number

    Examples:
    - Am154nb2 - Axiom, hash 154, fingerprint 'nb', version 2
    - Th892xk  - Theorem, hash 892, fingerprint 'xk'
    - Cn445dm  - Concept, hash 445, fingerprint 'dm'
    """

    PREFIX_MAP = {
        'axiom': 'Am',
        'theorem': 'Th',
        'lemma': 'Lm',
        'corollary': 'Cr',
        'proposition': 'Pr',
        'definition': 'Df',
        'concept': 'Cn',
        'block': 'Bk',
    }

    def __init__(self):
        pass

    def generate(
        self,
        content: str,
        block_type: str = 'block',
        identifier: Optional[str] = None,
        version: Optional[int] = None
    ) -> str:
        """Generate a stable alias for content

        Args:
            content: The content to generate alias for
            block_type: Type of block (axiom, theorem, etc.)
            identifier: Optional existing identifier (e.g., 'A1', 'GA-8')
            version: Optional version number

        Returns:
            Alias string (e.g., 'Am154nb2')
        """
        # Get prefix
        prefix = self.PREFIX_MAP.get(block_type.lower(), 'Bk')

        # If there's an existing identifier, use it
        if identifier:
            return self._generate_from_identifier(prefix, identifier, content, version)

        # Otherwise generate from content hash
        return self._generate_from_content(prefix, content, version)

    def _generate_from_identifier(
        self,
        prefix: str,
        identifier: str,
        content: str,
        version: Optional[int]
    ) -> str:
        """Generate alias from existing identifier (A1, GA-8, etc.)"""

        # Extract numbers from identifier
        numbers = re.findall(r'\d+', identifier)
        if numbers:
            num = int(numbers[0]) % 1000  # Use first number, mod 1000
        else:
            # Fall back to content hash
            return self._generate_from_content(prefix, content, version)

        # Generate fingerprint from identifier text
        letters = re.findall(r'[a-zA-Z]+', identifier)
        if letters:
            fingerprint = ''.join(letters).lower()[:2]
        else:
            fingerprint = self._content_fingerprint(content)

        # Build alias
        alias = f"{prefix}{num:03d}{fingerprint}"

        if version:
            alias += str(version)

        return alias

    def _generate_from_content(
        self,
        prefix: str,
        content: str,
        version: Optional[int]
    ) -> str:
        """Generate alias from content hash"""

        # Hash content to get stable number
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        num = int(content_hash[:6], 16) % 1000  # First 6 hex chars, mod 1000

        # Generate fingerprint
        fingerprint = self._content_fingerprint(content)

        # Build alias
        alias = f"{prefix}{num:03d}{fingerprint}"

        if version:
            alias += str(version)

        return alias

    def _content_fingerprint(self, content: str) -> str:
        """Generate 2-char fingerprint from content

        Uses first significant letters from content
        """
        # Extract first few meaningful words (skip articles, etc.)
        words = re.findall(r'\b[A-Za-z]{3,}\b', content)

        if not words:
            # Fall back to hash
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            return content_hash[:2]

        # Take first letters of first two significant words
        if len(words) >= 2:
            fingerprint = words[0][0].lower() + words[1][0].lower()
        elif len(words) == 1:
            fingerprint = words[0][:2].lower()
        else:
            fingerprint = 'xx'

        return fingerprint

    def generate_batch(
        self,
        blocks: List[dict],
        use_formal_type: bool = True
    ) -> List[Alias]:
        """Generate aliases for multiple blocks

        Args:
            blocks: List of block dicts with 'content', 'type', 'identifier' keys
            use_formal_type: If True, use formal statement type when available

        Returns:
            List of Alias objects
        """
        aliases = []

        for block in blocks:
            content = block.get('content', '')
            block_type = block.get('type', 'block')
            identifier = block.get('identifier')
            version = block.get('version')

            # Determine type
            if use_formal_type and block.get('statement_type'):
                block_type = block['statement_type']

            alias_str = self.generate(
                content=content,
                block_type=block_type,
                identifier=identifier,
                version=version
            )

            basis = identifier if identifier else 'content_hash'

            aliases.append(Alias(
                alias=alias_str,
                type=block_type,
                basis=basis
            ))

        return aliases


def extract_existing_aliases(content: str) -> List[str]:
    """Extract any existing aliases from content

    Looks for patterns like Am154nb2, Th892xk5, etc.

    Returns:
        List of found alias strings
    """
    # Pattern: 2 capital letters, 3 digits, 2-3 lowercase letters, optional digit
    pattern = r'\b([A-Z][a-z]\d{3}[a-z]{2,3}\d?)\b'

    matches = re.findall(pattern, content)
    return list(set(matches))


def parse_alias(alias: str) -> Optional[dict]:
    """Parse an alias into its components

    Args:
        alias: Alias string (e.g., 'Am154nb2')

    Returns:
        Dict with keys: prefix, number, fingerprint, version
        or None if invalid format
    """
    pattern = r'^([A-Z][a-z])(\d{3})([a-z]{2,3})(\d?)$'
    match = re.match(pattern, alias)

    if not match:
        return None

    prefix = match.group(1)
    number = int(match.group(2))
    fingerprint = match.group(3)
    version = int(match.group(4)) if match.group(4) else None

    # Reverse lookup type
    type_map = {v: k for k, v in AliasGenerator.PREFIX_MAP.items()}
    alias_type = type_map.get(prefix, 'unknown')

    return {
        'prefix': prefix,
        'type': alias_type,
        'number': number,
        'fingerprint': fingerprint,
        'version': version,
        'full': alias
    }


if __name__ == "__main__":
    # Test cases
    generator = AliasGenerator()

    # Test axiom with identifier
    axiom_content = "Ψ₀ cannot remain perfectly still; deviation exists: ∃ δ: δΨ₀ ≠ 0."
    alias1 = generator.generate(axiom_content, 'axiom', identifier='A1')
    print(f"Axiom A1: {alias1}")

    # Test theorem
    theorem_content = "The three operators δ, Φ, Π are equivalent."
    alias2 = generator.generate(theorem_content, 'theorem', identifier='Tri-Unity')
    print(f"Tri-Unity Theorem: {alias2}")

    # Test GA-8
    ga8_content = "The Meta-Einstein equation derived from δ-geometry."
    alias3 = generator.generate(ga8_content, 'theorem', identifier='GA-8')
    print(f"GA-8: {alias3}")

    # Test content-only
    concept_content = "Box Algebra defines the semantic operator space."
    alias4 = generator.generate(concept_content, 'concept')
    print(f"Box Algebra concept: {alias4}")

    # Test parsing
    print("\nParsing aliases:")
    for alias in [alias1, alias2, alias3, alias4]:
        parsed = parse_alias(alias)
        if parsed:
            print(f"  {alias} -> {parsed['type']} #{parsed['number']} ({parsed['fingerprint']})")

    # Test extraction
    text = "See Am154nb2 and Th445dm for details. Also check Cn892xk3."
    found = extract_existing_aliases(text)
    print(f"\nFound in text: {found}")
