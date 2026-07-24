from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest


SKILL_ROOT = Path(__file__).resolve().parents[1] / "odi-builder"
SCRIPTS = SKILL_ROOT / "scripts"
REFERENCES = SKILL_ROOT / "references"
ASSETS = SKILL_ROOT / "assets"


def run_script(name: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def test_skill_package_is_complete_and_metadata_is_valid() -> None:
    required = {
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "agents" / "openai.yaml",
        REFERENCES / "pentaho-discovery.md",
        REFERENCES / "migration-workflow.md",
        REFERENCES / "oci-project-contract.md",
        REFERENCES / "mock-deployment.md",
        REFERENCES / "live-oci-operations.md",
        REFERENCES / "validation-troubleshooting.md",
        SCRIPTS / "inspect_pentaho.py",
        SCRIPTS / "scaffold_migration.py",
        SCRIPTS / "validate_odi_project.py",
        ASSETS / "migration-spec.template.md",
        ASSETS / "traceability.template.md",
        ASSETS / "deployment.env.example",
        ASSETS / "operator-readme.template.md",
    }
    assert all(path.is_file() for path in required)

    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = skill.split("---", 2)[1].strip().splitlines()
    assert {line.split(":", 1)[0] for line in frontmatter} == {
        "name",
        "description",
    }
    assert "name: odi-builder" in frontmatter

    agent = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert agent.startswith("interface:\n")
    assert "dependencies:" not in agent
    assert "$odi-builder" in agent
    short = re.search(r'short_description: "([^"]+)"', agent)
    assert short
    assert 25 <= len(short.group(1)) <= 64


def test_skill_is_standalone_generic_and_links_stay_inside_package() -> None:
    files = sorted(
        path
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    assert files
    assert not any(path.is_symlink() for path in SKILL_ROOT.rglob("*"))
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in files)

    for forbidden in (
        "$development",
        "development/SKILL.md",
        ".codex/skills",
        "/Users/",
        "TASK_RUN_HABITAT_SUCURSALES",
        "HABITAT_SUCURSALES",
        "TODO",
        "FIXME",
    ):
        assert forbidden not in corpus
    assert not re.search(r"\bocid1\.[a-z0-9.]+\b", corpus, re.IGNORECASE)
    assert not re.search(r"BEGIN [A-Z ]*PRIVATE KEY", corpus)
    addresses = set(re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", corpus))
    assert addresses <= {"0.0.0.0"}

    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", skill)
    assert links
    for link in links:
        assert not link.startswith(("/", "../"))
        resolved = (SKILL_ROOT / link).resolve()
        assert resolved.is_relative_to(SKILL_ROOT.resolve())
        assert resolved.exists()


def test_skill_routes_to_the_complete_end_to_end_workflow() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    for phase in (
        "Intake",
        "Discover",
        "Specify",
        "Test",
        "Implement",
        "Package",
        "Deploy",
        "Publish",
        "Run",
        "Verify",
        "Handoff",
    ):
        assert phase in skill
    for resource in (
        "references/pentaho-discovery.md",
        "references/migration-workflow.md",
        "references/oci-project-contract.md",
        "references/mock-deployment.md",
        "references/live-oci-operations.md",
        "references/validation-troubleshooting.md",
        "scripts/inspect_pentaho.py",
        "scripts/scaffold_migration.py",
        "scripts/validate_odi_project.py",
        "assets/migration-spec.template.md",
        "assets/traceability.template.md",
        "assets/deployment.env.example",
        "assets/operator-readme.template.md",
    ):
        assert f"]({resource})" in skill


def test_skill_encodes_proven_oci_caveats_without_fixed_cardinality() -> None:
    corpus = "\n".join(
        path.read_text(encoding="utf-8") for path in REFERENCES.glob("*.md")
    )
    for required in (
        ".project.zip",
        "objectKeysProvidedForExport",
        "USER_PROJECT",
        "objectStatus: 8",
        "JSON_TEXT",
        "REPLACE",
        "set -euo pipefail",
        "mock-backend.invalid",
        "parameter-free",
        "notification task",
        "INTEGRATION_APPLICATION",
        "application get",
        "get-patch",
        "FAILED",
        "list-published-objects",
        "--all",
        "Page 2",
        "derive expected",
        "derived from the specification",
        "zero parameters",
    ):
        assert required in corpus


def test_reusable_scripts_use_only_the_standard_library_and_have_help() -> None:
    for script in sorted(SCRIPTS.glob("*.py")):
        tree = ast.parse(script.read_text(encoding="utf-8"))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        assert imports <= sys.stdlib_module_names

        result = run_script(script.name, "--help")
        assert result.returncode == 0, result.stderr
        assert "usage:" in result.stdout.lower()


def test_pentaho_inspector_is_deterministic_secret_safe_and_read_only(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    job = source / "main.kjb"
    transformation = source / "transform.ktr"
    job.write_text(
        """<?xml version="1.0"?>
<job>
  <name>MAIN</name>
  <connection>
    <name>PRIVATE_JNDI</name><type>ORACLE</type><access>JNDI</access>
    <server>192.0.2.10</server><database>REAL_DB</database>
    <username>real_user</username><password>super-secret</password>
  </connection>
  <entries>
    <entry><name>START</name><type>SPECIAL</type></entry>
    <entry><name>FLOW</name><type>TRANS</type><filename>transform.ktr</filename></entry>
  </entries>
  <hops>
    <hop><from>START</from><to>FLOW</to><enabled>Y</enabled>
      <evaluation>Y</evaluation><unconditional>Y</unconditional></hop>
  </hops>
  <parameters>
    <parameter><name>API_TOKEN</name><value>ocid1.example.secret</value></parameter>
  </parameters>
</job>
""",
        encoding="utf-8",
    )
    transformation.write_text(
        """<?xml version="1.0"?>
<transformation>
  <name>FLOW</name>
  <step><name>INPUT</name><type>CsvInput</type></step>
  <step><name>OUTPUT</name><type>TextFileOutput</type></step>
  <order><hop><from>INPUT</from><to>OUTPUT</to><enabled>Y</enabled></hop></order>
</transformation>
""",
        encoding="utf-8",
    )
    before = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source.iterdir()
    }

    first = run_script("inspect_pentaho.py", str(source))
    second = run_script("inspect_pentaho.py", str(source))
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert payload["document_count"] == 2
    assert payload["jobs"] == payload["transformations"] == 1
    assert {"MAIN", "FLOW"} <= {item["name"] for item in payload["documents"]}
    assert "<redacted>" in first.stdout
    for sensitive in (
        "192.0.2.10",
        "REAL_DB",
        "real_user",
        "super-secret",
        "ocid1.example.secret",
    ):
        assert sensitive not in first.stdout
    after = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source.iterdir()
    }
    assert after == before


def test_scaffolder_requires_identity_and_dry_run_makes_no_writes(
    tmp_path: Path,
) -> None:
    spec = tmp_path / "spec.md"
    source = tmp_path / "source"
    canonical = tmp_path / "canonical.project"
    output = tmp_path / "output"
    spec.write_text("# Approved\n", encoding="utf-8")
    source.mkdir()
    canonical.mkdir()
    arguments = (
        "--output-root",
        str(output),
        "--spec",
        str(spec),
        "--source-root",
        str(source),
        "--canonical-project",
        str(canonical),
        "--project-name",
        "Novel Project",
        "--project-identifier",
        "NOVEL_PROJECT",
        "--pipeline-name",
        "Novel Pipeline",
        "--pipeline-identifier",
        "PL_NOVEL",
        "--task-name",
        "Run Novel",
        "--task-identifier",
        "TASK_RUN_NOVEL",
        "--release-version",
        "1.2.3",
    )
    dry_run = run_script("scaffold_migration.py", *arguments, "--dry-run")
    assert dry_run.returncode == 0, dry_run.stderr
    assert dry_run.stdout.startswith("PLAN ")
    assert not output.exists()

    created = run_script("scaffold_migration.py", *arguments)
    assert created.returncode == 0, created.stderr
    assert (output / "spec" / "migration-spec.md").is_file()
    assert (output / "analysis" / "source-to-target-traceability.md").is_file()
    assert (output / "platforms" / "oci" / "deployment.env.example").is_file()
    assert (output / "README.md").is_file()

    missing = run_script("scaffold_migration.py")
    assert missing.returncode == 2
    assert "--project-identifier" in missing.stderr
    assert "--task-identifier" in missing.stderr


def write_valid_project(root: Path) -> tuple[Path, Path, str, str]:
    project_root = root / "NOVEL_PROJECT.project"
    objects = project_root / "Objects"
    objects.mkdir(parents=True)
    project_key = "11111111-1111-5111-8111-111111111111"
    rest_key = "22222222-2222-5222-8222-222222222222"
    project_name = f"USER_PROJECT_NOVEL_PROJECT_{project_key}.json"
    rest_name = f"REST_TASK_REST_STAGE_{rest_key}.json"
    (objects / project_name).write_text(
        json.dumps(
            {
                "modelType": "USER_PROJECT",
                "key": project_key,
                "identifier": "NOVEL_PROJECT",
                "objectStatus": 8,
                "metadata": {"registryVersion": 1},
            }
        ),
        encoding="utf-8",
    )
    (objects / rest_name).write_text(
        json.dumps(
            {
                "modelType": "REST_TASK",
                "key": rest_key,
                "identifier": "REST_STAGE",
                "objectStatus": 8,
                "parameters": [],
                "typedExpressions": [],
                "configProviderDelegate": {},
                "metadata": {
                    "aggregator": {
                        "type": "USER_PROJECT",
                        "key": project_key,
                        "identifier": "NOVEL_PROJECT",
                    },
                    "aggregatorKey": project_key,
                    "registryVersion": 1,
                },
                "executeRestCallConfig": {
                    "configValues": {
                        "configParamValues": {
                            "requestURL": {
                                "stringValue": "http://mock-backend.invalid/v1/stage"
                            },
                            "requestPayload": {
                                "refValue": {
                                    "modelType": "JSON_TEXT",
                                    "configValues": {
                                        "configParamValues": {
                                            "dataParam": {"stringValue": "{}"}
                                        }
                                    },
                                }
                            },
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (project_root / "manifest.json").write_text(
        json.dumps(
            {
                "version": "V1",
                "exportedWorkspaceOcid": "",
                "objects": [
                    f"/Objects/{project_name}",
                    f"/Objects/{rest_name}",
                ],
                "objectKeysProvidedForExport": [project_key],
                "referencedObjectsList": [],
                "modelVersionMap": {"257": "20200901"},
            }
        ),
        encoding="utf-8",
    )
    return project_root, objects / rest_name, project_key, rest_key


def zip_project(project_root: Path, destination: Path, explicit_dirs: bool = True) -> None:
    with zipfile.ZipFile(destination, "w") as archive:
        if explicit_dirs:
            archive.writestr(f"{project_root.name}/", "")
            archive.writestr(f"{project_root.name}/Objects/", "")
        for path in sorted(item for item in project_root.rglob("*") if item.is_file()):
            archive.write(path, f"{project_root.name}/{path.relative_to(project_root)}")


def test_odi_validator_accepts_canonical_directory_and_zip(tmp_path: Path) -> None:
    project_root, _, _, _ = write_valid_project(tmp_path)
    valid_directory = run_script("validate_odi_project.py", str(project_root))
    assert valid_directory.returncode == 0, valid_directory.stderr

    archive = tmp_path / "NOVEL_PROJECT.project.zip"
    zip_project(project_root, archive)
    valid_zip = run_script("validate_odi_project.py", str(archive))
    assert valid_zip.returncode == 0, valid_zip.stderr


@pytest.mark.parametrize(
    ("mutation", "diagnostic"),
    (
        ("workspace", "exportedWorkspaceOcid must be empty"),
        ("aggregator", "aggregatorKey does not match USER_PROJECT"),
        ("payload", "requestPayload must use JSON_TEXT"),
        ("parameters", "REST_TASK must be parameter-free"),
    ),
)
def test_odi_validator_rejects_unsafe_or_unpublishable_objects(
    tmp_path: Path, mutation: str, diagnostic: str
) -> None:
    project_root, rest_path, _, _ = write_valid_project(tmp_path)
    if mutation == "workspace":
        manifest_path = project_root / "manifest.json"
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
        value["exportedWorkspaceOcid"] = "not-empty"
        manifest_path.write_text(json.dumps(value), encoding="utf-8")
    else:
        value = json.loads(rest_path.read_text(encoding="utf-8"))
        if mutation == "aggregator":
            value["metadata"]["aggregatorKey"] = "wrong"
        elif mutation == "payload":
            value["executeRestCallConfig"]["configValues"]["configParamValues"][
                "requestPayload"
            ] = {"stringValue": "{}"}
        elif mutation == "parameters":
            value["parameters"] = [{"name": "RUNTIME_VALUE"}]
        rest_path.write_text(json.dumps(value), encoding="utf-8")

    result = run_script("validate_odi_project.py", str(project_root))
    assert result.returncode == 1
    assert diagnostic in result.stderr


def test_odi_validator_requires_explicit_zip_envelope_directories(
    tmp_path: Path,
) -> None:
    project_root, _, _, _ = write_valid_project(tmp_path)
    archive = tmp_path / "NOVEL_PROJECT.project.zip"
    zip_project(project_root, archive, explicit_dirs=False)
    result = run_script("validate_odi_project.py", str(archive))
    assert result.returncode == 1
    assert "explicit top-level .project directory" in result.stderr
    assert "explicit Objects/ directory" in result.stderr


def test_templates_are_present_blank_and_secret_free() -> None:
    env = (ASSETS / "deployment.env.example").read_text(encoding="utf-8")
    assignments = [
        line for line in env.splitlines() if line and not line.startswith("#")
    ]
    assert assignments
    assert all(line.endswith("=") for line in assignments)

    corpus = "\n".join(
        path.read_text(encoding="utf-8") for path in ASSETS.iterdir() if path.is_file()
    )
    assert "PROJECT-NAME.project.zip" in corpus
    assert "Page 2" not in corpus
    assert not re.search(r"\bocid1\.", corpus, re.IGNORECASE)
    assert not re.search(r"BEGIN [A-Z ]*PRIVATE KEY", corpus)
