#!/usr/bin/env python3
"""
Universal Markdown Chapter Splitter
Usage: python universal_split.py <path_to_file_or_directory>
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def extract_chapters(md_file_path):
    """Extract chapters from a markdown file based on level-1 headings."""
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {md_file_path}: {e}")
        return []

    # Regex for Level 1 headers (# Title)
    pattern = r'^# (.+)$'
    matches = list(re.finditer(pattern, content, re.MULTILINE))

    if not matches:
        print(f"  [!] No chapters (Level-1 Headers) found in {md_file_path.name}")
        return []

    chapters = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start_pos = match.start()

        # Find end position (start of next chapter or end of file)
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)

        chapter_content = content[start_pos:end_pos].strip()
        chapters.append({
            'title': title,
            'content': chapter_content,
            'number': i + 1
        })

    return chapters

def sanitize_filename(title):
    """Convert chapter title to safe filename."""
    title = re.sub(r'\*\*', '', title) # Remove bold
    title = re.sub(r'[<>:"/\\|?*]', '', title) # Remove illegal chars
    title = title.replace(' ', '_') # Spaces to underscores
    return title[:100] # Limit length

def create_summary(output_dir, source_file, chapter_info):
    """Create a summary/index file for the directory."""
    summary_path = output_dir / "00_INDEX.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# Index: {source_file}\n\n")
        f.write(f"**Total Chapters:** {len(chapter_info)}\n\n")
        f.write("---\n\n")
        f.write("## Chapter List\n\n")
        for ch in chapter_info:
            f.write(f"{ch['number']}. **{ch['title']}**\n")
            f.write(f"   - File: `{ch['filename']}`\n\n")
    print(f"  ✓ Created index: {summary_path.name}")

def process_single_file(md_file, output_root):
    """Process a single markdown file."""
    
    # 1. Determine Output Directory
    # Creates a folder named after the file (e.g., "MyBook.md" -> "MyBook/")
    dest_dir = output_root / md_file.stem

    # 2. Clean/Create Directory
    if dest_dir.exists():
        # Safely remove old version to ensure clean extraction
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nProcessing: {md_file.name}")
    print(f"Target:     {dest_dir}")
    print(f"{'-'*60}")

    # 3. Extract
    chapters = extract_chapters(md_file)
    
    if not chapters:
        return 0

    # 4. Save Chapters
    chapter_info = []
    for chapter in chapters:
        safe_title = sanitize_filename(chapter['title'])
        filename = f"Chapter_{chapter['number']:02d}_{safe_title}.md"
        filepath = dest_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(chapter['content'])

        chapter_info.append({
            'number': chapter['number'],
            'title': chapter['title'],
            'filename': filename
        })
        print(f"  [{chapter['number']:02d}] {chapter['title'][:60]}")

    # 5. Create Index
    create_summary(dest_dir, md_file.name, chapter_info)
    return len(chapters)

def main():
    parser = argparse.ArgumentParser(description="Split Markdown files by Level-1 Headers.")
    parser.add_argument("input_path", help="Path to a single .md file OR a folder containing .md files")
    parser.add_argument("-o", "--output", help="Optional custom output directory (default: same as input)", default=None)
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    
    # Determine Output Root
    if args.output:
        output_root = Path(args.output)
    else:
        # If no output specified, use the parent of the file or the folder itself
        output_root = input_path.parent if input_path.is_file() else input_path

    files_to_process = []

    # Logic to handle File vs Directory
    if input_path.is_file():
        if input_path.suffix.lower() == '.md':
            files_to_process.append(input_path)
        else:
            print("Error: Input file must be a .md file.")
            return
    elif input_path.is_dir():
        print(f"Scanning directory: {input_path}")
        files_to_process = list(input_path.glob("*.md"))
    else:
        print(f"Error: Path not found: {input_path}")
        return

    if not files_to_process:
        print("No .md files found to process.")
        return

    print(f"{'='*60}")
    print(f"Found {len(files_to_process)} files to process.")
    print(f"{'='*60}")

    total_chapters = 0
    for md_file in files_to_process:
        total_chapters += process_single_file(md_file, output_root)

    print(f"\n{'='*60}")
    print(f"COMPLETE. Extracted {total_chapters} chapters total.")
    print(f"{'='*60}")

    # Keep window open if running from double-click/bat
    if sys.platform == 'win32':
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()