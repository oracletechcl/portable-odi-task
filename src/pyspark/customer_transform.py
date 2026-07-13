"""Portable customer transformation job."""

import argparse

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def parse_arguments() -> argparse.Namespace:
    """Parse runtime-independent Spark job parameters."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--tax-rate", type=float, default=0.18)
    return parser.parse_args()


def transform_customers(dataframe: DataFrame, tax_rate: float) -> DataFrame:
    """Retain active customers, normalize names, and calculate tax."""
    return (
        dataframe.filter(F.col("status") == "ACTIVE")
        .withColumn("customer_name", F.upper(F.trim(F.col("customer_name"))))
        .withColumn("amount", F.col("amount").cast("double"))
        .withColumn("amount_tax", F.round(F.col("amount") * F.lit(1 + tax_rate), 2))
        .select(
            "customer_id",
            "customer_name",
            "status",
            "country",
            "amount",
            "amount_tax",
        )
    )


def main() -> None:
    """Execute the transformation using paths supplied by the runtime."""
    args = parse_arguments()
    spark = SparkSession.builder.appName("customer-portability-demo").getOrCreate()
    try:
        source = (
            spark.read.option("header", "true")
            .option("inferSchema", "true")
            .csv(args.input)
        )
        result = transform_customers(source, args.tax_rate)
        result.coalesce(1).write.mode("overwrite").option("header", "true").csv(
            args.output
        )
        print(f"Input records: {source.count()}")
        print(f"Output records: {result.count()}")
        print(f"Output path: {args.output}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
