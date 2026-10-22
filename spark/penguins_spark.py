"""
Section 4 - PySpark Application on Hadoop
Big Data with Hadoop | Palmer Penguins Assessment

Run:
    spark-submit --master yarn spark/penguins_spark.py
    (or --master local[*] on a single-node sandbox)

Reads  : hdfs:///user/maria_dev/datasets/clean/penguins_clean.csv
Writes : hdfs:///user/maria_dev/spark/output/penguins   (JSON, partitioned by species)
"""
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (DoubleType, IntegerType, StringType,
                               StructField, StructType)

HDFS_NN = "hdfs://localhost:9000"   # change to hdfs://sandbox-hdp.hortonworks.com:8020 on HDP
INPUT_PATH = f"{HDFS_NN}/user/maria_dev/datasets/clean/penguins_clean.csv"
OUTPUT_PATH = f"{HDFS_NN}/user/maria_dev/spark/output/penguins"

SCHEMA = StructType([
    StructField("species", StringType(), False),
    StructField("island", StringType(), False),
    StructField("bill_length_mm", DoubleType(), True),
    StructField("bill_depth_mm", DoubleType(), True),
    StructField("flipper_length_mm", DoubleType(), True),
    StructField("body_mass_g", DoubleType(), True),
    StructField("body_mass_kg", DoubleType(), True),
    StructField("sex", StringType(), True),
    StructField("year", IntegerType(), True),
])


def main() -> int:
    spark = (SparkSession.builder
             .appName("PenguinsSparkApp")
             .config("spark.sql.shuffle.partitions", "4")
             .getOrCreate())
    spark.sparkContext.setLogLevel("WARN")

    try:
        # ---- 1. Read the cleaned CSV from HDFS and show its schema -------------
        df = (spark.read
              .option("header", True)
              .schema(SCHEMA)
              .csv(INPUT_PATH))
        print("\n=== [1] Schema of penguins_clean.csv ===")
        df.printSchema()
        print(f"Rows read from HDFS: {df.count()}")
        df.show(5, truncate=False)

        # ---- 2. Select, filter, sort, cache ------------------------------------
        selected = df.select("species", "island", "sex", "year",
                             "bill_length_mm", "flipper_length_mm",
                             "body_mass_kg")

        # remove invalid records: flipper length <= 0 (or null)
        valid = selected.filter(F.col("flipper_length_mm") > 0)
        removed = selected.count() - valid.count()
        print(f"\n=== [2] Records removed with flipper_length_mm <= 0 : {removed}")

        # simple business filter + sort: heavier penguins (>= 4 kg) sorted by mass
        processed = (valid
                     .filter(F.col("body_mass_kg") >= 4.0)
                     .orderBy(F.col("body_mass_kg").desc(),
                              F.col("flipper_length_mm").desc())
                     .cache())

        print(f"Rows after filter (body_mass_kg >= 4.0): {processed.count()}  [cached={processed.is_cached}]")
        processed.show(10, truncate=False)

        print("=== Summary of processed data per species ===")
        (processed.groupBy("species")
         .agg(F.count("*").alias("penguins"),
              F.round(F.avg("body_mass_kg"), 3).alias("avg_mass_kg"),
              F.round(F.avg("flipper_length_mm"), 1).alias("avg_flipper_mm"))
         .orderBy("species")
         .show())

        # ---- 3. Save as JSON partitioned by species ----------------------------
        # one JSON file per species folder, rows kept sorted inside each file
        (processed.repartition("species")
         .sortWithinPartitions(F.col("body_mass_kg").desc())
         .write
         .mode("overwrite")
         .partitionBy("species")
         .json(OUTPUT_PATH))
        print(f"=== [3] JSON output written to {OUTPUT_PATH} (partitioned by species) ===")

        processed.unpersist()
    finally:
        spark.stop()
        print("Spark session stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
