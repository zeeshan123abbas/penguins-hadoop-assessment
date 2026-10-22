# Big Data with Hadoop: Palmer Penguins Pipeline

![Hadoop](https://img.shields.io/badge/Hadoop-3.3.6-66CCFF?logo=apachehadoop&logoColor=black)
![Hive](https://img.shields.io/badge/Hive-3.1.3-FDEE21?logo=apachehive&logoColor=black)
![Spark](https://img.shields.io/badge/Spark-3.5.1-E25A1C?logo=apachespark&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

An end-to-end big data pipeline on the **Palmer Penguins** dataset (344 records):
**HDFS → Hive → Python/Pandas ELT over WebHDFS → PySpark**, executed on a working Hadoop cluster as user `maria_dev`.

**Author:** Zeeshan Abbas · T3 Hadoop Assessment

---

## Pipeline architecture

```mermaid
flowchart LR
    A[penguins.csv<br/>GitHub source] -->|wget + hdfs dfs -put| B[(HDFS<br/>/user/maria_dev/datasets)]
    B -->|LOAD DATA| C[Hive<br/>penguins_db.penguins_raw]
    C --> D[HiveQL analysis<br/>counts, averages, nulls]
    B -->|WebHDFS InsecureClient| E[Jupyter + Pandas<br/>clean, impute, kg]
    E -->|upload| F[(HDFS<br/>datasets/clean/penguins_clean.csv)]
    F --> G[PySpark<br/>schema, filter, sort, cache]
    G -->|JSON partitionBy species| H[(HDFS<br/>spark/output/penguins)]
```

## Repository structure

```
.
├── data/                 penguins.csv (source dataset)
├── hdfs/                 Section 1: HDFS CLI script
├── hive/                 Section 2: HiveQL (database, table, analysis)
├── notebooks/            Section 3: Jupyter notebook (executed, with outputs)
├── spark/                Section 4: PySpark application
├── logs/                 Real command transcripts from every task
├── screenshots/          Evidence for every practical step
├── docs/charts/          Analysis charts
├── report/               Assessment report (PDF + DOCX)
├── tools/                Helpers used to capture transcripts and render evidence
└── requirements.txt
```

## Sections

| # | Task | File |
|---|---|---|
| 1 | HDFS: `mkdir`, download, `put`, `ls` | [`hdfs/section1_hdfs_commands.sh`](hdfs/section1_hdfs_commands.sh) |
| 2 | Hive: `penguins_db`, `penguins_raw`, preview, counts, averages, missing values | [`hive/penguins.hql`](hive/penguins.hql) |
| 3 | WebHDFS + Pandas: inspect, clean, impute, add `body_mass_kg`, upload | [`notebooks/penguins_elt_webhdfs.ipynb`](notebooks/penguins_elt_webhdfs.ipynb) |
| 4 | PySpark: schema, select, filter, sort, cache, JSON partitioned by species | [`spark/penguins_spark.py`](spark/penguins_spark.py) |

## Key results

| Metric | Value |
|---|---|
| Records loaded | 344 (342 after cleaning) |
| Adelie by island (Biscoe / Dream / Torgersen) | 44 / 56 / 52 |
| Chinstrap (Dream) · Gentoo (Biscoe) | 68 · 124 |
| Avg body mass, g (Gentoo / Chinstrap / Adelie) | 5076.02 / 3733.09 / 3700.66 |
| Avg flipper length, mm (Gentoo / Chinstrap / Adelie) | 217.19 / 195.82 / 189.95 |
| Missing values (bill length / flipper / mass / sex) | 2 / 2 / 2 / 11 |
| Cleaning | 2 empty rows dropped, numeric gaps filled with species median, sex set to `unknown` |
| Spark output (body mass ≥ 4 kg) | 177 rows → `/user/maria_dev/spark/output/penguins/species=*` |

## Screenshots

**Section 1: HDFS listing**
![HDFS ls](screenshots/s1_t4_ls.png)

**Section 2: Hive species and island counts**
![Hive counts](screenshots/s2_t3a.png)

**Section 3: Cleaned file uploaded over WebHDFS**
![Clean upload](screenshots/s3_clean_hdfs.png)

**Section 4: Spark JSON output partitioned by species**
![Spark output](screenshots/s4_output_hdfs.png)

More in [`screenshots/`](screenshots/), full transcripts in [`logs/`](logs/).

## Charts

| Average by species | Species by island |
|---|---|
| ![](docs/charts/chart_avg_species.png) | ![](docs/charts/chart_species_island.png) |

## How to run

**Prerequisites:** Hadoop (HDFS + YARN), Hive with HiveServer2, Spark 3.x, Python 3 with `pip install -r requirements.txt`.

```bash
# Section 1: HDFS
bash hdfs/section1_hdfs_commands.sh

# Section 2: Hive
hdfs dfs -mkdir -p /user/maria_dev/hive_stage
hdfs dfs -cp -f /user/maria_dev/datasets/penguins.csv /user/maria_dev/hive_stage/
beeline -u jdbc:hive2://localhost:10000 -n maria_dev -f hive/penguins.hql

# Section 3: Jupyter (Run All)
jupyter notebook notebooks/penguins_elt_webhdfs.ipynb

# Section 4: Spark
spark-submit --master yarn spark/penguins_spark.py     # or --master local[2]
```

> **HDP Sandbox:** set `WEBHDFS_URL = "http://sandbox-hdp.hortonworks.com:50070"` in the notebook and `HDFS_NN = "hdfs://sandbox-hdp.hortonworks.com:8020"` in the Spark script.

## Environment used

Apache Hadoop 3.3.6 · Apache Hive 3.1.3 · Apache Spark 3.5.1 · OpenJDK 8 · Python 3.12 (pandas, hdfs) · single-node cluster, host `sandbox-hdp`, user `maria_dev`.

## Deliverables

- 📄 [Assessment report (PDF)](report/Hadoop_Penguins_Assessment_Report.pdf) · [DOCX](report/Hadoop_Penguins_Assessment_Report.docx)

## Dataset

Palmer Penguins by Dr. Kristen Gorman and Palmer Station LTER, via [allisonhorst/palmerpenguins](https://github.com/allisonhorst/palmerpenguins) (CC0).

## License

[MIT](LICENSE)
