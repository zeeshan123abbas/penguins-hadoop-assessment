# Section 4: PySpark application
from pyspark.sql import SparkSession

# Start Spark session
spark = SparkSession.builder.appName("PenguinsApp").getOrCreate()

# Read clean CSV from HDFS
df = spark.read.csv("/user/maria_dev/datasets/clean/penguins_clean.csv",
                    header=True, inferSchema=True)

# Display schema
df.printSchema()

# Select relevant columns
df2 = df.select("species", "island", "flipper_length_mm", "body_mass_kg", "sex")

# Remove records with flipper length <= 0
df2 = df2.filter(df2.flipper_length_mm > 0)

# Sort by body mass (highest first)
df2 = df2.orderBy(df2.body_mass_kg.desc())

# Cache the result
df2.cache()
df2.show(10)

# Save as JSON in HDFS, partitioned by island
df2.write.mode("overwrite").partitionBy("island").json("/user/maria_dev/spark/output/penguins")

# Stop Spark session
spark.stop()
