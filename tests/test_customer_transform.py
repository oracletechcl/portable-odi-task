import pytest

from pyspark.sql import SparkSession

from src.pyspark.customer_transform import transform_customers


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("customer-transform-tests")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_transform_filters_normalizes_and_calculates_tax(
    spark: SparkSession,
) -> None:
    source = spark.createDataFrame(
        [
            (1, " Ana Lopez ", "ACTIVE", "PE", 100.0),
            (2, "John Smith", "INACTIVE", "US", 50.0),
        ],
        [
            "customer_id",
            "customer_name",
            "status",
            "country",
            "amount",
        ],
    )

    result = transform_customers(source, tax_rate=0.18).collect()

    assert len(result) == 1
    assert result[0]["customer_name"] == "ANA LOPEZ"
    assert result[0]["amount"] == 100.0
    assert result[0]["amount_tax"] == 118.0
