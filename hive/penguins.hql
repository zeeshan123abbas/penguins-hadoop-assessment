-- =====================================================================
--  Section 2 - Hive Table and HiveQL
--  Big Data with Hadoop | Palmer Penguins Assessment
--  Run with:  beeline -u jdbc:hive2://localhost:10000 -n maria_dev -f hive/penguins.hql
--  (Before running:  hdfs dfs -mkdir -p /user/maria_dev/hive_stage
--                    hdfs dfs -cp -f /user/maria_dev/datasets/penguins.csv /user/maria_dev/hive_stage/ )
-- =====================================================================

-- 1. Database + table loaded from the CSV in HDFS
CREATE DATABASE IF NOT EXISTS penguins_db
COMMENT 'Palmer penguins wildlife research data';

USE penguins_db;

DROP TABLE IF EXISTS penguins_raw;

CREATE TABLE penguins_raw (
    species            STRING,
    island             STRING,
    bill_length_mm     DOUBLE,
    bill_depth_mm      DOUBLE,
    flipper_length_mm  INT,
    body_mass_g        INT,
    sex                STRING,
    year               INT
)
COMMENT 'Raw penguins measurements loaded from HDFS CSV'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
TBLPROPERTIES (
    'skip.header.line.count'   = '1',
    'serialization.null.format' = 'NA'
);

-- Load the CSV that lives in HDFS (a staging copy, so the original stays in /datasets)
LOAD DATA INPATH '/user/maria_dev/hive_stage/penguins.csv'
OVERWRITE INTO TABLE penguins_raw;

DESCRIBE penguins_raw;

-- 2. Preview
SELECT * FROM penguins_raw LIMIT 10;

SELECT COUNT(*) AS total_records FROM penguins_raw;

-- 3a. Count records for each penguin species and island
SELECT species,
       island,
       COUNT(*) AS num_records
FROM   penguins_raw
GROUP  BY species, island
ORDER  BY species, island;

-- 3b. Average body mass and average flipper length for each species
SELECT species,
       ROUND(AVG(body_mass_g), 2)       AS avg_body_mass_g,
       ROUND(AVG(flipper_length_mm), 2) AS avg_flipper_length_mm
FROM   penguins_raw
GROUP  BY species
ORDER  BY avg_body_mass_g DESC;

-- 3c. Count missing values in bill_length_mm, flipper_length_mm, body_mass_g and sex
SELECT SUM(CASE WHEN bill_length_mm    IS NULL THEN 1 ELSE 0 END) AS missing_bill_length_mm,
       SUM(CASE WHEN flipper_length_mm IS NULL THEN 1 ELSE 0 END) AS missing_flipper_length_mm,
       SUM(CASE WHEN body_mass_g       IS NULL THEN 1 ELSE 0 END) AS missing_body_mass_g,
       SUM(CASE WHEN sex IS NULL OR TRIM(sex) = '' THEN 1 ELSE 0 END) AS missing_sex
FROM   penguins_raw;
