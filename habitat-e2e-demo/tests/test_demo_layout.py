from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEMO_ROOT = REPOSITORY_ROOT / "habitat-e2e-demo"


def test_airflow_server_is_centralized_under_mocks() -> None:
    airflow_root = DEMO_ROOT / "mocks" / "airflow"

    assert {
        path.name for path in airflow_root.iterdir() if path.is_dir()
    } == {"config", "docs", "scripts", "systemd", "tests"}
    assert (airflow_root / "scripts" / "deploy-airflow-server.sh").is_file()
    assert (airflow_root / "tests" / "test_airflow_server_assets.py").is_file()
    assert (airflow_root / "README.md").is_file()
    assert not (DEMO_ROOT / "airflow").exists()
    assert not (DEMO_ROOT / "migrated-airflow-demo").exists()


def test_oci_odi_is_grouped_by_pentaho_migration() -> None:
    oci_odi_root = DEMO_ROOT / "oci-odi"
    sucursales = DEMO_ROOT / "oci-odi" / "sucursales"
    web = DEMO_ROOT / "oci-odi" / "web"

    assert {
        path.name for path in oci_odi_root.iterdir() if path.is_dir()
    } == {"sucursales", "web"}
    assert (sucursales / "README.md").is_file()
    assert (sucursales / "implementation" / "habitat_sucursales").is_dir()
    assert (sucursales / "target" / "HABITAT_SUCURSALES.project.zip").is_file()
    assert (web / "README.md").is_file()
    assert (web / "implementation" / "habitat_web").is_dir()
    assert (web / "target" / "HABITAT_WEB.project.zip").is_file()
    assert not (DEMO_ROOT / "migrated-pipeline-demo").exists()
    assert not (DEMO_ROOT / "migrated-pipeline-web-demo").exists()


def test_active_files_do_not_reference_the_retired_roots() -> None:
    roots = (
        REPOSITORY_ROOT / ".gitignore",
        REPOSITORY_ROOT / "platforms",
        DEMO_ROOT / "mocks",
        DEMO_ROOT / "oci-odi",
    )
    retired = (
        "habitat-e2e-demo/airflow",
        "migrated-airflow-demo",
        "migrated-pipeline-demo",
        "migrated-pipeline-web-demo",
    )

    for root in roots:
        files = [root] if root.is_file() else root.rglob("*")
        for path in files:
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.suffix in {".gz", ".zip", ".pyc"}:
                continue
            text = path.read_text(encoding="utf-8")
            assert not any(name in text for name in retired), path
