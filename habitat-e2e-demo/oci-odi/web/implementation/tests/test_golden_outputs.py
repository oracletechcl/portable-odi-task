from __future__ import annotations

import hashlib
import json
from pathlib import Path

from habitat_web.transformations import render_dataset


IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = IMPLEMENTATION_ROOT.parent


def test_synthetic_fixtures_regenerate_byte_exact_golden_outputs() -> None:
    manifest = json.loads(
        (APP_ROOT / "expected-output" / "run-manifest.json").read_text()
    )

    for item in manifest["outputs"]:
        dataset = item["path"].removesuffix(".csv")
        fixture = json.loads(
            (
                IMPLEMENTATION_ROOT
                / "fixtures"
                / "mock-responses"
                / f"{dataset}.json"
            ).read_text()
        )
        actual = render_dataset(dataset, fixture["records"])
        expected = (APP_ROOT / "expected-output" / item["path"]).read_bytes()
        assert actual == expected
        assert hashlib.sha256(actual).hexdigest() == item["sha256"]
        assert len(actual) == item["bytes"]
        assert actual.count(b"\n") == item["rows"]

