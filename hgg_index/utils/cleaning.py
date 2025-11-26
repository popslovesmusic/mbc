"""Conversational text detection and cleaning for ChatGPT transcripts"""

import re
from typing import Tuple, List


class ConversationalDetector:
    """Detects conversational patterns in ChatGPT transcripts"""

    # Common ChatGPT opening patterns
    CHATGPT_OPENINGS = [
        r"^Here'?s?\s",
        r"^Let'?s?\s",
        r"^I'?ll\s",
        r"^I'?m\s",
        r"^I can\s",
        r"^I will\s",
        r"^You'?re\s",
        r"^You can\s",
        r"^We can\s",
        r"^We'?ll\s",
        r"^This is\s",
        r"^That'?s?\s",
        r"^Great question",
        r"^Good question",
        r"^Excellent",
        r"^Perfect",
        r"^Absolutely",
        r"^Certainly",
        r"^Of course",
        r"^Sure",
        r"^Yes,?\s",
        r"^No,?\s",
    ]

    # Meta-commentary patterns
    META_PATTERNS = [
        r"note to self",
        r"todo:?",
        r"to-?do:?",
        r"fixme",
        r"please see",
        r"see above",
        r"see below",
        r"as mentioned",
        r"as we discussed",
        r"remember that",
        r"don'?t forget",
        r"keep in mind",
    ]

    # Dialogue markers
    DIALOGUE_MARKERS = [
        r"^User:",
        r"^Assistant:",
        r"^Human:",
        r"^AI:",
        r"^Q:",
        r"^A:",
        r"^Question:",
        r"^Answer:",
    ]

    # Imperative/instructional patterns
    INSTRUCTIONAL_PATTERNS = [
        r"^Let me explain",
        r"^Let me show",
        r"^I'?ll demonstrate",
        r"^To understand",
        r"^To see",
        r"^Notice that",
        r"^Observe that",
        r"^Consider",
        r"^Imagine",
        r"^Think about",
        r"^Think of",
    ]

    def __init__(self):
        self.opening_pattern = re.compile(
            '|'.join(self.CHATGPT_OPENINGS),
            re.IGNORECASE | re.MULTILINE
        )
        self.meta_pattern = re.compile(
            '|'.join(self.META_PATTERNS),
            re.IGNORECASE
        )
        self.dialogue_pattern = re.compile(
            '|'.join(self.DIALOGUE_MARKERS),
            re.MULTILINE
        )
        self.instructional_pattern = re.compile(
            '|'.join(self.INSTRUCTIONAL_PATTERNS),
            re.IGNORECASE | re.MULTILINE
        )

    def detect_conversational(self, text: str) -> Tuple[bool, List[str]]:
        """Detect if text contains conversational patterns

        Returns:
            (is_conversational, list_of_detected_patterns)
        """
        detected = []

        # Check for dialogue markers
        if self.dialogue_pattern.search(text):
            detected.append("dialogue_marker")

        # Check for ChatGPT openings
        if self.opening_pattern.search(text):
            detected.append("chatgpt_opening")

        # Check for meta-commentary
        if self.meta_pattern.search(text):
            detected.append("meta_commentary")

        # Check for instructional language
        if self.instructional_pattern.search(text):
            detected.append("instructional")

        # Check for questions directed at reader
        if re.search(r'\?\s*$', text) and re.search(r'^(Why|What|How|Where|When|Who)', text, re.MULTILINE):
            detected.append("rhetorical_question")

        is_conversational = len(detected) > 0

        return is_conversational, detected

    def get_conversational_score(self, text: str) -> float:
        """Calculate conversational score (0.0 = technical, 1.0 = very conversational)"""
        is_conv, patterns = self.detect_conversational(text)

        if not is_conv:
            return 0.0

        # Weight different patterns
        score = 0.0
        weights = {
            'dialogue_marker': 1.0,      # Definitely conversational
            'chatgpt_opening': 0.8,      # Likely conversational
            'meta_commentary': 0.6,      # Probably conversational
            'instructional': 0.4,        # Maybe conversational
            'rhetorical_question': 0.3,  # Could be technical
        }

        for pattern in patterns:
            score += weights.get(pattern, 0.5)

        # Normalize to 0-1 range
        max_score = len(weights)
        return min(1.0, score / max_score)


def is_technical_content(text: str) -> bool:
    """Check if content is clearly technical (equations, symbols, definitions)"""

    # Check for mathematical content
    math_patterns = [
        r'\$\$',                    # Display math
        r'\\\[',                    # LaTeX display
        r'\\begin\{',              # LaTeX environments
        r'[∀∃∈∉⊂⊃∩∪∧∨¬→↔]',      # Logic symbols
        r'[∫∂∇∆∑∏]',              # Calculus symbols
        r'[αβγδεζηθικλμνξοπρστυφχψω]',  # Greek lowercase
        r'[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]',  # Greek uppercase
    ]

    for pattern in math_patterns:
        if re.search(pattern, text):
            return True

    # Check for formal definitions
    if re.search(r'^(Definition|Theorem|Lemma|Corollary|Proposition|Axiom)\s*\d*[.:]', text, re.MULTILINE | re.IGNORECASE):
        return True

    # Check for formal proof language
    if re.search(r'(Proof|QED|∎|□)', text):
        return True

    return False


def clean_conversational_text(text: str, aggressive: bool = False) -> Tuple[str, List[str]]:
    """Remove conversational text while preserving technical content

    Args:
        text: Input text
        aggressive: If True, remove more aggressively

    Returns:
        (cleaned_text, list_of_removed_patterns)
    """
    # Don't clean if clearly technical
    if is_technical_content(text):
        return text, []

    detector = ConversationalDetector()
    is_conv, patterns = detector.detect_conversational(text)

    if not is_conv:
        return text, []

    removed = []
    cleaned = text

    # Remove dialogue markers
    if 'dialogue_marker' in patterns:
        lines = cleaned.split('\n')
        new_lines = []
        for line in lines:
            if not re.match(r'^(User:|Assistant:|Human:|AI:|Q:|A:|Question:|Answer:)', line, re.IGNORECASE):
                new_lines.append(line)
            else:
                removed.append(f"dialogue: {line[:50]}")
        cleaned = '\n'.join(new_lines)

    # Remove meta-commentary lines (if aggressive)
    if aggressive and 'meta_commentary' in patterns:
        lines = cleaned.split('\n')
        new_lines = []
        for line in lines:
            if not detector.meta_pattern.search(line):
                new_lines.append(line)
            else:
                removed.append(f"meta: {line[:50]}")
        cleaned = '\n'.join(new_lines)

    return cleaned, removed


if __name__ == "__main__":
    # Test cases
    detector = ConversationalDetector()

    test_cases = [
        "Here's how the δ-operator works in Box Calculus.",
        "The δ-operator is defined as δ: Φ → Φ.",
        "User: What is the Box? Assistant: The Box is...",
        "Note to self: TODO - add more examples here",
        "Let me explain how Meta-Genesis works.",
        "## Axiom A1: Deviation Necessity\n\nδΨ₀ ≠ 0",
    ]

    for text in test_cases:
        is_conv, patterns = detector.detect_conversational(text)
        score = detector.get_conversational_score(text)
        tech = is_technical_content(text)
        print(f"\nText: {text[:60]}...")
        print(f"  Conversational: {is_conv} (score: {score:.2f})")
        print(f"  Patterns: {patterns}")
        print(f"  Technical: {tech}")
