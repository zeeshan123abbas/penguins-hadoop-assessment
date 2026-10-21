-- Section 2: Hive table and HiveQL

-- 1. Create database and external table on the CSV in HDFS
CREATE DATABASE IF NOT EXISTS penguins_db;
USE penguins_db;

CREATE EXTERNAL TABLE IF NOT EXISTS penguins_raw (
  species STRING,
  island STRING,
  bill_length_mm DOUBLE,
  bill_depth_mm DOUBLE,
  flipper_length_mm INT,
  body_mass_g INT,
  sex STRING,
  year INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/maria_dev/datasets/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 2. Preview data
SELECT * FROM penguins_raw LIMIT 10;

-- 3a. Count records for each species and island
SELECT species, island, COUNT(*) AS total
FROM penguins_raw
GROUP BY species, island;

-- 3b. Average body mass and flipper length per species
SELECT species,
       AVG(body_mass_g) AS avg_body_mass,
       AVG(flipper_length_mm) AS avg_flipper_length
FROM penguins_raw
GROUP BY species;

-- 3c. Missing values count
SELECT
  SUM(CASE WHEN bill_length_mm IS NULL THEN 1 ELSE 0 END) AS missing_bill_length,
  SUM(CASE WHEN flipper_length_mm IS NULL THEN 1 ELSE 0 END) AS missing_flipper_length,
  SUM(CASE WHEN body_mass_g IS NULL THEN 1 ELSE 0 END) AS missing_body_mass,
  SUM(CASE WHEN sex = 'NA' OR sex IS NULL THEN 1 ELSE 0 END) AS missing_sex
FROM penguins_raw;
