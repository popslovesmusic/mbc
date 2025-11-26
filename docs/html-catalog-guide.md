# HGG HTML Catalog - User Guide

## Overview

The HGG HTML Catalog is a **web-based browser interface** for exploring your semantic markdown library. It provides:

- **Interactive catalog browser** with search and filters
- **Analytics dashboard** with charts and visualizations
- **Source file viewer** with syntax highlighting and line numbers
- **Direct links** from catalog cards to specific sections in source files

## Generating the HTML Catalog

### Quick Start

```bash
python generate-html-catalog.py
```

This generates:
- `catalog-html/index.html` - Main catalog browser
- `catalog-html/analytics.html` - Analytics dashboard
- `catalog-html/sources/*.html` - 81 source files as HTML

### Open in Browser

```bash
# Windows
start catalog-html/index.html

# Mac/Linux
open catalog-html/index.html
# or
xdg-open catalog-html/index.html
```

Or navigate to: `file:///path/to/catalog-html/index.html`

## Catalog Browser Features

### 1. Search

The search box filters cards in real-time by:
- **Heading text**
- **Concepts**
- **Content excerpts**
- **Location codes**

Example searches:
- `axiom` - Find all axiom-related cards
- `Box Calculus` - Find Box Calculus content
- `δ-geometry` - Find delta-geometry blocks
- `Meta-Time` - Find Meta-Time references

### 2. Filters

**Directory Filter:**
- Filter by source directory (genesis-0, genesis-1, intake, etc.)
- Shows only cards from selected directory

**Type Filter** (if using enhanced cards):
- **Formal** - Axioms, theorems, lemmas
- **Technical** - Contains equations, proofs, symbols
- **Conversational** - ChatGPT dialogue patterns

### 3. Statistics Panel

Overview stats at the top:
- **Total Cards** - Number of catalog entries
- **Directories** - Number of source directories
- **Formal Statements** - Count of axioms/theorems (enhanced only)
- **Technical Blocks** - Count of technical content (enhanced only)

### 4. Card Display

Each card shows:
- **Card ID** (e.g., GEN0-001)
- **Heading** - Section title
- **Location Code** - Full semantic address
- **Excerpt** - Content preview (~200 chars)
- **Tags** - Formal, Technical, Conversational, etc. (enhanced)
- **Concepts** - Extracted key terms (up to 10)
- **Source Link** - Click to view in source file

### 5. Source Viewing

Clicking "View in source" opens the HTML-formatted source file with:
- **Syntax highlighting** for markdown
- **Line numbers** for reference
- **Jump to line** - Automatically scrolls to the card's line range
- **Highlighted line** - Target line is highlighted
- **Dark theme** - Easy-to-read code display

## Analytics Dashboard

Access via: `catalog-html/analytics.html` or click "View Analytics 📊" in the catalog.

### Visualizations

#### 1. Cards by Directory (Bar Chart)
- Shows distribution of cards across directories
- Helps identify which sources have the most content
- Interactive: hover for exact counts

#### 2. Block Types Distribution (Pie Chart)
- Shows proportion of different block types:
  - Paragraphs
  - Lists
  - Tables
  - Code blocks
  - Equations
- Helps understand content structure

#### 3. Content Depth Distribution (Line Chart)
- Shows nesting levels (heading hierarchy depth)
- Depth 0 = root level
- Depth 1 = top-level sections
- Depth 2+ = nested subsections
- Helps assess document complexity

#### 4. Top 15 Sources by Card Count (Horizontal Bar)
- Most segmented files
- Shows which documents have most content
- Useful for prioritizing review

#### 5. Top 30 Concepts (Horizontal Bar)
- Most frequently appearing concepts
- Includes Greek symbols, domain terms, operators
- Shows your library's key themes

### Statistics Cards

Quick overview metrics:
- **Total Cards**
- **Unique Directories**
- **Block Types**
- **Unique Concepts**

## Directory Structure

```
catalog-html/
├── index.html              # Main catalog browser
├── analytics.html          # Analytics dashboard
└── sources/                # HTML-formatted sources
    ├── genesis-0_*.html
    ├── genesis-1_*.html
    ├── ...
    ├── intake_*.html
    └── special_*.html
```

## Features Details

### Syntax Highlighting

Markdown files are converted to HTML with highlighting for:
- **Headings** - Blue/teal
- **Bold text** - Yellow/gold
- **Italic text** - Orange
- **Code** - Red with background
- **Greek letters** - Purple (δ, Φ, Π, Ψ, etc.)
- **Math symbols** - Blue (∀, ∃, ∈, ∫, ∂, etc.)
- **List markers** - Light blue

### Line Anchors

Every line in source files has an anchor: `#L123`

Direct link format:
```
sources/genesis-0_Tri-Unity_Theorem.html#L150
```

Opens file and scrolls to line 150.

### Responsive Design

The HTML catalog is responsive and works on:
- Desktop browsers (optimized)
- Tablets
- Mobile devices (limited)

### Dark Theme

Source viewer uses a dark theme:
- Background: `#1e1e1e`
- Text: `#d4d4d4`
- Highlighted line: `#264f78`
- Syntax colors optimized for readability

## Workflow Examples

### Finding an Axiom

1. Open `index.html`
2. Search for "axiom" or specific ID like "A1"
3. Click card to read excerpt
4. Click "View in source" to see full context
5. Source opens at exact line with full text

### Exploring a Concept

1. Go to `analytics.html`
2. Check "Top 30 Concepts" chart
3. Note interesting concept (e.g., "Meta-Time")
4. Go back to `index.html`
5. Search for "Meta-Time"
6. Browse all cards mentioning it

### Analyzing Content Distribution

1. Open `analytics.html`
2. View "Cards by Directory" chart
3. Identify heavily-documented areas
4. View "Block Types" to understand content structure
5. Check "Content Depth" for complexity

### Filtering by Source

1. Open `index.html`
2. Use Directory filter dropdown
3. Select "genesis-0"
4. See only cards from genesis-0 directory
5. Further refine with search

## Chart Interactivity

All charts in analytics.html support:
- **Hover tooltips** - See exact values
- **Responsive sizing** - Adapts to window
- **Legend toggle** - Click legend items to hide/show data
- **Download** (right-click) - Save as image

## Performance

- **Load time**: ~1-2 seconds for 11,429 cards
- **Search**: Real-time filtering (instant)
- **Charts**: Rendered client-side (fast)
- **Source files**: Load on-demand (only when clicked)

## Browser Compatibility

Tested on:
- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE11 (limited support)

## Tips & Tricks

### Quick Navigation

- Use browser's **Ctrl+F** on catalog page for additional search
- Bookmark `analytics.html` for quick stats
- Open multiple source files in tabs for cross-reference

### Offline Use

The HTML catalog is **fully offline** - no internet required:
- All resources embedded or local
- Chart.js loaded from CDN (requires initial internet for charts)
- To make charts offline: download Chart.js library locally

### Keyboard Shortcuts

Standard browser shortcuts work:
- `Ctrl+F` - Find in page
- `Ctrl+Click` - Open link in new tab
- `Backspace` - Go back
- `F5` - Reload

### Mobile Viewing

On mobile devices:
- Catalog browser works well
- Source viewer may require horizontal scrolling
- Analytics charts are touch-enabled (pinch to zoom)

## Regenerating

To rebuild the HTML catalog:

```bash
# Full rebuild
python generate-html-catalog.py

# Or step-by-step
python -c "from hgg_index.html_generator import generate_html_catalog; generate_html_catalog()"
python -c "from hgg_index.html_charts import generate_analytics_html; generate_analytics_html()"
```

**When to rebuild:**
- After adding new source files
- After updating card catalog
- When switching between basic/enhanced cards

## Customization

### Colors

Edit the `<style>` sections in:
- `hgg_index/html_generator.py` - Catalog styles
- `hgg_index/html_charts.py` - Analytics styles

### Charts

Modify chart configurations in `hgg_index/html_charts.py`:
- Chart types (bar, pie, line, etc.)
- Colors and themes
- Data displayed

### Layout

Adjust grid layouts and responsive breakpoints in CSS.

## Troubleshooting

### Charts not showing
- Check internet connection (Chart.js loads from CDN)
- Or download Chart.js locally and update script src

### Source links broken
- Ensure `sources/` directory exists
- Check that source HTML files were generated
- Verify file:///// protocol is allowed in browser

### Search not working
- Check JavaScript is enabled
- Try clearing browser cache
- Reload page

### Slow loading
- Normal for 11,429 cards
- Consider filtering by directory first
- Use search to narrow results

## Future Enhancements

Possible additions:
- [ ] Export search results to CSV
- [ ] Bookmark/favorite cards
- [ ] Notes and annotations
- [ ] Enhanced card comparison view
- [ ] Network graph of concept relationships
- [ ] Timeline view (for dated content)

## See Also

- `hgg-index-user-guide.md` - CLI catalog usage
- `hgg-index-enhanced-features.md` - Enhanced metrics
- `README.md` - Project overview

---

**Enjoy exploring your semantic knowledge base!** 📚
