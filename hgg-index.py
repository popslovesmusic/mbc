#!/usr/bin/env python3
"""HGG Index runner script"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hgg_index.cli import main

if __name__ == "__main__":
    main()
