package com.oracle.poc

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions.{col, round, trim, upper}

/** OCI Data Flow Scala entry point for the portable customer transformation. */
object CustomerScalaProbe {
  def main(args: Array[String]): Unit = {
    require(args.length == 3, "Usage: <input-csv> <output-path> <tax-rate>")

    val spark = SparkSession.builder.appName("customer-scala-probe").getOrCreate()
    try {
      val transformed = spark.read.option("header", true).option("inferSchema", true).csv(args(0))
        .filter(col("status") === "ACTIVE")
        .withColumn("customer_name", upper(trim(col("customer_name"))))
        .withColumn("amount", col("amount").cast("double"))
        .withColumn("amount_tax", round(col("amount") * (1 + args(2).toDouble), 2))
      transformed.write.mode("overwrite").option("header", true).csv(args(1))
    } finally {
      spark.stop()
    }
  }
}
