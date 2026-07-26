from __future__ import annotations

import sys
from pathlib import Path

IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(IMPLEMENTATION_ROOT))

