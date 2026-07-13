package com.oracle.poc;

import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.round;
import static org.apache.spark.sql.functions.trim;
import static org.apache.spark.sql.functions.upper;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

/** OCI Data Flow Java entry point for the portable customer transformation. */
public final class CustomerJavaProbe {
  private CustomerJavaProbe() {}

  public static void main(String[] args) {
    if (args.length != 3) {
      throw new IllegalArgumentException("Usage: <input-csv> <output-path> <tax-rate>");
    }

    SparkSession spark = SparkSession.builder().appName("customer-java-probe").getOrCreate();
    try {
      Dataset<Row> customers = spark.read().option("header", true).option("inferSchema", true).csv(args[0]);
      Dataset<Row> transformed = customers
          .filter(col("status").equalTo("ACTIVE"))
          .withColumn("customer_name", upper(trim(col("customer_name"))))
          .withColumn("amount", col("amount").cast("double"))
          .withColumn("amount_tax", round(col("amount").multiply(1 + Double.parseDouble(args[2])), 2));
      transformed.write().mode("overwrite").option("header", true).csv(args[1]);
    } finally {
      spark.stop();
    }
  }
}
