"""Location code generation for stable block addressing"""

import re
from pathlib import Path
from typing import List
from .markdown import MarkdownHeading


def slugify_path(filepath: str, base_dir: str = "HGG-") -> str:
    """Convert file path to a clean slug

    Example: HGG-/genesis-0/Tri-Unity_Theorem.md -> genesis-0/tri-unity-theorem
    """
    path = Path(filepath)

    # Get relative path from base_dir
    parts = path.parts
    try:
        base_idx = parts.index(base_dir)
        rel_parts = parts[base_idx + 1:]
    except ValueError:
        rel_parts = parts

    # Remove .md extension from filename
    filename = rel_parts[-1] if rel_parts else path.stem
    filename = filename.replace('.md', '')

    # Slugify filename
    filename_slug = slugify_component(filename)

    # Combine directory + filename
    if len(rel_parts) > 1:
        directory = rel_parts[0]
        return f"{directory}/{filename_slug}"
    else:
        return filename_slug


def slugify_component(text: str) -> str:
    """Slugify a single path component or heading"""
    # Remove special chars, keep hyphens and underscores
    text = re.sub(r'[^\w\s\-_δΦΠΨ]', '', text)
    # Convert to lowercase
    text = text.lower().strip()
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def generate_location_code(
    filepath: str,
    heading_chain: List[MarkdownHeading],
    block_seq: int,
    base_dir: str = "HGG-"
) -> str:
    """Generate a stable location code for a block

    Format: source-slug::heading-chain::block-seq
    Example: genesis-0/tri-unity-theorem::objects-primitives::b1

    Args:
        filepath: Path to the source markdown file
        heading_chain: List of parent headings for this block
        block_seq: Sequential block number under this heading
        base_dir: Base directory name to strip from path

    Returns:
        Stable location code string
    """
    # Source slug
    source_slug = slugify_path(filepath, base_dir)

    # Heading chain slug
    if heading_chain:
        heading_slugs = [h.slug for h in heading_chain]
        heading_chain_str = '::'.join(heading_slugs)
    else:
        heading_chain_str = 'root'

    # Block sequence
    block_id = f"b{block_seq}"

    # Combine
    location_code = f"{source_slug}::{heading_chain_str}::{block_id}"

    return location_code


def generate_card_id(filepath: str, block_num: int) -> str:
    """Generate a short card ID for encyclopedia entries

    Format: DIR#-NNN
    Examples: GEN0-001, GEN5-042, INTK-012

    Args:
        filepath: Path to source file
        block_num: Global block number across all files

    Returns:
        Short card ID
    """
    path = Path(filepath)
    parts = path.parts

    # Extract directory identifier
    dir_prefix = "UNK"
    for part in parts:
        if part.startswith('genesis-'):
            # Extract number
            match = re.search(r'genesis-(\d+)', part)
            if match:
                dir_prefix = f"GEN{match.group(1)}"
                break
        elif part == 'intake':
            dir_prefix = "INTK"
            break
        elif part == 'special':
            dir_prefix = "SPEC"
            break

    # Format with zero-padding
    card_id = f"{dir_prefix}-{block_num:03d}"

    return card_id
