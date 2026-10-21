# Big Data with Hadoop: Penguins Dataset

Assessment project using HDFS, Hive, Python (WebHDFS) and PySpark on the Hadoop sandbox.

## Files
- `commands.sh`: Section 1, HDFS commands
- `hive_queries.sql`: Section 2, Hive table and queries
- `penguins_elt.ipynb`: Section 3, Jupyter notebook (WebHDFS + Pandas cleaning)
- `spark/penguins_spark.py`: Section 4, PySpark application

## Run order
1. Run `commands.sh` commands on the VM
2. Run `hive_queries.sql` in Hive
3. Run `penguins_elt.ipynb` in Jupyter (Windows)
4. `spark-submit spark/penguins_spark.py`

Dataset: https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv
