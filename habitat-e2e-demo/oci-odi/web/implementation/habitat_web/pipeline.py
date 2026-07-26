from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from .transformations import DATASET_CONTRACTS, ContractError, render_dataset


class PipelineError(RuntimeError):
    """Raised when a stage fails and the source failure branch must be taken."""


class JsonClient(Protocol):
    def post_json(self, route: str, payload: dict[str, str]) -> Any: ...


ROUTES: dict[str, str] = {
    dataset: f"/v1/web/{dataset.lower().replace('_', '-')}"
    for dataset in DATASET_CONTRACTS
}


def _records(response: object, dataset: str) -> list[Mapping[str, object]]:
    if isinstance(response, list):
        value = response
    elif isinstance(response, Mapping):
        value = response.get("records", response.get("rows"))
    else:
        value = None
    if not isinstance(value, list) or not all(
        isinstance(row, Mapping) for row in value
    ):
        raise PipelineError(f"{dataset}: response must contain records")
    return value


def run_pipeline(
    *,
    client: JsonClient,
    output_dir: Path,
    run_date: str,
) -> dict[str, object]:
    if ".." in output_dir.parts:
        raise PipelineError("output directory must not contain path traversal")
    try:
        date.fromisoformat(run_date)
    except ValueError as exc:
        raise PipelineError("run_date must use YYYY-MM-DD") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_outputs: list[dict[str, object]] = []
    for dataset, route in ROUTES.items():
        try:
            response = client.post_json(route, {"runDate": run_date})
            content = render_dataset(dataset, _records(response, dataset))
        except (Exception, ContractError) as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            raise PipelineError(f"{dataset}: {exc}") from exc
        path = output_dir / f"{dataset}.csv"
        path.write_bytes(content)
        manifest_outputs.append(
            {
                "name": path.name,
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
                "rows": content.count(b"\n"),
                "encoding": "ISO-8859-1",
                "delimiter": "~|",
                "newline": "LF",
            }
        )

    manifest: dict[str, object] = {
        "runDate": run_date,
        "outputs": manifest_outputs,
    }
    (output_dir / "run-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest

