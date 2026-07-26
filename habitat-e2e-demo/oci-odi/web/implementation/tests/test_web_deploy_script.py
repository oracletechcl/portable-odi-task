from __future__ import annotations

import subprocess
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[2]


def test_root_deployer_requires_config_and_app_name() -> None:
    result = subprocess.run(
        [str(APP_ROOT / "deploy.sh"), "--dry-run"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    assert "--config is required" in result.stderr


def test_deployer_dry_run_validates_without_contacting_mock_or_oci(
    tmp_path: Path,
) -> None:
    config = tmp_path / "web.env"
    config.write_text(
        "\n".join(
            (
                "OCI_CLI_PROFILE=demo",
                "OCI_REGION=region",
                "OCI_WORKSPACE_ID=workspace",
                "OCI_BUCKET_NAME=bucket",
                "OCI_OBJECT_NAME=HABITAT_WEB.project.zip",
                "OCI_APPLICATION_IDENTIFIER=HABITAT_WEB_DEMO",
                "MOCK_BASE_URL=http://trusted-mock.invalid:8000",
                "RUN_DATE=2026-07-25",
                "PROJECT_ZIP=target/HABITAT_WEB.project.zip",
                "PROJECT_SHA256=target/HABITAT_WEB.project.zip.sha256",
                "PIPELINE_TASK_IDENTIFIER=TASK_RUN_HABITAT_WEB",
                "IMPORT_TIMEOUT_SECONDS=600",
                "PATCH_TIMEOUT_SECONDS=600",
            )
        )
        + "\n"
    )

    result = subprocess.run(
        [
            str(APP_ROOT / "deploy.sh"),
            "--config",
            str(config),
            "--app-name",
            "Habitat Web Demo",
            "--dry-run",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "no OCI mutation performed" in result.stdout
    assert "trusted external service" in result.stdout


def test_deployer_contains_complete_import_publish_verification_contract() -> None:
    text = (APP_ROOT / "platforms/oci/scripts/deploy.sh").read_text()
    for required in (
        "import-request create",
        "update-task-from-rest-task",
        "application create-patch",
        "application get-patch",
        "application list-published-objects",
        "--all",
        "READY_WITH_TRUSTED_MOCK",
    ):
        assert required in text
