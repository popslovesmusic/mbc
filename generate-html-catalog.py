"""Generate complete HTML catalog with analytics"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from hgg_index.html_generator import generate_html_catalog
from hgg_index.html_charts import generate_analytics_html


def main():
    """Generate complete HTML catalog"""
    print("="*60)
    print("HGG Catalog HTML Generator")
    print("="*60)

    # Generate main catalog
    print("\n[1/2] Generating catalog browser...")
    catalog_file = generate_html_catalog(enhanced=False)
    print(f"[OK] Catalog saved to: {catalog_file}")

    # Generate analytics
    print("\n[2/2] Generating analytics dashboard...")
    analytics_file = generate_analytics_html()
    print(f"[OK] Analytics saved to: {analytics_file}")

    print("\n" + "="*60)
    print("[OK] HTML catalog generation complete!")
    print("="*60)
    print(f"\nOpen in your browser:")
    print(f"  Catalog:   file:///{Path(catalog_file).absolute()}")
    print(f"  Analytics: file:///{Path(analytics_file).absolute()}")
    print()


if __name__ == "__main__":
    main()
