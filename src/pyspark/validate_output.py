"""Portable output-quality validation job."""

import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def parse_arguments() -> argparse.Namespace:
    """Parse runtime-independent validation parameters."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--minimum-records", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    """Fail when output volume or customer identifiers violate quality rules."""
    args = parse_arguments()
    spark = SparkSession.builder.appName("customer-output-validation").getOrCreate()
    try:
        dataframe = spark.read.option("header", "true").csv(args.input)
        record_count = dataframe.count()
        null_customer_ids = dataframe.filter(F.col("customer_id").isNull()).count()

        print(f"Record count: {record_count}")
        print(f"Null customer IDs: {null_customer_ids}")

        if record_count < args.minimum_records:
            raise RuntimeError(
                f"Expected at least {args.minimum_records} records; found {record_count}"
            )
        if null_customer_ids > 0:
            raise RuntimeError(f"Found {null_customer_ids} null customer IDs")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
