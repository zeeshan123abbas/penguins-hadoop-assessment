#!/usr/bin/env bash
# Runs the full pipeline end to end on a Hadoop sandbox as maria_dev.
#   bash scripts/run_all.sh
# Override endpoints with env vars, e.g. HIVE_URL=jdbc:hive2://sandbox-hdp.hortonworks.com:10000
set -euo pipefail
cd "$(dirname "$0")/.."

HIVE_URL="${HIVE_URL:-jdbc:hive2://localhost:10000}"
HDFS_USER="${HDFS_USER:-maria_dev}"
SPARK_MASTER="${SPARK_MASTER:-yarn}"
export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1,sandbox-hdp}"

step() { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }

step "Section 1: HDFS"
bash hdfs/section1_hdfs_commands.sh

step "Section 2: Hive"
hdfs dfs -mkdir -p /user/${HDFS_USER}/hive_stage
hdfs dfs -cp -f /user/${HDFS_USER}/datasets/penguins.csv /user/${HDFS_USER}/hive_stage/
beeline -u "${HIVE_URL}" -n "${HDFS_USER}" -f hive/penguins.hql

step "Section 3: WebHDFS + Pandas (executing notebook)"
jupyter nbconvert --to notebook --execute --inplace notebooks/penguins_elt_webhdfs.ipynb

step "Section 4: PySpark"
hdfs dfs -rm -r -f /user/${HDFS_USER}/spark/output/penguins
spark-submit --master "${SPARK_MASTER}" spark/penguins_spark.py
hdfs dfs -ls -R /user/${HDFS_USER}/spark/output/penguins

step "Pipeline complete"
