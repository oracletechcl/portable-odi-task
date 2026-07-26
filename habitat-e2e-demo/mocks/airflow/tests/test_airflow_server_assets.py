from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


SERVER_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SERVER_ROOT / "scripts"
SYSTEMD_UNIT = SERVER_ROOT / "systemd" / "airflow-standalone.service"


def run_script(name: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPTS / name), *arguments],
        check=False,
        capture_output=True,
        text=True,
        env={"PATH": os.environ["PATH"]},
    )


def test_required_airflow_server_assets_exist() -> None:
    for path in (
        SERVER_ROOT / "README.md",
        SERVER_ROOT / "docs" / "official-sources.md",
        SERVER_ROOT / "config" / "airflow.env.template",
        SYSTEMD_UNIT,
        SCRIPTS / "deploy-airflow-server.sh",
        SCRIPTS / "install-airflow-server.sh",
        SCRIPTS / "show-airflow-credentials.sh",
        SCRIPTS / "deploy-dag.sh",
    ):
        assert path.is_file(), path


def test_every_shell_script_is_strict_valid_and_has_help() -> None:
    for script in sorted(SCRIPTS.glob("*.sh")):
        text = script.read_text(encoding="utf-8")
        assert text.startswith("#!/usr/bin/env bash\nset -euo pipefail\n")
        syntax = subprocess.run(
            ["bash", "-n", str(script)],
            check=False,
            capture_output=True,
            text=True,
        )
        help_result = run_script(script.name, "--help")
        assert syntax.returncode == 0, syntax.stderr
        assert help_result.returncode == 0, help_result.stderr
        assert "Usage:" in help_result.stdout


def test_install_contract_is_airflow_330_vanilla_and_loopback_only() -> None:
    script = (SCRIPTS / "install-airflow-server.sh").read_text(encoding="utf-8")
    env_template = (
        SERVER_ROOT / "config" / "airflow.env.template"
    ).read_text(encoding="utf-8")

    for required in (
        'AIRFLOW_VERSION="3.3.0"',
        "constraints-3.3.0/constraints-3.11.txt",
        "python3.11",
        "-m venv",
        "apache-airflow[standard]==${AIRFLOW_VERSION}",
        "pip check",
        "db migrate",
        "systemctl enable --now airflow-standalone.service",
        "/api/v2/monitor/health",
        "simple_auth_manager_passwords.json.generated",
        "secrets.token_urlsafe",
        "credentials.get(username)",
        "os.replace(temporary_path, path)",
        "chmod 0600",
        "MOCK_PID_BEFORE",
        "MOCK_UNIT_SHA_BEFORE",
    ):
        assert required in script
    assert "firewall-cmd" not in script
    assert not re.search(r"systemctl\s+(restart|stop|start).*habitat", script)

    for required in (
        "AIRFLOW_HOME=@@AIRFLOW_HOME@@",
        "AIRFLOW__CORE__DAGS_FOLDER=@@DAGS_FOLDER@@",
        "AIRFLOW__CORE__LOAD_EXAMPLES=False",
        "AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_USERS=@@ADMIN_USER@@:admin",
        "AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE=@@PASSWORD_FILE@@",
        "AIRFLOW__API__HOST=127.0.0.1",
        "AIRFLOW__API__PORT=@@AIRFLOW_PORT@@",
        "AIRFLOW__CORE__EXECUTION_API_SERVER_URL=http://127.0.0.1:@@AIRFLOW_PORT@@/execution/",
    ):
        assert required in env_template

    assert "0.0.0.0" not in env_template
    assert "AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_ALL_ADMINS=True" not in env_template
    assert "AIRFLOW__CORE__LOAD_EXAMPLES=True" not in env_template


def test_systemd_unit_is_test_scoped_and_hardened() -> None:
    unit = SYSTEMD_UNIT.read_text(encoding="utf-8")
    for required in (
        "User=airflow",
        "Group=airflow",
        "EnvironmentFile=/etc/airflow/airflow.env",
        "ExecStart=/opt/airflow/venv/bin/airflow standalone",
        "Restart=on-failure",
        "NoNewPrivileges=true",
        "PrivateTmp=true",
        "ProtectHome=true",
        "UMask=0027",
        "KillMode=control-group",
    ):
        assert required in unit


def test_one_stop_deploy_requires_every_environment_value_and_has_safe_dry_run(
    tmp_path: Path,
) -> None:
    script = SCRIPTS / "deploy-airflow-server.sh"
    text = script.read_text(encoding="utf-8")
    for required in (
        "--vm-public-ip",
        "--ssh-user",
        "--ssh-key",
        "--airflow-port",
        "--admin-user",
        "--dry-run",
        "install-airflow-server.sh",
        "airflow-standalone.service",
        "airflow.env.template",
        "sha256",
        "scp",
        "ssh",
    ):
        assert required in text

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    marker = tmp_path / "external-called"
    for command in ("ssh", "scp"):
        executable = fake_bin / command
        executable.write_text(
            f"#!/usr/bin/env bash\ntouch {marker}\nexit 99\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)

    key = tmp_path / "key"
    key.write_text("fixture", encoding="utf-8")
    result = subprocess.run(
        [
            "bash",
            str(script),
            "--vm-public-ip",
            "192.0.2.10",
            "--ssh-user",
            "operator",
            "--ssh-key",
            str(key),
            "--airflow-port",
            "8081",
            "--admin-user",
            "airflowadmin",
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
        env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    assert not marker.exists()

    missing = run_script("deploy-airflow-server.sh")
    assert missing.returncode != 0
    assert "--vm-public-ip is required" in missing.stderr

    assert not re.search(r'VM_PUBLIC_IP="\$\{[^}]+:-', text)
    assert not re.search(r'AIRFLOW_PORT="\$\{[^}]+:-', text)
    assert not re.search(r'ADMIN_USER="\$\{[^}]+:-', text)


def test_credentials_are_generated_remote_only_and_never_embedded() -> None:
    installer = (SCRIPTS / "install-airflow-server.sh").read_text(encoding="utf-8")
    helper = (SCRIPTS / "show-airflow-credentials.sh").read_text(encoding="utf-8")
    runtime_files = [
        SERVER_ROOT / "README.md",
        *(SERVER_ROOT / "config").glob("*"),
        *(SERVER_ROOT / "docs").glob("*"),
        *SCRIPTS.glob("*.sh"),
        *(SERVER_ROOT / "systemd").glob("*"),
    ]
    corpus = "\n".join(
        path.read_text(encoding="utf-8") for path in runtime_files if path.is_file()
    )

    assert "simple_auth_manager_passwords.json.generated" in helper
    assert "sudo" in helper
    assert "chmod 0600" in installer
    assert "secrets.token_urlsafe" in installer
    assert "PASSWORD=" not in corpus
    assert "AIRFLOW_PASSWORD=" not in corpus
    assert not re.search(r"\bocid1\.", corpus, re.IGNORECASE)
    assert not re.search(r"BEGIN [A-Z ]*PRIVATE KEY", corpus)
    assert "/Users/" not in corpus
    assert "170.9." not in corpus


def test_dag_deployer_validates_python_and_installs_as_airflow() -> None:
    script = (SCRIPTS / "deploy-dag.sh").read_text(encoding="utf-8")
    for required in (
        "--dag-file",
        '[[ "${DAG_FILE}" == *.py ]]',
        "compile(",
        "sha256",
        "scp",
        "sudo install -o airflow -g airflow -m 0644",
        "/var/lib/airflow/dags",
        "airflow dags list-import-errors",
    ):
        assert required in script


def test_readme_is_a_short_complete_operator_runbook() -> None:
    readme = (SERVER_ROOT / "README.md").read_text(encoding="utf-8")
    for required in (
        "Apache Airflow 3.3.0",
        "TEST only",
        "8080",
        "8081",
        "## 1. Deploy",
        "deploy-airflow-server.sh",
        "## 2. Read the generated credentials",
        "show-airflow-credentials.sh",
        "## 3. Open the SSH tunnel",
        "127.0.0.1:8081",
        "## 4. Deploy a DAG",
        "deploy-dag.sh",
        "/api/v2/monitor/health",
        "systemctl status airflow-standalone.service",
        "journalctl -u airflow-standalone.service",
        "simple_auth_manager_passwords.json.generated",
    ):
        assert required in readme
    assert len(readme.splitlines()) <= 140


def test_official_sources_are_airflow_330_primary_docs() -> None:
    sources = (SERVER_ROOT / "docs" / "official-sources.md").read_text(
        encoding="utf-8"
    )
    for required in (
        "Airflow 3.3.0",
        "airflow.apache.org/docs/apache-airflow/3.3.0/installation/installing-from-pypi.html",
        "airflow.apache.org/docs/apache-airflow/3.3.0/core-concepts/auth-manager/simple/",
        "airflow.apache.org/docs/apache-airflow/3.3.0/configurations-ref.html",
        "airflow.apache.org/docs/apache-airflow/3.3.0/administration-and-deployment/logging-monitoring/check-health.html",
    ):
        assert required in sources
