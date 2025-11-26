"""HTML catalog generator with links to source sections"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SourceHTML:
    """Represents an HTML version of a source file"""
    source_path: str
    html_path: str
    title: str


class HTMLGenerator:
    """Generate browsable HTML catalog with source links"""

    def __init__(self, catalog_dir: str = "catalog", output_dir: str = "catalog-html"):
        self.catalog_dir = Path(catalog_dir)
        self.output_dir = Path(output_dir)
        self.sources_html_dir = self.output_dir / "sources"
        self.sources_html_dir.mkdir(parents=True, exist_ok=True)

    def generate_source_html(self, source_path: str, base_dir: str = "HGG-") -> SourceHTML:
        """Convert a markdown source file to HTML with line anchors

        Args:
            source_path: Path to source markdown file
            base_dir: Base directory for sources

        Returns:
            SourceHTML with path info
        """
        source_file = Path(source_path)

        # Read source content
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Get relative path for output
        try:
            rel_path = source_file.relative_to(base_dir)
        except ValueError:
            rel_path = source_file

        # Create output path
        html_filename = str(rel_path).replace('\\', '_').replace('/', '_').replace('.md', '.html')
        html_path = self.sources_html_dir / html_filename

        # Generate HTML
        html = self._create_source_html(lines, source_file.name, str(rel_path))

        # Write HTML file
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return SourceHTML(
            source_path=str(source_file),
            html_path=str(html_path.relative_to(self.output_dir)),
            title=source_file.name
        )

    def _create_source_html(self, lines: List[str], title: str, source_path: str) -> str:
        """Create HTML for a source file with line numbers and anchors"""

        # Escape HTML in content
        def escape_html(text):
            return (text.replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;')
                       .replace('"', '&quot;'))

        # Build line HTML
        lines_html = []
        for i, line in enumerate(lines, start=1):
            line_html = escape_html(line.rstrip('\n'))

            # Add syntax highlighting for markdown
            line_html = self._highlight_markdown(line_html)

            lines_html.append(
                f'<div class="line" id="L{i}">'
                f'<span class="line-number">{i}</span>'
                f'<span class="line-content">{line_html}</span>'
                f'</div>'
            )

        content_html = '\n'.join(lines_html)

        # Generate full HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }}
        .header {{
            background: #2d2d30;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .header h1 {{
            margin: 0 0 5px 0;
            font-size: 18px;
            color: #4ec9b0;
        }}
        .header .path {{
            color: #858585;
            font-size: 12px;
        }}
        .source-content {{
            background: #1e1e1e;
            border: 1px solid #3e3e42;
            border-radius: 5px;
            overflow: auto;
        }}
        .line {{
            display: flex;
            line-height: 1.6;
            min-height: 20px;
        }}
        .line:target {{
            background: #264f78;
        }}
        .line:hover {{
            background: #2a2d2e;
        }}
        .line-number {{
            flex-shrink: 0;
            width: 60px;
            padding: 2px 10px;
            text-align: right;
            color: #858585;
            border-right: 1px solid #3e3e42;
            user-select: none;
        }}
        .line-content {{
            flex: 1;
            padding: 2px 15px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        /* Markdown syntax highlighting */
        .heading {{ color: #4ec9b0; font-weight: bold; }}
        .bold {{ color: #dcdcaa; font-weight: bold; }}
        .italic {{ color: #ce9178; font-style: italic; }}
        .code {{ color: #ce9178; background: #2d2d30; padding: 2px 4px; }}
        .link {{ color: #3794ff; }}
        .list-marker {{ color: #569cd6; }}
        .greek {{ color: #c586c0; }}
        .math {{ color: #4fc1ff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="path">{source_path}</div>
    </div>
    <div class="source-content">
        {content_html}
    </div>
</body>
</html>'''

        return html

    def _highlight_markdown(self, line: str) -> str:
        """Apply basic syntax highlighting to markdown"""

        # Headings
        if line.strip().startswith('#'):
            line = f'<span class="heading">{line}</span>'
            return line

        # Bold
        line = re.sub(r'\*\*([^*]+)\*\*', r'<span class="bold">**\1**</span>', line)

        # Italic
        line = re.sub(r'\*([^*]+)\*', r'<span class="italic">*\1*</span>', line)

        # Code
        line = re.sub(r'`([^`]+)`', r'<span class="code">`\1`</span>', line)

        # Greek letters
        line = re.sub(r'([δΦΠΨΣΩΛΓΘαβγλμνωηξζρστ])', r'<span class="greek">\1</span>', line)

        # Math symbols
        line = re.sub(r'([∀∃∈∉⊂⊃∩∪∧∨¬→↔∫∂∇∆∑∏])', r'<span class="math">\1</span>', line)

        # List markers
        line = re.sub(r'^(\s*[-*+]\s)', r'<span class="list-marker">\1</span>', line)

        return line

    def generate_catalog_html(self, cards_file: str = None, enhanced: bool = True) -> str:
        """Generate main catalog HTML browser

        Args:
            cards_file: Path to cards JSONL file
            enhanced: Use enhanced cards if True

        Returns:
            Path to generated HTML file
        """
        if cards_file is None:
            if enhanced:
                cards_file = self.catalog_dir / "indexes" / "cards-enhanced.jsonl"
            else:
                cards_file = self.catalog_dir / "indexes" / "cards.jsonl"
        else:
            cards_file = Path(cards_file)

        if not cards_file.exists():
            raise FileNotFoundError(f"Cards file not found: {cards_file}")

        # Load cards
        cards = []
        with open(cards_file, 'r', encoding='utf-8') as f:
            for line in f:
                card = json.loads(line)
                cards.append(card)

        print(f"Loaded {len(cards)} cards")

        # Generate HTML for all sources (track which ones we need)
        source_htmls = {}
        sources_to_convert = set(card['source'] for card in cards)

        print(f"Converting {len(sources_to_convert)} source files to HTML...")
        for i, source_path in enumerate(sources_to_convert, 1):
            if i % 10 == 0:
                print(f"  Converted {i}/{len(sources_to_convert)} sources...")

            full_path = Path("HGG-") / source_path
            if full_path.exists():
                source_html = self.generate_source_html(str(full_path))
                source_htmls[source_path] = source_html

        print(f"Converted {len(source_htmls)} sources to HTML")

        # Generate catalog HTML
        html = self._create_catalog_html(cards, source_htmls, enhanced)

        # Write catalog HTML
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\nCatalog HTML saved to {output_file}")
        return str(output_file)

    def _create_catalog_html(self, cards: List[Dict], source_htmls: Dict[str, SourceHTML], enhanced: bool) -> str:
        """Create the main catalog HTML page"""

        # Group cards by source directory
        by_directory = {}
        for card in cards:
            source = card['source']
            directory = source.split('\\')[0] if '\\' in source else source.split('/')[0]
            if directory not in by_directory:
                by_directory[directory] = []
            by_directory[directory].append(card)

        # Generate cards HTML
        cards_html = []
        for directory in sorted(by_directory.keys()):
            dir_cards = by_directory[directory]

            cards_html.append(f'<div class="directory-section" data-directory="{directory}">')
            cards_html.append(f'<h2>{directory} <span class="count">({len(dir_cards)} cards)</span></h2>')

            for card in dir_cards:
                card_html = self._create_card_html(card, source_htmls, enhanced)
                cards_html.append(card_html)

            cards_html.append('</div>')

        cards_content = '\n'.join(cards_html)

        # Create full HTML page
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HGG Catalog Browser</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }}
        .header {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        .header .subtitle {{
            color: #ecf0f1;
            font-size: 14px;
        }}
        .controls {{
            background: white;
            padding: 15px 20px;
            border-bottom: 1px solid #ddd;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .search-box {{
            flex: 1;
            min-width: 300px;
        }}
        .search-box input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        .filter-group {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .filter-group label {{
            font-size: 14px;
            color: #666;
        }}
        .filter-group select {{
            padding: 6px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        .content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .stats {{
            background: white;
            padding: 15px 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        .directory-section {{
            margin-bottom: 30px;
        }}
        .directory-section h2 {{
            background: #34495e;
            color: white;
            padding: 10px 15px;
            margin: 0 0 15px 0;
            border-radius: 5px;
            font-size: 18px;
        }}
        .directory-section h2 .count {{
            font-weight: normal;
            opacity: 0.8;
            font-size: 14px;
        }}
        .card {{
            background: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: box-shadow 0.2s;
        }}
        .card:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }}
        .card-id {{
            font-family: 'Courier New', monospace;
            background: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }}
        .card-heading {{
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin: 0 0 8px 0;
        }}
        .card-location {{
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 8px;
        }}
        .card-excerpt {{
            color: #555;
            font-size: 14px;
            line-height: 1.5;
            margin: 10px 0;
        }}
        .card-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        .tag {{
            background: #ecf0f1;
            color: #2c3e50;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 500;
        }}
        .tag.formal {{ background: #e8f5e9; color: #2e7d32; }}
        .tag.technical {{ background: #e3f2fd; color: #1565c0; }}
        .tag.conversational {{ background: #fff3e0; color: #e65100; }}
        .tag.contradiction {{ background: #ffebee; color: #c62828; }}
        .tag.ambiguous {{ background: #fff9c4; color: #f57f17; }}
        .tag.definitive {{ background: #e8f5e9; color: #388e3c; }}
        .concepts {{
            margin-top: 10px;
            font-size: 12px;
        }}
        .concepts strong {{
            color: #666;
        }}
        .concepts .concept {{
            display: inline-block;
            background: #f8f9fa;
            padding: 2px 6px;
            margin: 2px;
            border-radius: 2px;
            color: #555;
        }}
        .source-link {{
            display: inline-block;
            margin-top: 10px;
            color: #3498db;
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
        }}
        .source-link:hover {{
            text-decoration: underline;
        }}
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 HGG Catalog Browser</h1>
        <div class="subtitle">Semantic index of {len(cards)} blocks across {len(by_directory)} directories · <a href="analytics.html" style="color: #3498db;">View Analytics 📊</a></div>
    </div>

    <div class="controls">
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search cards by heading, concepts, or content...">
        </div>
        <div class="filter-group">
            <label>Directory:</label>
            <select id="directoryFilter">
                <option value="">All</option>
                {''.join(f'<option value="{d}">{d}</option>' for d in sorted(by_directory.keys()))}
            </select>
        </div>
        {'<div class="filter-group"><label>Type:</label><select id="typeFilter"><option value="">All</option><option value="formal">Formal</option><option value="technical">Technical</option><option value="conversational">Conversational</option></select></div>' if enhanced else ''}
    </div>

    <div class="content">
        <div class="stats">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">{len(cards)}</div>
                    <div class="stat-label">Total Cards</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(by_directory)}</div>
                    <div class="stat-label">Directories</div>
                </div>
                {'<div class="stat-item"><div class="stat-value">' + str(sum(1 for c in cards if c.get('is_formal'))) + '</div><div class="stat-label">Formal Statements</div></div>' if enhanced else ''}
                {'<div class="stat-item"><div class="stat-value">' + str(sum(1 for c in cards if c.get('is_technical'))) + '</div><div class="stat-label">Technical Blocks</div></div>' if enhanced else ''}
            </div>
        </div>

        <div id="cardsContainer">
            {cards_content}
        </div>

        <div id="noResults" class="no-results" style="display: none;">
            No cards match your filters.
        </div>
    </div>

    <script>
        // Search and filter functionality
        const searchInput = document.getElementById('searchInput');
        const directoryFilter = document.getElementById('directoryFilter');
        const typeFilter = document.getElementById('typeFilter');
        const cardsContainer = document.getElementById('cardsContainer');
        const noResults = document.getElementById('noResults');

        function filterCards() {{
            const searchTerm = searchInput.value.toLowerCase();
            const directory = directoryFilter.value;
            const type = typeFilter ? typeFilter.value : '';

            const sections = document.querySelectorAll('.directory-section');
            let visibleCount = 0;

            sections.forEach(section => {{
                const sectionDir = section.dataset.directory;
                let sectionVisible = false;

                if (directory && sectionDir !== directory) {{
                    section.style.display = 'none';
                    return;
                }}

                const cards = section.querySelectorAll('.card');
                cards.forEach(card => {{
                    let visible = true;

                    // Search filter
                    if (searchTerm) {{
                        const text = card.textContent.toLowerCase();
                        visible = text.includes(searchTerm);
                    }}

                    // Type filter
                    if (visible && type) {{
                        const tags = Array.from(card.querySelectorAll('.tag')).map(t => t.textContent.toLowerCase());
                        visible = tags.includes(type);
                    }}

                    card.style.display = visible ? 'block' : 'none';
                    if (visible) {{
                        sectionVisible = true;
                        visibleCount++;
                    }}
                }});

                section.style.display = sectionVisible ? 'block' : 'none';
            }});

            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            cardsContainer.style.display = visibleCount === 0 ? 'none' : 'block';
        }}

        searchInput.addEventListener('input', filterCards);
        directoryFilter.addEventListener('change', filterCards);
        if (typeFilter) typeFilter.addEventListener('change', filterCards);
    </script>
</body>
</html>'''

        return html

    def _create_card_html(self, card: Dict, source_htmls: Dict[str, SourceHTML], enhanced: bool) -> str:
        """Create HTML for a single card"""

        # Get source HTML link
        source = card['source']
        source_html = source_htmls.get(source)

        if source_html:
            # Extract line numbers
            lines = card.get('lines', '')
            if lines and '-' in lines:
                start_line = lines.split('-')[0]
                source_url = f"sources/{Path(source_html.html_path).name}#L{start_line}"
            else:
                source_url = f"sources/{Path(source_html.html_path).name}"
        else:
            source_url = "#"

        # Build tags
        tags_html = []

        if enhanced:
            if card.get('is_formal'):
                tags_html.append('<span class="tag formal">Formal</span>')
            if card.get('is_technical'):
                tags_html.append('<span class="tag technical">Technical</span>')
            if card.get('conversational_score', 0) > 0.5:
                tags_html.append('<span class="tag conversational">Conversational</span>')
            if card.get('has_contradictions'):
                tags_html.append('<span class="tag contradiction">Contradictions</span>')
            if card.get('has_ambiguity'):
                tags_html.append('<span class="tag ambiguous">Ambiguous</span>')
            if card.get('is_definitive'):
                tags_html.append('<span class="tag definitive">Definitive</span>')

            # Add custom tags
            for tag in card.get('tags', []):
                if tag not in ['formal', 'technical', 'conversational', 'definitive']:
                    tags_html.append(f'<span class="tag">{tag}</span>')

        # Build concepts
        concepts = card.get('concepts', [])
        concepts_html = ''
        if concepts:
            concept_spans = ''.join(f'<span class="concept">{c}</span>' for c in concepts[:10])
            concepts_html = f'<div class="concepts"><strong>Concepts:</strong> {concept_spans}</div>'

        card_html = f'''
<div class="card">
    <div class="card-header">
        <span class="card-id">{card['id']}</span>
    </div>
    <div class="card-heading">{card['heading']}</div>
    <div class="card-location">{card['location']}</div>
    <div class="card-excerpt">{card.get('excerpt', '')}</div>
    <div class="card-meta">
        {''.join(tags_html)}
    </div>
    {concepts_html}
    <a href="{source_url}" class="source-link" target="_blank">→ View in source (lines {card.get('lines', 'N/A')})</a>
</div>'''

        return card_html


def generate_html_catalog(catalog_dir: str = "catalog", output_dir: str = "catalog-html", enhanced: bool = True):
    """Generate complete HTML catalog

    Args:
        catalog_dir: Catalog directory
        output_dir: Output directory for HTML
        enhanced: Use enhanced cards

    Returns:
        Path to generated index.html
    """
    generator = HTMLGenerator(catalog_dir=catalog_dir, output_dir=output_dir)
    return generator.generate_catalog_html(enhanced=enhanced)


if __name__ == "__main__":
    # Test generation
    output_file = generate_html_catalog(enhanced=True)
    print(f"\n✓ HTML catalog generated!")
    print(f"Open in browser: file:///{output_file}")
