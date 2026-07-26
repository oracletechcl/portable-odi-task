"""Boundary client and filesystem orchestration; business formatting stays pure."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

from web_transformations import ContractError, DATASET_CONTRACTS, render_dataset

ROUTES = {name: f"/v1/web/{name.lower().replace('_', '-')}" for name in DATASET_CONTRACTS}


class PipelineError(RuntimeError):
    pass


def post_json(base_url: str, route: str, payload: dict[str, str]) -> object:
    request = Request(base_url.rstrip("/") + route, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def run_pipeline(*, base_url: str, output_dir: Path, run_date: str) -> dict[str, object]:
    try:
        date.fromisoformat(run_date)
    except ValueError as exc:
        raise PipelineError("run_date must use YYYY-MM-DD") from exc
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for dataset, route in ROUTES.items():
        try:
            response = post_json(base_url, route, {"runDate": run_date})
            records = response.get("records") if isinstance(response, Mapping) else None
            if not isinstance(records, list) or not all(isinstance(row, Mapping) for row in records):
                raise PipelineError("response must contain records")
            content = render_dataset(dataset, records)
        except (OSError, ValueError, ContractError) as exc:
            raise PipelineError(f"{dataset}: {exc}") from exc
        path = output_dir / f"{dataset}.csv"
        path.write_bytes(content)
        outputs.append({"name": path.name, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "rows": content.count(b"\n"), "encoding": "ISO-8859-1", "delimiter": "~|", "newline": "LF"})
    manifest = {"runDate": run_date, "outputs": outputs}
    (output_dir / "run-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest
