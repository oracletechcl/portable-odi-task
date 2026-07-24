from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from urllib.request import Request


IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = IMPLEMENTATION_ROOT / "start-mock-backend.sh"
sys.path.insert(0, str(IMPLEMENTATION_ROOT))

from habitat_sucursales.cli import main
from habitat_sucursales.oci_export import package_backend, sha256_file


def _unused_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_wrapper_has_valid_shell_syntax() -> None:
    result = subprocess.run(
        ["bash", "-n", str(WRAPPER)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_wrapper_is_single_start_point_and_serves_health(tmp_path: Path) -> None:
    port = _unused_port()
    env = os.environ.copy()
    env.update(
        {
            "MOCK_HOST": "127.0.0.1",
            "MOCK_PORT": str(port),
            "MOCK_FIXTURES_DIR": str(IMPLEMENTATION_ROOT / "fixtures/raw"),
            "MOCK_OUTPUT_DIR": str(tmp_path / "output"),
            "PYTHONUNBUFFERED": "1",
        }
    )
    process = subprocess.Popen(
        ["bash", str(WRAPPER)],
        cwd=tmp_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 8
        while True:
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise AssertionError(
                    f"wrapper exited early ({process.returncode})\n{stdout}\n{stderr}"
                )
            try:
                with urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
                    body = json.load(response)
                break
            except URLError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.05)

        assert body == {"service": "habitat-sucursales-mock", "status": "ok"}
        for route, payload in [
            ("/v1/periods", {"as_of_date": "2026-07-24"}),
            (
                "/v1/process/atenciones",
                {"as_of_date": "2026-07-24", "window": "previous"},
            ),
            (
                "/v1/process/atenciones",
                {"as_of_date": "2026-07-24", "window": "current"},
            ),
            (
                "/v1/process/agendamientos",
                {"as_of_date": "2026-07-24", "window": "previous"},
            ),
            (
                "/v1/process/agendamientos",
                {"as_of_date": "2026-07-24", "window": "current"},
            ),
            ("/v1/validate", {"as_of_date": "2026-07-24"}),
        ]:
            request = Request(
                f"http://127.0.0.1:{port}{route}",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=3) as response:
                response_body = json.load(response)
            assert response.status == 200
            assert response_body["status"] == "ok"
        assert len(list((tmp_path / "output").rglob("*.csv"))) == 8
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_wrapper_fails_clearly_when_port_is_in_use(tmp_path: Path) -> None:
    port = _unused_port()
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", port))
        reservation.listen()
        result = subprocess.run(
            ["bash", str(WRAPPER)],
            cwd=tmp_path,
            env={
                **os.environ,
                "MOCK_HOST": "127.0.0.1",
                "MOCK_PORT": str(port),
                "MOCK_FIXTURES_DIR": str(tmp_path / "fixtures"),
                "MOCK_OUTPUT_DIR": str(tmp_path / "output"),
            },
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

    assert result.returncode != 0
    assert "cannot start mock backend" in result.stderr


def test_backend_bundle_is_deterministic_and_machine_ready(tmp_path: Path) -> None:
    first = package_backend(
        IMPLEMENTATION_ROOT, tmp_path / "first-backend.tar.gz"
    )
    second = package_backend(
        IMPLEMENTATION_ROOT, tmp_path / "second-backend.tar.gz"
    )

    assert first.read_bytes() == second.read_bytes()
    with tarfile.open(first, "r:gz") as archive:
        names = archive.getnames()
    assert "implementation/start-mock-backend.sh" in names
    assert "implementation/habitat_sucursales/mock_api.py" in names
    assert any(name.startswith("implementation/fixtures/raw/") for name in names)
    assert not any("/tests/" in name for name in names)


def test_package_backend_cli_writes_bundle_and_checksum(
    tmp_path: Path, capsys
) -> None:
    archive = tmp_path / "habitat-sucursales-mock-backend-1.0.0.tar.gz"

    status = main(
        [
            "package-backend",
            "--implementation-dir",
            str(IMPLEMENTATION_ROOT),
            "--tar-path",
            str(archive),
        ]
    )

    result = json.loads(capsys.readouterr().out)
    checksum_path = Path(f"{archive}.sha256")
    assert status == 0
    assert archive.is_file()
    assert checksum_path.read_text().split()[0] == sha256_file(archive)
    assert result["sha256"] == sha256_file(archive)


def test_readme_documents_the_entire_compute_vm_to_oci_demo() -> None:
    readme = (IMPLEMENTATION_ROOT.parent / "README.md").read_text(encoding="utf-8")

    required_runbook_content = (
        "## Run the Entire End-to-End Demo",
        "odi-portability-demo",
        "HABITAT_SUCURSALES.project.zip",
        "habitat-sucursales-mock-backend-1.0.0.tar.gz",
        "start-mock-backend.sh",
        "TCP 8080",
        "/health",
        "HABITAT_SUCURSALES_DEMO",
        "TASK_RUN_HABITAT_SUCURSALES",
        "MOCK_BASE_URL",
        "AS_OF_DATE",
        "target/expected-output",
        "systemctl",
    )

    for expected in required_runbook_content:
        assert expected in readme
