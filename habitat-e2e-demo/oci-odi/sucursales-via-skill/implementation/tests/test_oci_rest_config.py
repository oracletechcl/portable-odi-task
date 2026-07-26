from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))
from oci_rest_config import build


def test_deployment_rest_configuration_has_canonical_json_text_payload():
    config = build("task-key", "http://10.0.20.127:8000/", "2024-03-15")
    assert config["configValues"]["parentRef"] == {"parent": "task-key"}
    values = config["configValues"]["configParamValues"]
    assert values["requestURL"]["stringValue"] == "http://10.0.20.127:8000/v1/run"
    assert values["requestPayload"]["refValue"]["modelType"] == "JSON_TEXT"
    assert json.loads(values["requestPayload"]["refValue"]["configValues"]["configParamValues"]["dataParam"]["stringValue"]) == {"as_of_date": "2024-03-15"}
