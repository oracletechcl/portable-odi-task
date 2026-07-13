"""Structural checks for portable Spark language probes."""

from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def test_maven_build_defines_java_and_scala_data_flow_artifacts() -> None:
    """The OCI Data Flow Maven build packages Java and Scala job JARs."""
    pom = ROOT / "pom.xml"
    assert pom.is_file()

    namespaces = {"m": "http://maven.apache.org/POM/4.0.0"}
    root = ET.parse(pom).getroot()
    artifact_id = root.findtext("m:artifactId", namespaces=namespaces)
    assert artifact_id == "portable-spark-language-probes"

    final_names = {
        value.text
        for value in root.findall(".//m:finalName", namespaces)
        if value.text is not None
    }
    assert "customer-java-probe" in final_names
    assert "customer-scala-probe" in final_names


def test_all_supported_language_probes_are_present() -> None:
    """Each OCI Data Flow language option has a runnable sample artifact."""
    expected_sources = {
        "java": ROOT / "src/java/com/oracle/poc/CustomerJavaProbe.java",
        "scala": ROOT / "src/scala/com/oracle/poc/CustomerScalaProbe.scala",
        "sql": ROOT / "src/sql/customer_transform.sql",
    }

    for language, source in expected_sources.items():
        assert source.is_file(), f"Missing {language} Data Flow probe: {source}"


def test_sql_probe_encodes_the_portable_customer_transformation() -> None:
    """SQL mirrors the active-customer name and tax transformation contract."""
    sql = (ROOT / "src/sql/customer_transform.sql").read_text(encoding="utf-8")

    assert "CREATE OR REPLACE TEMP VIEW active_customers" in sql
    assert "UPPER(TRIM(customer_name))" in sql
    assert "amount * (1 + ${tax_rate})" in sql
