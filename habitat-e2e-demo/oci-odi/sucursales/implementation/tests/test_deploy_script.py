from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
DEPLOY_SCRIPT = (
    REPO_ROOT / "platforms/oci/scripts/deploy-habitat-sucursales-demo.sh"
)
SYSTEMD_UNIT = (
    REPO_ROOT / "platforms/oci/systemd/habitat-sucursales-mock.service"
)


def test_deploy_script_is_one_command_vm_and_oci_setup() -> None:
    assert DEPLOY_SCRIPT.is_file()
    script = DEPLOY_SCRIPT.read_text(encoding="utf-8")

    syntax = subprocess.run(
        ["bash", "-n", str(DEPLOY_SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
    )
    help_result = subprocess.run(
        ["bash", str(DEPLOY_SCRIPT), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert syntax.returncode == 0, syntax.stderr
    assert help_result.returncode == 0, help_result.stderr
    for required in (
        "set -euo pipefail",
        "--app-name",
        "--as-of-date",
        "VM_PUBLIC_IP",
        "VM_PRIVATE_IP",
        "VM_SSH_KEY",
        "OCI_WORKSPACE_ID",
        "OCI_BUCKET_NAME",
        "sha256",
        "scp",
        "ssh",
        "python3.11",
        "firewall-cmd",
        "systemctl enable --now",
        "/health",
        "os object put",
        "import-request create",
        "update-task-from-rest-task",
        '"modelType": "JSON_TEXT"',
        "application create",
        "application get",
        "--model-type INTEGRATION_APPLICATION",
        "application create-patch",
        "application get-patch",
        "application list-published-objects",
        "TASK_RUN_HABITAT_SUCURSALES",
        "FAILED",
        "SUCCESSFUL",
    ):
        assert required in script

    missing_app_name = subprocess.run(
        ["bash", str(DEPLOY_SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
        env={"PATH": os.environ["PATH"], "DEMO_CONFIG_FILE": "/dev/null"},
    )
    assert missing_app_name.returncode != 0
    assert "--app-name is required" in missing_app_name.stderr
    assert 'OCI_APPLICATION_IDENTIFIER="${OCI_APPLICATION_IDENTIFIER:-' not in script
    assert 'OCI_DEPLOY_AS_OF_DATE="${' not in script
    assert not re.search(r"\bocid1\.", script)
    assert not re.search(r'VM_PUBLIC_IP="\$\{[^}]+:-', script)
    assert not re.search(r'VM_PRIVATE_IP="\$\{[^}]+:-', script)
    assert "--wait-for-state ACTIVE" not in script


def test_systemd_unit_runs_only_the_mock_wrapper() -> None:
    assert SYSTEMD_UNIT.is_file()
    unit = SYSTEMD_UNIT.read_text(encoding="utf-8")

    assert "User=opc" in unit
    assert "MOCK_PYTHON_BIN=/usr/bin/python3.11" in unit
    assert "MOCK_HOST=0.0.0.0" in unit
    assert "MOCK_PORT=8080" in unit
    assert (
        "ExecStart=/opt/habitat-sucursales/current/"
        "implementation/start-mock-backend.sh"
    ) in unit
    assert "Restart=on-failure" in unit
