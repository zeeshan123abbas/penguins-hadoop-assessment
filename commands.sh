# Section 1: HDFS using command line (run on the VM terminal)

# 1. Create directory in HDFS
hdfs dfs -mkdir -p /user/maria_dev/datasets

# 2. Download dataset to VM local file system
wget https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv

# 3. Copy penguins.csv from local to HDFS
hdfs dfs -put penguins.csv /user/maria_dev/datasets/

# 4. List contents of the HDFS directory
hdfs dfs -ls /user/maria_dev/datasets

# Section 4: run PySpark application
# spark-submit spark/penguins_spark.py
# hdfs dfs -ls -R /user/maria_dev/spark/output/penguins
