"""Segmentation - split documents into semantic blocks with location codes"""

import json
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict

from .utils.markdown import parse_markdown_file, MarkdownBlock, MarkdownHeading
from .utils.location import generate_location_code, generate_card_id


@dataclass
class Segment:
    """Represents a semantic segment (block with metadata)"""
    id: str  # Card ID (e.g., GEN0-001)
    location_code: str  # Full location code
    source_path: str
    source_relative: str
    heading: str  # Immediate heading text
    heading_chain: List[str]  # Full heading chain as strings
    content: str
    start_line: int
    end_line: int
    block_type: str
    block_seq: int  # Sequence number under this heading


class Segmenter:
    """Segments markdown files into semantic blocks"""

    def __init__(self, base_dir: str = "HGG-", catalog_dir: str = "catalog"):
        self.base_dir = Path(base_dir)
        self.catalog_dir = Path(catalog_dir)
        self.segments: List[Segment] = []
        self.global_block_num = 1  # Global counter for card IDs

    def segment_file(self, filepath: str) -> List[Segment]:
        """Segment a single markdown file into blocks"""
        print(f"Segmenting: {filepath}")

        # Parse markdown
        headings, blocks = parse_markdown_file(filepath)

        if not blocks:
            print(f"  No blocks found")
            return []

        # Get relative path
        try:
            relative_path = str(Path(filepath).relative_to(self.base_dir))
        except ValueError:
            relative_path = filepath

        # Group blocks by heading
        file_segments = []
        heading_block_counts: Dict[str, int] = {}  # Track block seq per heading

        for block in blocks:
            # Get heading chain
            if block.heading_chain:
                heading = block.heading_chain[-1].text
                heading_chain_str = [h.text for h in block.heading_chain]

                # Get heading key for sequence tracking
                heading_key = '::'.join([h.slug for h in block.heading_chain])
            else:
                heading = "(root)"
                heading_chain_str = []
                heading_key = "root"

            # Increment block sequence for this heading
            if heading_key not in heading_block_counts:
                heading_block_counts[heading_key] = 0
            heading_block_counts[heading_key] += 1
            block_seq = heading_block_counts[heading_key]

            # Generate location code
            location_code = generate_location_code(
                filepath=filepath,
                heading_chain=block.heading_chain,
                block_seq=block_seq,
                base_dir=str(self.base_dir)
            )

            # Generate card ID
            card_id = generate_card_id(filepath, self.global_block_num)
            self.global_block_num += 1

            # Create segment
            segment = Segment(
                id=card_id,
                location_code=location_code,
                source_path=filepath,
                source_relative=relative_path,
                heading=heading,
                heading_chain=heading_chain_str,
                content=block.content,
                start_line=block.start_line,
                end_line=block.end_line,
                block_type=block.block_type,
                block_seq=block_seq
            )

            file_segments.append(segment)

        print(f"  Created {len(file_segments)} segments")
        return file_segments

    def segment_all(self, source_files: List[str]) -> List[Segment]:
        """Segment all source files"""
        print(f"\nSegmenting {len(source_files)} files...")

        self.segments = []
        self.global_block_num = 1

        for filepath in source_files:
            file_segments = self.segment_file(filepath)
            self.segments.extend(file_segments)

        print(f"\nTotal segments created: {len(self.segments)}")
        return self.segments

    def save(self, output_file: str = None):
        """Save segments to JSONL file"""
        if output_file is None:
            output_file = self.catalog_dir / "indexes" / "segments.jsonl"
        else:
            output_file = Path(output_file)

        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write JSONL
        with open(output_file, 'w', encoding='utf-8') as f:
            for segment in self.segments:
                json.dump(asdict(segment), f)
                f.write('\n')

        print(f"\nSegments saved to {output_file}")

    def save_location_index(self, output_file: str = None):
        """Save simple text index of location codes"""
        if output_file is None:
            output_file = self.catalog_dir / "indexes" / "location-index.txt"
        else:
            output_file = Path(output_file)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for segment in self.segments:
                f.write(f"{segment.id}\t{segment.location_code}\n")

        print(f"Location index saved to {output_file}")


def segment_sources(
    source_files: List[str],
    base_dir: str = "HGG-",
    catalog_dir: str = "catalog"
) -> Segmenter:
    """Segment all source files into semantic blocks

    Args:
        source_files: List of markdown file paths to segment
        base_dir: Base directory for sources
        catalog_dir: Directory to store catalog data

    Returns:
        Segmenter with all segments
    """
    segmenter = Segmenter(base_dir=base_dir, catalog_dir=catalog_dir)
    segmenter.segment_all(source_files)
    segmenter.save()
    segmenter.save_location_index()

    return segmenter


if __name__ == "__main__":
    # Test segmentation
    from .ingest import SourceRegistry

    # Load sources
    registry = SourceRegistry()
    sources = registry.load()

    if sources:
        source_paths = [s.path for s in sources]
        segmenter = segment_sources(source_paths)
        print(f"\n[OK] Segmentation complete: {len(segmenter.segments)} segments")
