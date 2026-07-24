from __future__ import annotations

import json
import re
import sys
from pathlib import Path


IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(IMPLEMENTATION_ROOT))

from habitat_sucursales.oci_export import build_export_documents


SECRET_ASSIGNMENT = re.compile(
    r"(?i)(password|private[_-]?key|client[_-]?secret)\s*[:=]\s*[\"'][^$<{][^\"']+"
)
REAL_ENDPOINT = re.compile(
    r"https?://(?!\$\{MOCK_BASE_URL\}|mock-backend\.invalid)"
)


def test_generated_export_has_no_ocids_secrets_or_real_endpoints() -> None:
    serialized = json.dumps(build_export_documents(), sort_keys=True)

    assert "ocid1." not in serialized
    assert SECRET_ASSIGNMENT.search(serialized) is None
    assert REAL_ENDPOINT.search(serialized) is None
    assert "${MOCK_BASE_URL}" in serialized


def test_owned_runtime_files_have_no_embedded_secrets() -> None:
    files = [
        *IMPLEMENTATION_ROOT.joinpath("habitat_sucursales").glob("*.py"),
        IMPLEMENTATION_ROOT / "start-mock-backend.sh",
        IMPLEMENTATION_ROOT / "config/pipeline.yaml",
    ]

    for path in files:
        if not path.is_file():
            continue
        text = path.read_text(errors="replace")
        assert "ocid1." not in text, path
        assert SECRET_ASSIGNMENT.search(text) is None, path
        assert REAL_ENDPOINT.search(text) is None, path
