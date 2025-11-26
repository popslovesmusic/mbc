"""Generate analytics page with charts and visualizations"""

import json
from pathlib import Path
from typing import List, Dict
from collections import Counter


def generate_analytics_html(catalog_dir: str = "catalog", output_dir: str = "catalog-html") -> str:
    """Generate analytics dashboard with charts

    Args:
        catalog_dir: Catalog directory
        output_dir: Output directory

    Returns:
        Path to generated analytics HTML
    """
    catalog_dir = Path(catalog_dir)
    output_dir = Path(output_dir)

    # Load cards
    cards_file = catalog_dir / "indexes" / "cards.jsonl"
    if not cards_file.exists():
        raise FileNotFoundError(f"Cards file not found: {cards_file}")

    cards = []
    with open(cards_file, 'r', encoding='utf-8') as f:
        for line in f:
            card = json.loads(line)
            cards.append(card)

    print(f"Loaded {len(cards)} cards for analytics")

    # Collect statistics
    stats = collect_statistics(cards)

    # Generate HTML
    html = create_analytics_html(stats, len(cards))

    # Save
    output_file = output_dir / "analytics.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Analytics page saved to {output_file}")
    return str(output_file)


def collect_statistics(cards: List[Dict]) -> Dict:
    """Collect statistics from cards"""

    stats = {}

    # By directory
    by_directory = Counter()
    for card in cards:
        source = card['source']
        directory = source.split('\\')[0] if '\\' in source else source.split('/')[0]
        by_directory[directory] += 1

    stats['by_directory'] = dict(sorted(by_directory.items()))

    # By block type
    by_type = Counter(card.get('block_type', 'unknown') for card in cards)
    stats['by_type'] = dict(sorted(by_type.items()))

    # Top concepts
    all_concepts = []
    for card in cards:
        all_concepts.extend(card.get('concepts', []))
    concept_freq = Counter(all_concepts)
    stats['top_concepts'] = dict(concept_freq.most_common(30))

    # Top sources
    source_counts = Counter(card['source'] for card in cards)
    stats['top_sources'] = dict(source_counts.most_common(15))

    # Cards per heading level (approximate by location depth)
    location_depths = []
    for card in cards:
        location = card.get('location', '')
        depth = location.count('::')
        location_depths.append(depth)
    depth_counts = Counter(location_depths)
    stats['by_depth'] = dict(sorted(depth_counts.items()))

    return stats


def create_analytics_html(stats: Dict, total_cards: int) -> str:
    """Create analytics HTML with Chart.js visualizations"""

    # Prepare data for charts
    dir_labels = list(stats['by_directory'].keys())
    dir_values = list(stats['by_directory'].values())

    type_labels = list(stats['by_type'].keys())
    type_values = list(stats['by_type'].values())

    concept_labels = list(stats['top_concepts'].keys())
    concept_values = list(stats['top_concepts'].values())

    source_labels = [Path(s).name for s in stats['top_sources'].keys()]
    source_values = list(stats['top_sources'].values())

    depth_labels = [f"Depth {d}" for d in stats['by_depth'].keys()]
    depth_values = list(stats['by_depth'].values())

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HGG Catalog Analytics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
        .nav {{
            background: white;
            padding: 10px 20px;
            border-bottom: 1px solid #ddd;
        }}
        .nav a {{
            color: #3498db;
            text-decoration: none;
            margin-right: 20px;
            font-weight: 500;
        }}
        .nav a:hover {{
            text-decoration: underline;
        }}
        .content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .stats-overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card .value {{
            font-size: 36px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 8px;
        }}
        .stat-card .label {{
            font-size: 14px;
            color: #666;
        }}
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chart-container h2 {{
            margin: 0 0 20px 0;
            font-size: 18px;
            color: #2c3e50;
        }}
        .chart-container.full-width {{
            grid-column: 1 / -1;
        }}
        canvas {{
            max-height: 400px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 HGG Catalog Analytics</h1>
        <div class="subtitle">Visual analysis of {total_cards} catalog entries</div>
    </div>

    <div class="nav">
        <a href="index.html">← Back to Catalog</a>
        <a href="#overview">Overview</a>
        <a href="#distribution">Distribution</a>
        <a href="#concepts">Concepts</a>
    </div>

    <div class="content">
        <div id="overview" class="stats-overview">
            <div class="stat-card">
                <div class="value">{total_cards}</div>
                <div class="label">Total Cards</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(stats['by_directory'])}</div>
                <div class="label">Directories</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(stats['by_type'])}</div>
                <div class="label">Block Types</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(stats['top_concepts'])}</div>
                <div class="label">Unique Concepts</div>
            </div>
        </div>

        <div id="distribution" class="chart-grid">
            <div class="chart-container">
                <h2>Cards by Directory</h2>
                <canvas id="directoryChart"></canvas>
            </div>

            <div class="chart-container">
                <h2>Block Types Distribution</h2>
                <canvas id="typeChart"></canvas>
            </div>

            <div class="chart-container">
                <h2>Content Depth Distribution</h2>
                <canvas id="depthChart"></canvas>
            </div>

            <div class="chart-container">
                <h2>Top 15 Sources by Card Count</h2>
                <canvas id="sourcesChart"></canvas>
            </div>
        </div>

        <div id="concepts" class="chart-grid">
            <div class="chart-container full-width">
                <h2>Top 30 Concepts</h2>
                <canvas id="conceptsChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Common chart options
        const chartOptions = {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{
                    display: true,
                    position: 'top'
                }}
            }}
        }};

        // Directory chart (bar)
        new Chart(document.getElementById('directoryChart'), {{
            type: 'bar',
            data: {{
                labels: {dir_labels},
                datasets: [{{
                    label: 'Cards',
                    data: {dir_values},
                    backgroundColor: 'rgba(52, 152, 219, 0.8)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                ...chartOptions,
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});

        // Block type chart (pie)
        new Chart(document.getElementById('typeChart'), {{
            type: 'pie',
            data: {{
                labels: {type_labels},
                datasets: [{{
                    data: {type_values},
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(46, 204, 113, 0.8)',
                        'rgba(155, 89, 182, 0.8)',
                        'rgba(241, 196, 15, 0.8)',
                        'rgba(231, 76, 60, 0.8)',
                        'rgba(26, 188, 156, 0.8)'
                    ]
                }}]
            }},
            options: chartOptions
        }});

        // Depth chart (line)
        new Chart(document.getElementById('depthChart'), {{
            type: 'line',
            data: {{
                labels: {depth_labels},
                datasets: [{{
                    label: 'Cards at Depth',
                    data: {depth_values},
                    backgroundColor: 'rgba(155, 89, 182, 0.2)',
                    borderColor: 'rgba(155, 89, 182, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                ...chartOptions,
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});

        // Sources chart (horizontal bar)
        new Chart(document.getElementById('sourcesChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(source_labels)},
                datasets: [{{
                    label: 'Cards per Source',
                    data: {source_values},
                    backgroundColor: 'rgba(46, 204, 113, 0.8)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                ...chartOptions,
                indexAxis: 'y',
                scales: {{
                    x: {{ beginAtZero: true }}
                }}
            }}
        }});

        // Concepts chart (horizontal bar)
        new Chart(document.getElementById('conceptsChart'), {{
            type: 'bar',
            data: {{
                labels: {concept_labels},
                datasets: [{{
                    label: 'Frequency',
                    data: {concept_values},
                    backgroundColor: 'rgba(230, 126, 34, 0.8)',
                    borderColor: 'rgba(230, 126, 34, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                ...chartOptions,
                indexAxis: 'y',
                scales: {{
                    x: {{ beginAtZero: true }}
                }}
            }}
        }});
    </script>
</body>
</html>'''

    return html


if __name__ == "__main__":
    output_file = generate_analytics_html()
    print(f"\n✓ Analytics page generated!")
    print(f"Open in browser: file:///{output_file}")
