"""Generate PDF-ready HTML report with all metrics and visualizations"""

import json
from pathlib import Path
from typing import Dict
from hgg_index.metrics_export import MetricsExporter


def generate_pdf_report(output_file: str = "reports/catalog-report.html") -> str:
    """Generate comprehensive PDF-ready HTML report

    Args:
        output_file: Output HTML file path

    Returns:
        Path to generated HTML file
    """
    # Load metrics
    exporter = MetricsExporter()
    cards = exporter.load_enhanced_cards()
    metrics = exporter.collect_metrics(cards)

    # Generate HTML
    html = create_pdf_html(metrics)

    # Save
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"PDF-ready report saved to {output_path}")
    print(f"\nTo generate PDF:")
    print(f"  1. Open in browser: file:///{output_path.absolute()}")
    print(f"  2. Print -> Save as PDF")
    print(f"  3. Or use: wkhtmltopdf {output_path} output.pdf")

    return str(output_path)


def create_pdf_html(metrics: Dict) -> str:
    """Create PDF-ready HTML with all visualizations"""

    # Prepare chart data
    concept_labels = list(metrics['concepts']['top_50'].keys())[:30]
    concept_values = list(metrics['concepts']['top_50'].values())[:30]

    formal_labels = [k for k in metrics['formal_statements']['by_type'].keys() if k]
    formal_values = [metrics['formal_statements']['by_type'][k] for k in formal_labels]

    dir_labels = list(metrics['by_directory'].keys())
    dir_totals = [metrics['by_directory'][d]['total'] for d in dir_labels]
    dir_formal = [metrics['by_directory'][d]['formal'] for d in dir_labels]
    dir_contradictions = [metrics['by_directory'][d]['contradictions'] for d in dir_labels]

    tags_labels = [t for t, _ in metrics['tags'].most_common(20)]
    tags_values = [c for _, c in metrics['tags'].most_common(20)]

    alias_prefix_labels = list(metrics['aliases']['by_prefix'].keys())
    alias_prefix_values = list(metrics['aliases']['by_prefix'].values())

    # Pre-calculate percentages to avoid f-string formatting issues
    technical_pct = f"{metrics['technical_blocks']/metrics['total_cards']*100:.1f}"
    avg_concepts = f"{metrics['concepts']['avg_per_card']:.1f}"
    avg_concepts_precise = f"{metrics['concepts']['avg_per_card']:.2f}"

    # Formal statement percentages
    formal_total = metrics['formal_statements']['total']
    formal_pcts = {}
    for stmt_type, count in metrics['formal_statements']['by_type'].items():
        if stmt_type:
            formal_pcts[stmt_type] = f"{count/formal_total*100:.1f}" if formal_total > 0 else "0.0"

    # Contradiction severity percentages
    contr_total = metrics['contradictions']['total']
    contr_low_pct = f"{metrics['contradictions']['by_severity']['low']/contr_total*100:.1f}" if contr_total > 0 else "0.0"
    contr_med_pct = f"{metrics['contradictions']['by_severity']['medium']/contr_total*100:.1f}" if contr_total > 0 else "0.0"
    contr_high_pct = f"{metrics['contradictions']['by_severity']['high']/contr_total*100:.1f}" if contr_total > 0 else "0.0"

    # Ambiguity severity percentages
    ambig_total = metrics['ambiguity']['total']
    ambig_low_pct = f"{metrics['ambiguity']['by_severity']['low']/ambig_total*100:.1f}" if ambig_total > 0 else "0.0"
    ambig_med_pct = f"{metrics['ambiguity']['by_severity']['medium']/ambig_total*100:.1f}" if ambig_total > 0 else "0.0"
    ambig_high_pct = f"{metrics['ambiguity']['by_severity']['high']/ambig_total*100:.1f}" if ambig_total > 0 else "0.0"

    # Concept frequency percentages
    concept_total = metrics['concepts']['total_mentions']
    concept_pcts = {}
    for concept, count in metrics['concepts']['top_50'].items():
        concept_pcts[concept] = f"{count/concept_total*100:.2f}" if concept_total > 0 else "0.00"

    # Prefix meanings helper
    prefix_meanings = {
        'Am': 'Axiom', 'Th': 'Theorem', 'Lm': 'Lemma', 'Cr': 'Corollary',
        'Pr': 'Proposition', 'Df': 'Definition', 'Cn': 'Concept', 'Bk': 'Block'
    }

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HGG Catalog Comprehensive Metrics Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        @media print {{
            .no-print {{ display: none; }}
            .page-break {{ page-break-before: always; }}
            body {{ margin: 0; padding: 20px; }}
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fff;
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .cover-page {{
            text-align: center;
            padding: 100px 0;
            border-bottom: 3px solid #2c3e50;
        }}

        .cover-page h1 {{
            font-size: 42px;
            color: #2c3e50;
            margin-bottom: 20px;
        }}

        .cover-page .subtitle {{
            font-size: 20px;
            color: #666;
            margin-bottom: 40px;
        }}

        .cover-page .stats-summary {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            max-width: 800px;
            margin: 40px auto;
        }}

        .stat-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}

        .stat-box .value {{
            font-size: 36px;
            font-weight: bold;
            color: #3498db;
        }}

        .stat-box .label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}

        .section {{
            margin: 40px 0;
        }}

        h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin: 30px 0 20px 0;
            font-size: 28px;
        }}

        h3 {{
            color: #34495e;
            margin: 20px 0 15px 0;
            font-size: 20px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .chart-container {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
        }}

        .chart-container h3 {{
            margin-top: 0;
        }}

        canvas {{
            max-height: 400px !important;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}

        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}

        .metric-card h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .metric-card .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin: 5px 0;
        }}

        .metric-card .metric-label {{
            font-size: 12px;
            color: #666;
        }}

        .severity-indicator {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}

        .severity-low {{ background: #d4edda; color: #155724; }}
        .severity-medium {{ background: #fff3cd; color: #856404; }}
        .severity-high {{ background: #f8d7da; color: #721c24; }}

        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
            margin-top: 40px;
        }}

        @media print {{
            body {{ padding: 20px; }}
            .chart-container {{ page-break-inside: avoid; }}
            canvas {{ max-height: 300px !important; }}
        }}
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page">
        <h1>HGG Catalog</h1>
        <div class="subtitle">Comprehensive Metrics Report</div>

        <div class="stats-summary">
            <div class="stat-box">
                <div class="value">{metrics['total_cards']:,}</div>
                <div class="label">Total Blocks</div>
            </div>
            <div class="stat-box">
                <div class="value">{metrics['concepts']['unique_count']:,}</div>
                <div class="label">Unique Concepts</div>
            </div>
            <div class="stat-box">
                <div class="value">{metrics['formal_statements']['total']}</div>
                <div class="label">Formal Statements</div>
            </div>
        </div>

        <p style="margin-top: 40px; color: #666;">
            Generated from 81 markdown files<br>
            Meta-Genesis Physics Theory Knowledge Base
        </p>
    </div>

    <div class="page-break"></div>

    <!-- Executive Summary -->
    <div class="section">
        <h2>Executive Summary</h2>

        <div class="metric-grid">
            <div class="metric-card">
                <h4>Content Overview</h4>
                <div class="metric-value">{metrics['total_cards']:,}</div>
                <div class="metric-label">Semantic Blocks</div>
                <div class="metric-value">{metrics['technical_blocks']:,}</div>
                <div class="metric-label">Technical Blocks ({technical_pct}%)</div>
            </div>

            <div class="metric-card">
                <h4>Formal Mathematics</h4>
                <div class="metric-value">{metrics['formal_statements']['total']}</div>
                <div class="metric-label">Axioms & Theorems</div>
                <div class="metric-value">{metrics['definitive_statements']:,}</div>
                <div class="metric-label">Definitive Statements</div>
            </div>

            <div class="metric-card">
                <h4>Quality Indicators</h4>
                <div class="metric-value">{metrics['contradictions']['total']:,}</div>
                <div class="metric-label">Blocks with Contradictions</div>
                <div class="metric-value">{metrics['ambiguity']['total']:,}</div>
                <div class="metric-label">Blocks with Ambiguity</div>
            </div>

            <div class="metric-card">
                <h4>Semantic Richness</h4>
                <div class="metric-value">{avg_concepts}</div>
                <div class="metric-label">Avg Concepts per Block</div>
                <div class="metric-value">{metrics['concepts']['total_mentions']:,}</div>
                <div class="metric-label">Total Concept Mentions</div>
            </div>
        </div>
    </div>

    <!-- Formal Statements -->
    <div class="section">
        <h2>Formal Statements Analysis</h2>

        <h3>Distribution by Type</h3>
        <table>
            <thead>
                <tr>
                    <th>Statement Type</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f"""
                <tr>
                    <td style="text-transform: capitalize;">{stmt_type}</td>
                    <td>{count}</td>
                    <td>{formal_pcts[stmt_type]}%</td>
                </tr>
                """ for stmt_type, count in sorted(metrics['formal_statements']['by_type'].items(), key=lambda x: -x[1]) if stmt_type)}
            </tbody>
        </table>

        <div class="chart-container">
            <h3>Formal Statements by Type</h3>
            <canvas id="formalChart"></canvas>
        </div>
    </div>

    <div class="page-break"></div>

    <!-- Quality Metrics -->
    <div class="section">
        <h2>Quality & Consistency Metrics</h2>

        <h3>Contradictions</h3>
        <table>
            <thead>
                <tr>
                    <th>Severity Level</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><span class="severity-indicator severity-low">Low (< 0.3)</span></td>
                    <td>{metrics['contradictions']['by_severity']['low']}</td>
                    <td>{contr_low_pct}%</td>
                </tr>
                <tr>
                    <td><span class="severity-indicator severity-medium">Medium (0.3-0.7)</span></td>
                    <td>{metrics['contradictions']['by_severity']['medium']}</td>
                    <td>{contr_med_pct}%</td>
                </tr>
                <tr>
                    <td><span class="severity-indicator severity-high">High (> 0.7)</span></td>
                    <td>{metrics['contradictions']['by_severity']['high']}</td>
                    <td>{contr_high_pct}%</td>
                </tr>
            </tbody>
        </table>

        <h3>Ambiguity</h3>
        <table>
            <thead>
                <tr>
                    <th>Severity Level</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><span class="severity-indicator severity-low">Low (< 0.3)</span></td>
                    <td>{metrics['ambiguity']['by_severity']['low']}</td>
                    <td>{ambig_low_pct}%</td>
                </tr>
                <tr>
                    <td><span class="severity-indicator severity-medium">Medium (0.3-0.7)</span></td>
                    <td>{metrics['ambiguity']['by_severity']['medium']}</td>
                    <td>{ambig_med_pct}%</td>
                </tr>
                <tr>
                    <td><span class="severity-indicator severity-high">High (> 0.7)</span></td>
                    <td>{metrics['ambiguity']['by_severity']['high']}</td>
                    <td>{ambig_high_pct}%</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="page-break"></div>

    <!-- Concepts Analysis -->
    <div class="section">
        <h2>Concept Analysis</h2>

        <p><strong>Total Unique Concepts</strong>: {metrics['concepts']['unique_count']:,}<br>
        <strong>Total Mentions</strong>: {metrics['concepts']['total_mentions']:,}<br>
        <strong>Average per Block</strong>: {avg_concepts_precise}</p>

        <div class="chart-container">
            <h3>Top 30 Most Frequent Concepts</h3>
            <canvas id="conceptsChart"></canvas>
        </div>

        <h3>Top 50 Concepts</h3>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Concept</th>
                    <th>Frequency</th>
                    <th>% of Total</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f"""
                <tr>
                    <td>{i}</td>
                    <td>{concept}</td>
                    <td>{count}</td>
                    <td>{concept_pcts[concept]}%</td>
                </tr>
                """ for i, (concept, count) in enumerate(list(metrics['concepts']['top_50'].items())[:50], 1))}
            </tbody>
        </table>
    </div>

    <div class="page-break"></div>

    <!-- Aliases & Tags -->
    <div class="section">
        <h2>Aliases & Classification</h2>

        <h3>Alias Statistics</h3>
        <p><strong>Total Aliases</strong>: {metrics['aliases']['total_aliases']:,}<br>
        <strong>Unique Aliases</strong>: {metrics['aliases']['unique_aliases']:,}</p>

        <div class="chart-container">
            <h3>Aliases by Prefix</h3>
            <canvas id="aliasChart"></canvas>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Prefix</th>
                    <th>Meaning</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f"""
                <tr>
                    <td style="font-family: monospace;">{prefix}</td>
                    <td>{prefix_meanings.get(prefix, 'Unknown')}</td>
                    <td>{count}</td>
                </tr>
                """ for prefix, count in sorted(metrics['aliases']['by_prefix'].items(), key=lambda x: -x[1]))}
            </tbody>
        </table>

        <div class="chart-container">
            <h3>Top 20 Tags</h3>
            <canvas id="tagsChart"></canvas>
        </div>
    </div>

    <div class="page-break"></div>

    <!-- Directory Analysis -->
    <div class="section">
        <h2>Content Distribution by Directory</h2>

        <div class="chart-container">
            <h3>Total Blocks by Directory</h3>
            <canvas id="directoryChart"></canvas>
        </div>

        <div class="chart-container">
            <h3>Formal Statements by Directory</h3>
            <canvas id="directoryFormalChart"></canvas>
        </div>

        <h3>Detailed Directory Breakdown</h3>
        <table>
            <thead>
                <tr>
                    <th>Directory</th>
                    <th>Total</th>
                    <th>Formal</th>
                    <th>Technical</th>
                    <th>Contradictions</th>
                    <th>Definitive</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f"""
                <tr>
                    <td><strong>{directory}</strong></td>
                    <td>{stats['total']}</td>
                    <td>{stats['formal']}</td>
                    <td>{stats['technical']}</td>
                    <td>{stats['contradictions']}</td>
                    <td>{stats['definitive']}</td>
                </tr>
                """ for directory, stats in sorted(metrics['by_directory'].items()))}
            </tbody>
        </table>
    </div>

    <!-- Footer -->
    <div class="footer">
        <p>HGG Catalog Comprehensive Metrics Report</p>
        <p>Generated from {metrics['total_cards']:,} enhanced catalog cards</p>
        <p>Meta-Genesis Physics Theory Knowledge Base</p>
    </div>

    <script>
        // Chart.js visualizations
        const chartOptions = {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{ display: true, position: 'top' }}
            }}
        }};

        // Formal statements
        new Chart(document.getElementById('formalChart'), {{
            type: 'pie',
            data: {{
                labels: {json.dumps(formal_labels)},
                datasets: [{{
                    data: {json.dumps(formal_values)},
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(46, 204, 113, 0.8)',
                        'rgba(155, 89, 182, 0.8)',
                        'rgba(241, 196, 15, 0.8)',
                        'rgba(231, 76, 60, 0.8)'
                    ]
                }}]
            }},
            options: chartOptions
        }});

        // Top concepts
        new Chart(document.getElementById('conceptsChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(concept_labels)},
                datasets: [{{
                    label: 'Frequency',
                    data: {json.dumps(concept_values)},
                    backgroundColor: 'rgba(230, 126, 34, 0.8)',
                    borderColor: 'rgba(230, 126, 34, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                ...chartOptions,
                indexAxis: 'y',
                scales: {{ x: {{ beginAtZero: true }} }}
            }}
        }});

        // Aliases by prefix
        new Chart(document.getElementById('aliasChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(alias_prefix_labels)},
                datasets: [{{
                    label: 'Count',
                    data: {json.dumps(alias_prefix_values)},
                    backgroundColor: 'rgba(52, 152, 219, 0.8)'
                }}]
            }},
            options: {{
                ...chartOptions,
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});

        // Tags
        new Chart(document.getElementById('tagsChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(tags_labels)},
                datasets: [{{
                    label: 'Count',
                    data: {json.dumps(tags_values)},
                    backgroundColor: 'rgba(155, 89, 182, 0.8)'
                }}]
            }},
            options: {{
                ...chartOptions,
                indexAxis: 'y',
                scales: {{ x: {{ beginAtZero: true }} }}
            }}
        }});

        // Directory total
        new Chart(document.getElementById('directoryChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(dir_labels)},
                datasets: [{{
                    label: 'Total Blocks',
                    data: {json.dumps(dir_totals)},
                    backgroundColor: 'rgba(52, 152, 219, 0.8)'
                }}]
            }},
            options: {{
                ...chartOptions,
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});

        // Directory formal
        new Chart(document.getElementById('directoryFormalChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(dir_labels)},
                datasets: [{{
                    label: 'Formal Statements',
                    data: {json.dumps(dir_formal)},
                    backgroundColor: 'rgba(46, 204, 113, 0.8)'
                }}, {{
                    label: 'Contradictions',
                    data: {json.dumps(dir_contradictions)},
                    backgroundColor: 'rgba(231, 76, 60, 0.8)'
                }}]
            }},
            options: {{
                ...chartOptions,
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});
    </script>
</body>
</html>'''

    return html


if __name__ == "__main__":
    generate_pdf_report()
