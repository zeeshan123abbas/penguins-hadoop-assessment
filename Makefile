.PHONY: install test pipeline hdfs hive notebook spark

install:
	pip install -r requirements.txt

test:
	python -m pytest -q

pipeline:
	bash scripts/run_all.sh

hdfs:
	bash hdfs/section1_hdfs_commands.sh

hive:
	beeline -u jdbc:hive2://localhost:10000 -n maria_dev -f hive/penguins.hql

notebook:
	jupyter nbconvert --to notebook --execute --inplace notebooks/penguins_elt_webhdfs.ipynb

spark:
	spark-submit --master yarn spark/penguins_spark.py
