"""Builds notebooks/penguins_elt_webhdfs.ipynb (Section 3)."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

nb.cells = [
md("""# Section 3 — ELT with WebHDFS `InsecureClient`
**Big Data with Hadoop · Palmer Penguins Assessment**

Connect to the Hadoop sandbox over **WebHDFS**, load `penguins.csv` from HDFS into Pandas, analyse structure and missing values, clean it, convert body mass to kilograms, and upload the result back to HDFS as `/user/maria_dev/datasets/clean/penguins_clean.csv`."""),
code("""# pip install hdfs pandas
import io
import pandas as pd
from hdfs import InsecureClient

# WebHDFS endpoint of the sandbox NameNode (HDP sandbox: http://sandbox-hdp.hortonworks.com:50070)
WEBHDFS_URL = "http://localhost:9870"
HDFS_USER   = "maria_dev"
RAW_PATH    = "/user/maria_dev/datasets/penguins.csv"
CLEAN_PATH  = "/user/maria_dev/datasets/clean/penguins_clean.csv"

client = InsecureClient(WEBHDFS_URL, user=HDFS_USER)
print("Connected to:", WEBHDFS_URL, "as", HDFS_USER)
print(client.list("/user/maria_dev/datasets"))"""),
md("## 1. Load `penguins.csv` from HDFS into a Pandas DataFrame"),
code("""status = client.status(RAW_PATH)
print(f"HDFS file size: {status['length']} bytes | replication: {status['replication']} | owner: {status['owner']}")

with client.read(RAW_PATH, encoding="utf-8") as reader:
    df = pd.read_csv(reader, na_values=["NA", ""])

df.head(10)"""),
md("## 2. Analyse structure"),
code("""print("Shape (rows, columns):", df.shape)
print()
df.info()"""),
code("df.describe(include='all').T"),
code("""print(df['species'].value_counts(), "\\n")
print(df['island'].value_counts(), "\\n")
print(df['sex'].value_counts(dropna=False))"""),
md("## 3. Missing values"),
code("""missing = pd.DataFrame({
    "missing_count": df.isna().sum(),
    "missing_pct":   (df.isna().mean() * 100).round(2)
})
missing"""),
code("""# Rows where every measurement is missing carry no information
measure_cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
df[df[measure_cols].isna().all(axis=1)]"""),
md("""## 4. Clean & preprocess
1. Drop rows where **all** body measurements are missing (2 rows).
2. Impute any remaining numeric gaps with the **species median**.
3. Normalise `sex` to lower case; fill missing sex with `"unknown"`.
4. Convert **body mass to kilograms** (`body_mass_kg = body_mass_g / 1000`).
5. Remove duplicates and enforce data types."""),
code("""clean = df.copy()
before = len(clean)

# 1. drop rows with no measurements at all
clean = clean.dropna(subset=measure_cols, how="all")

# 2. species-median imputation for numeric columns
for col in measure_cols:
    clean[col] = clean.groupby("species")[col].transform(lambda s: s.fillna(s.median()))

# 3. tidy sex
clean["sex"] = clean["sex"].str.strip().str.lower().fillna("unknown")

# 4. body mass in kilograms
clean["body_mass_kg"] = (clean["body_mass_g"] / 1000).round(3)

# 5. duplicates + dtypes
clean = clean.drop_duplicates()
clean["flipper_length_mm"] = clean["flipper_length_mm"].astype(float)
clean["year"] = clean["year"].astype(int)

clean = clean[["species", "island", "bill_length_mm", "bill_depth_mm",
               "flipper_length_mm", "body_mass_g", "body_mass_kg", "sex", "year"]]

print(f"Rows before: {before} | after: {len(clean)} | dropped: {before - len(clean)}")
print("\\nMissing values after cleaning:")
print(clean.isna().sum())
clean.head(10)"""),
code("""clean.groupby("species").agg(
    penguins=("species", "size"),
    avg_mass_kg=("body_mass_kg", "mean"),
    avg_flipper_mm=("flipper_length_mm", "mean")
).round(3)"""),
md("## 5. Upload cleaned dataset to HDFS"),
code("""client.makedirs("/user/maria_dev/datasets/clean")
csv_text = clean.to_csv(index=False)
client.write(CLEAN_PATH, data=csv_text, encoding="utf-8", overwrite=True)

print("Uploaded:", CLEAN_PATH)
print(client.list("/user/maria_dev/datasets/clean", status=True))"""),
code("""# Verify by reading it back from HDFS
with client.read(CLEAN_PATH, encoding="utf-8") as reader:
    check = pd.read_csv(reader)
print("Read back from HDFS:", check.shape)
check.head()"""),
]
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "notebooks/penguins_elt_webhdfs.ipynb")
print("notebook written")
