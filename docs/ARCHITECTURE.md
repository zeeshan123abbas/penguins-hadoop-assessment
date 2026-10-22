# Architecture

## Data flow

| Stage | Tool | Input | Output |
|---|---|---|---|
| Ingest | `wget`/`curl`, `hdfs dfs -put` | GitHub raw CSV | `/user/maria_dev/datasets/penguins.csv` |
| Query | Hive (HiveServer2, beeline) | HDFS CSV | `penguins_db.penguins_raw` + analysis queries |
| ELT | Python, Pandas, `hdfs.InsecureClient` (WebHDFS) | HDFS CSV | `/user/maria_dev/datasets/clean/penguins_clean.csv` |
| Process | PySpark | Clean CSV | JSON at `/user/maria_dev/spark/output/penguins/species=*` |

## Design decisions

- **Explicit schemas.** Hive DDL and the Spark `StructType` declare every column, so bad rows surface instead of silently becoming strings.
- **Drop only empty rows.** 2 records had no measurements at all and were dropped; every other gap was imputed, keeping 342 of 344 records.
- **Species-median imputation.** Body measurements differ strongly by species (Gentoo average 5076 g vs Adelie 3701 g), so a global mean would bias the smaller species.
- **`unknown` for missing sex.** 11 records lack sex; a label keeps them in the dataset without inventing a value.
- **Cache before multiple actions.** The processed Spark DataFrame is reused for counts, sorting and the write, so it is cached once.
- **Partition by species.** Downstream readers usually filter on species; partitioning lets them read one directory.
- **Testable cleaning logic.** `src/penguins_clean.py` holds the same steps as the notebook and is covered by `tests/`.

## Environment

Single-node cluster: Hadoop 3.3.6 (HDFS + YARN), Hive 3.1.3, Spark 3.5.1, OpenJDK 8, host `sandbox-hdp`, user `maria_dev`.
NameNode RPC `9000`, WebHDFS `9870`, HiveServer2 `10000`. On the Hortonworks HDP sandbox use `8020`, `50070` and `sandbox-hdp.hortonworks.com`.

## Issues met and fixed

| Problem | Fix |
|---|---|
| `Exec format error` starting Java | Replaced x86-64 JDK with the ARM64 build |
| HiveServer2 impersonation refused | Added `hadoop.proxyuser.maria_dev.*` to `core-site.xml` |
| WebHDFS requests routed to a proxy | Set `NO_PROXY=localhost,127.0.0.1,sandbox-hdp` |
| YARN container memory limits on a small node | Documented `--master local[2]` as a fallback; YARN run `application_1792660091975_0001` succeeded |
