#!/usr/bin/env bash
# =====================================================================
#  Section 1 - HDFS Using the Command Line
#  Big Data with Hadoop | Palmer Penguins Assessment
#  Run as: maria_dev on the Hadoop sandbox
# =====================================================================
set -euo pipefail

DATA_URL="https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv"
LOCAL_DIR="$HOME/datasets"
HDFS_DIR="/user/maria_dev/datasets"

echo "== Task 1: Create ${HDFS_DIR} in HDFS =="
hdfs dfs -mkdir -p "${HDFS_DIR}"

echo "== Task 2: Download the dataset into the VM's local file system =="
mkdir -p "${LOCAL_DIR}"
curl -sSL -o "${LOCAL_DIR}/penguins.csv" "${DATA_URL}"   # or: wget -O ...
ls -lh "${LOCAL_DIR}/penguins.csv"
head -5 "${LOCAL_DIR}/penguins.csv"

echo "== Task 3: Copy penguins.csv from local FS into HDFS =="
hdfs dfs -put -f "${LOCAL_DIR}/penguins.csv" "${HDFS_DIR}/"

echo "== Task 4: List the contents of ${HDFS_DIR} =="
hdfs dfs -ls "${HDFS_DIR}"

# Extra verification (optional)
hdfs dfs -cat "${HDFS_DIR}/penguins.csv" | head -5
hdfs dfs -du -h "${HDFS_DIR}"
