"""Export metrics in various formats for analysis and reporting"""

import json
import csv
from pathlib import Path
from typing import List, Dict
from collections import Counter


class MetricsExporter:
    """Export catalog metrics to various formats"""

    def __init__(self, catalog_dir: str = "catalog"):
        self.catalog_dir = Path(catalog_dir)
        self.enhanced_cards_file = self.catalog_dir / "indexes" / "cards-enhanced.jsonl"

    def load_enhanced_cards(self) -> List[Dict]:
        """Load all enhanced cards"""
        if not self.enhanced_cards_file.exists():
            raise FileNotFoundError(
                f"Enhanced cards not found at {self.enhanced_cards_file}. "
                "Run: python -c 'from hgg_index.card_enhanced import generate_enhanced_cards; "
                "from hgg_index.segment import Segment; import json; "
                "segments = [Segment(**json.loads(line)) for line in open(\"catalog/indexes/segments.jsonl\")]; "
                "generate_enhanced_cards(segments)'"
            )

        cards = []
        with open(self.enhanced_cards_file, 'r', encoding='utf-8') as f:
            for line in f:
                card = json.loads(line)
                cards.append(card)

        return cards

    def collect_metrics(self, cards: List[Dict]) -> Dict:
        """Collect comprehensive metrics from enhanced cards"""

        metrics = {
            'total_cards': len(cards),
            'formal_statements': {
                'total': sum(1 for c in cards if c.get('is_formal')),
                'by_type': Counter(c.get('statement_type') for c in cards if c.get('statement_type'))
            },
            'axiom_count': sum(c.get('axiom_count', 0) for c in cards),
            'theorem_count': sum(c.get('theorem_count', 0) for c in cards),
            'technical_blocks': sum(1 for c in cards if c.get('is_technical')),
            'conversational_blocks': sum(1 for c in cards if c.get('conversational_score', 0) > 0.5),
            'contradictions': {
                'total': sum(1 for c in cards if c.get('has_contradictions')),
                'by_severity': self._group_by_severity(cards, 'has_contradictions')
            },
            'ambiguity': {
                'total': sum(1 for c in cards if c.get('has_ambiguity')),
                'by_severity': self._group_by_severity(cards, 'has_ambiguity')
            },
            'definitive_statements': sum(1 for c in cards if c.get('is_definitive')),
            'concepts': self._concept_stats(cards),
            'aliases': self._alias_stats(cards),
            'tags': Counter(tag for c in cards for tag in c.get('tags', [])),
            'by_directory': self._directory_stats(cards),
            'quality_scores': self._quality_scores(cards)
        }

        return metrics

    def _group_by_severity(self, cards: List[Dict], flag_field: str) -> Dict:
        """Group cards by severity level"""
        groups = {
            'low': 0,      # 0.0-0.3
            'medium': 0,   # 0.3-0.7
            'high': 0      # 0.7-1.0
        }

        for card in cards:
            if not card.get(flag_field):
                continue

            severity = card.get('max_severity', 0)
            if severity < 0.3:
                groups['low'] += 1
            elif severity < 0.7:
                groups['medium'] += 1
            else:
                groups['high'] += 1

        return groups

    def _concept_stats(self, cards: List[Dict]) -> Dict:
        """Collect concept statistics"""
        all_concepts = []
        for card in cards:
            all_concepts.extend(card.get('concepts', []))

        concept_freq = Counter(all_concepts)

        return {
            'unique_count': len(concept_freq),
            'total_mentions': len(all_concepts),
            'top_50': dict(concept_freq.most_common(50)),
            'avg_per_card': len(all_concepts) / len(cards) if cards else 0
        }

    def _alias_stats(self, cards: List[Dict]) -> Dict:
        """Collect alias statistics"""
        all_aliases = []
        for card in cards:
            all_aliases.extend(card.get('aliases', []))

        alias_freq = Counter(all_aliases)

        # Count by prefix (Am, Th, Cn, etc.)
        by_prefix = Counter()
        for alias in all_aliases:
            if len(alias) >= 2:
                prefix = alias[:2]
                by_prefix[prefix] += 1

        return {
            'total_aliases': len(all_aliases),
            'unique_aliases': len(alias_freq),
            'by_prefix': dict(by_prefix),
            'top_20': dict(alias_freq.most_common(20))
        }

    def _directory_stats(self, cards: List[Dict]) -> Dict:
        """Stats by directory"""
        by_dir = {}

        for card in cards:
            source = card['source']
            directory = source.split('\\')[0] if '\\' in source else source.split('/')[0]

            if directory not in by_dir:
                by_dir[directory] = {
                    'total': 0,
                    'formal': 0,
                    'technical': 0,
                    'contradictions': 0,
                    'definitive': 0
                }

            by_dir[directory]['total'] += 1
            if card.get('is_formal'):
                by_dir[directory]['formal'] += 1
            if card.get('is_technical'):
                by_dir[directory]['technical'] += 1
            if card.get('has_contradictions'):
                by_dir[directory]['contradictions'] += 1
            if card.get('is_definitive'):
                by_dir[directory]['definitive'] += 1

        return by_dir

    def _quality_scores(self, cards: List[Dict]) -> Dict:
        """Calculate quality score distributions"""
        conv_scores = [c.get('conversational_score', 0) for c in cards]
        severity_scores = [c.get('max_severity', 0) for c in cards]
        density_scores = [c.get('concept_density', 0) for c in cards]

        return {
            'conversational': {
                'avg': sum(conv_scores) / len(conv_scores) if conv_scores else 0,
                'min': min(conv_scores) if conv_scores else 0,
                'max': max(conv_scores) if conv_scores else 0
            },
            'severity': {
                'avg': sum(severity_scores) / len(severity_scores) if severity_scores else 0,
                'min': min(severity_scores) if severity_scores else 0,
                'max': max(severity_scores) if severity_scores else 0
            },
            'concept_density': {
                'avg': sum(density_scores) / len(density_scores) if density_scores else 0,
                'min': min(density_scores) if density_scores else 0,
                'max': max(density_scores) if density_scores else 0
            }
        }

    def export_json(self, output_file: str = "metrics-report.json"):
        """Export metrics as JSON"""
        cards = self.load_enhanced_cards()
        metrics = self.collect_metrics(cards)

        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        print(f"Metrics exported to {output_path}")
        return str(output_path)

    def export_csv(self, output_file: str = "metrics-cards.csv"):
        """Export card-level metrics as CSV"""
        cards = self.load_enhanced_cards()

        output_path = Path(output_file)
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'ID', 'Location', 'Heading', 'Is_Formal', 'Statement_Type',
                'Axiom_Count', 'Theorem_Count', 'Is_Technical',
                'Conversational_Score', 'Has_Contradictions', 'Has_Ambiguity',
                'Is_Definitive', 'Max_Severity', 'Concept_Density',
                'Concepts', 'Aliases', 'Tags'
            ])

            # Rows
            for card in cards:
                writer.writerow([
                    card.get('id'),
                    card.get('location'),
                    card.get('heading'),
                    card.get('is_formal'),
                    card.get('statement_type') or '',
                    card.get('axiom_count', 0),
                    card.get('theorem_count', 0),
                    card.get('is_technical'),
                    round(card.get('conversational_score', 0), 2),
                    card.get('has_contradictions'),
                    card.get('has_ambiguity'),
                    card.get('is_definitive'),
                    round(card.get('max_severity', 0), 2),
                    round(card.get('concept_density', 0), 2),
                    ', '.join(card.get('concepts', [])[:5]),
                    ', '.join(card.get('aliases', [])),
                    ', '.join(card.get('tags', []))
                ])

        print(f"Card metrics exported to {output_path}")
        return str(output_path)

    def export_markdown(self, output_file: str = "metrics-report.md"):
        """Export metrics as Markdown report"""
        cards = self.load_enhanced_cards()
        metrics = self.collect_metrics(cards)

        md = self._create_markdown_report(metrics)

        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)

        print(f"Markdown report exported to {output_path}")
        return str(output_path)

    def _create_markdown_report(self, metrics: Dict) -> str:
        """Create Markdown formatted report"""

        md = f"""# HGG Catalog Metrics Report

## Overview

- **Total Cards**: {metrics['total_cards']:,}
- **Formal Statements**: {metrics['formal_statements']['total']:,}
- **Axioms**: {metrics['axiom_count']}
- **Theorems**: {metrics['theorem_count']}
- **Technical Blocks**: {metrics['technical_blocks']:,}
- **Definitive Statements**: {metrics['definitive_statements']:,}

## Formal Statements

### By Type

| Type | Count |
|------|-------|
"""
        for stmt_type, count in sorted(metrics['formal_statements']['by_type'].items(), key=lambda x: -x[1]):
            if stmt_type:
                md += f"| {stmt_type} | {count} |\n"

        md += f"""
## Quality Metrics

### Contradictions

- **Total Blocks with Contradictions**: {metrics['contradictions']['total']:,}
- **Low Severity** (< 0.3): {metrics['contradictions']['by_severity']['low']}
- **Medium Severity** (0.3-0.7): {metrics['contradictions']['by_severity']['medium']}
- **High Severity** (> 0.7): {metrics['contradictions']['by_severity']['high']}

### Ambiguity

- **Total Blocks with Ambiguity**: {metrics['ambiguity']['total']:,}
- **Low Severity** (< 0.3): {metrics['ambiguity']['by_severity']['low']}
- **Medium Severity** (0.3-0.7): {metrics['ambiguity']['by_severity']['medium']}
- **High Severity** (> 0.7): {metrics['ambiguity']['by_severity']['high']}

### Conversational Content

- **Conversational Blocks** (score > 0.5): {metrics['conversational_blocks']:,}
- **Average Conversational Score**: {metrics['quality_scores']['conversational']['avg']:.3f}

### Concept Density

- **Average Concepts per Block**: {metrics['concepts']['avg_per_card']:.2f}
- **Average Density**: {metrics['quality_scores']['concept_density']['avg']:.2f}%

## Concepts

- **Unique Concepts**: {metrics['concepts']['unique_count']:,}
- **Total Concept Mentions**: {metrics['concepts']['total_mentions']:,}

### Top 30 Concepts

| Rank | Concept | Frequency |
|------|---------|-----------|
"""
        for i, (concept, count) in enumerate(list(metrics['concepts']['top_50'].items())[:30], 1):
            md += f"| {i} | {concept} | {count} |\n"

        md += f"""
## Aliases

- **Total Aliases**: {metrics['aliases']['total_aliases']:,}
- **Unique Aliases**: {metrics['aliases']['unique_aliases']:,}

### By Prefix

| Prefix | Count | Meaning |
|--------|-------|---------|
"""
        prefix_meanings = {
            'Am': 'Axiom',
            'Th': 'Theorem',
            'Lm': 'Lemma',
            'Cr': 'Corollary',
            'Pr': 'Proposition',
            'Df': 'Definition',
            'Cn': 'Concept',
            'Bk': 'Block'
        }

        for prefix, count in sorted(metrics['aliases']['by_prefix'].items(), key=lambda x: -x[1]):
            meaning = prefix_meanings.get(prefix, 'Unknown')
            md += f"| {prefix} | {count} | {meaning} |\n"

        md += f"""
## Tags

### Top 20 Tags

| Tag | Count |
|-----|-------|
"""
        for tag, count in metrics['tags'].most_common(20):
            md += f"| {tag} | {count} |\n"

        md += f"""
## By Directory

| Directory | Total | Formal | Technical | Contradictions | Definitive |
|-----------|-------|--------|-----------|----------------|------------|
"""
        for directory in sorted(metrics['by_directory'].keys()):
            stats = metrics['by_directory'][directory]
            md += f"| {directory} | {stats['total']} | {stats['formal']} | {stats['technical']} | {stats['contradictions']} | {stats['definitive']} |\n"

        md += f"""
## Score Distributions

### Conversational Scores
- **Average**: {metrics['quality_scores']['conversational']['avg']:.3f}
- **Range**: {metrics['quality_scores']['conversational']['min']:.2f} - {metrics['quality_scores']['conversational']['max']:.2f}

### Severity Scores
- **Average**: {metrics['quality_scores']['severity']['avg']:.3f}
- **Range**: {metrics['quality_scores']['severity']['min']:.2f} - {metrics['quality_scores']['severity']['max']:.2f}

### Concept Density
- **Average**: {metrics['quality_scores']['concept_density']['avg']:.2f}%
- **Range**: {metrics['quality_scores']['concept_density']['min']:.2f}% - {metrics['quality_scores']['concept_density']['max']:.2f}%

---

*Report generated from {metrics['total_cards']:,} enhanced catalog cards*
"""

        return md


def export_all_formats(output_dir: str = "reports"):
    """Export metrics in all formats"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    exporter = MetricsExporter()

    print("\nExporting metrics in all formats...")

    json_file = exporter.export_json(str(output_path / "metrics-report.json"))
    csv_file = exporter.export_csv(str(output_path / "metrics-cards.csv"))
    md_file = exporter.export_markdown(str(output_path / "metrics-report.md"))

    print(f"\n[OK] All metrics exported to {output_path}/")
    print(f"  - {json_file}")
    print(f"  - {csv_file}")
    print(f"  - {md_file}")

    return {
        'json': json_file,
        'csv': csv_file,
        'markdown': md_file
    }


if __name__ == "__main__":
    export_all_formats()
