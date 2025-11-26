"""Source ingestion - scan and register markdown files"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class SourceFile:
    """Represents a registered source markdown file"""
    path: str
    checksum: str
    size_bytes: int
    line_count: int
    relative_path: str


class SourceRegistry:
    """Registry of all source markdown files"""

    def __init__(self, base_dir: str = "HGG-", catalog_dir: str = "catalog"):
        self.base_dir = Path(base_dir)
        self.catalog_dir = Path(catalog_dir)
        self.sources: List[SourceFile] = []

    def scan(self) -> List[SourceFile]:
        """Scan base directory for all .md files"""
        print(f"Scanning {self.base_dir} for markdown files...")

        md_files = list(self.base_dir.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files")

        for md_file in md_files:
            source = self._register_file(md_file)
            self.sources.append(source)
            print(f"  Registered: {source.relative_path}")

        return self.sources

    def _register_file(self, filepath: Path) -> SourceFile:
        """Register a single markdown file"""
        # Read file content
        content = filepath.read_text(encoding='utf-8')

        # Compute checksum
        checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Get file stats
        size_bytes = filepath.stat().st_size
        line_count = len(content.split('\n'))

        # Get relative path
        try:
            relative_path = str(filepath.relative_to(self.base_dir))
        except ValueError:
            relative_path = str(filepath)

        return SourceFile(
            path=str(filepath),
            checksum=checksum,
            size_bytes=size_bytes,
            line_count=line_count,
            relative_path=relative_path
        )

    def save(self, output_file: str = None):
        """Save registry to JSON file"""
        if output_file is None:
            output_file = self.catalog_dir / "sources.json"
        else:
            output_file = Path(output_file)

        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict
        registry_data = {
            'source_count': len(self.sources),
            'sources': [asdict(s) for s in self.sources]
        }

        # Write JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2)

        print(f"\nRegistry saved to {output_file}")
        print(f"Total sources: {len(self.sources)}")

    def load(self, input_file: str = None) -> List[SourceFile]:
        """Load registry from JSON file"""
        if input_file is None:
            input_file = self.catalog_dir / "sources.json"
        else:
            input_file = Path(input_file)

        if not input_file.exists():
            print(f"Registry not found at {input_file}")
            return []

        with open(input_file, 'r', encoding='utf-8') as f:
            registry_data = json.load(f)

        self.sources = [SourceFile(**s) for s in registry_data['sources']]
        print(f"Loaded {len(self.sources)} sources from {input_file}")

        return self.sources


def ingest_sources(base_dir: str = "HGG-", catalog_dir: str = "catalog") -> SourceRegistry:
    """Ingest all markdown sources and create registry

    Args:
        base_dir: Directory containing markdown sources
        catalog_dir: Directory to store catalog data

    Returns:
        SourceRegistry with all registered files
    """
    registry = SourceRegistry(base_dir=base_dir, catalog_dir=catalog_dir)
    registry.scan()
    registry.save()

    return registry


if __name__ == "__main__":
    # Test ingestion
    registry = ingest_sources()
    print(f"\n[OK] Ingestion complete: {len(registry.sources)} files registered")
