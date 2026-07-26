"""Build the canonical OCI REST task configuration used by deployment."""
from __future__ import annotations

import json
import sys


def build(task_key: str, base_url: str, as_of_date: str) -> dict[str, object]:
    payload = json.dumps({"as_of_date": as_of_date}, separators=(",", ":"))
    return {
        "methodType": "POST",
        "requestHeaders": {"Content-Type": "application/json"},
        "configValues": {
            "parentRef": {"parent": task_key},
            "configParamValues": {
                "requestURL": {"stringValue": base_url.rstrip("/") + "/v1/run"},
                "requestPayload": {
                    "refValue": {
                        "modelType": "JSON_TEXT",
                        "configValues": {"configParamValues": {"dataParam": {"stringValue": payload}}},
                    }
                },
            },
        },
    }


if __name__ == "__main__":
    print(json.dumps(build(*sys.argv[1:]), separators=(",", ":")))
