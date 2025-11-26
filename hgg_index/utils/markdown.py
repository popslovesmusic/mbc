"""Markdown parsing utilities"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MarkdownHeading:
    """Represents a markdown heading"""
    level: int
    text: str
    line_num: int
    slug: str

    @staticmethod
    def slugify(text: str) -> str:
        """Convert heading text to a URL-friendly slug"""
        # Remove markdown formatting
        text = re.sub(r'\*+', '', text)
        # Remove special chars but keep math symbols and hyphens
        text = re.sub(r'[^\w\s\-δΦΠΨ]', '', text)
        # Convert to lowercase and replace spaces with hyphens
        text = text.lower().strip()
        text = re.sub(r'[\s_]+', '-', text)
        # Remove duplicate hyphens
        text = re.sub(r'-+', '-', text)
        return text.strip('-')


@dataclass
class MarkdownBlock:
    """Represents a content block (paragraph, list, etc.)"""
    content: str
    start_line: int
    end_line: int
    heading_chain: List[MarkdownHeading]
    block_type: str  # 'paragraph', 'list', 'table', 'code', 'equation'


class MarkdownParser:
    """Parse markdown files into structured sections"""

    def __init__(self, content: str):
        self.lines = content.split('\n')
        self.headings: List[MarkdownHeading] = []
        self.blocks: List[MarkdownBlock] = []

    def parse(self):
        """Parse markdown content into headings and blocks"""
        self._extract_headings()
        self._extract_blocks()
        return self.headings, self.blocks

    def _extract_headings(self):
        """Extract all headings from the document"""
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')

        for i, line in enumerate(self.lines, start=1):
            match = heading_pattern.match(line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                slug = MarkdownHeading.slugify(text)

                self.headings.append(MarkdownHeading(
                    level=level,
                    text=text,
                    line_num=i,
                    slug=slug
                ))

    def _extract_blocks(self):
        """Extract content blocks between headings"""
        if not self.headings:
            # No headings, treat entire file as one block
            if self.lines:
                self.blocks.append(MarkdownBlock(
                    content='\n'.join(self.lines),
                    start_line=1,
                    end_line=len(self.lines),
                    heading_chain=[],
                    block_type='paragraph'
                ))
            return

        # Process blocks between headings
        for i, heading in enumerate(self.headings):
            start_line = heading.line_num + 1

            # Determine end line (next heading or end of file)
            if i + 1 < len(self.headings):
                end_line = self.headings[i + 1].line_num - 1
            else:
                end_line = len(self.lines)

            # Skip empty blocks
            if start_line > end_line:
                continue

            # Get heading chain (parent headings)
            heading_chain = self._get_heading_chain(i)

            # Extract content
            content_lines = self.lines[start_line-1:end_line]
            content = '\n'.join(content_lines).strip()

            if content:
                # Determine block type
                block_type = self._detect_block_type(content)

                self.blocks.append(MarkdownBlock(
                    content=content,
                    start_line=start_line,
                    end_line=end_line,
                    heading_chain=heading_chain,
                    block_type=block_type
                ))

    def _get_heading_chain(self, heading_idx: int) -> List[MarkdownHeading]:
        """Get the chain of parent headings for a given heading"""
        chain = []
        current_heading = self.headings[heading_idx]
        chain.append(current_heading)

        # Walk backwards to find parent headings
        for i in range(heading_idx - 1, -1, -1):
            if self.headings[i].level < current_heading.level:
                chain.insert(0, self.headings[i])
                current_heading = self.headings[i]
                if current_heading.level == 1:
                    break

        return chain

    def _detect_block_type(self, content: str) -> str:
        """Detect the type of content block"""
        content_stripped = content.strip()

        # Code block
        if content_stripped.startswith('```'):
            return 'code'

        # Table
        if '|' in content and re.search(r'\|[\s\-:]+\|', content):
            return 'table'

        # List
        if re.match(r'^[\*\-\+]\s', content_stripped, re.MULTILINE) or \
           re.match(r'^\d+\.\s', content_stripped, re.MULTILINE):
            return 'list'

        # Equation (inline math or display math)
        if '$$' in content or re.search(r'\\\(.+?\\\)', content):
            return 'equation'

        return 'paragraph'


def parse_markdown_file(filepath: str) -> tuple[List[MarkdownHeading], List[MarkdownBlock]]:
    """Parse a markdown file and return headings and blocks"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = MarkdownParser(content)
    return parser.parse()
