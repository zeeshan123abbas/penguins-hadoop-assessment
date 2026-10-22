"""Reusable cleaning logic for the Palmer Penguins ELT step (Section 3).

The notebook performs the same steps interactively; this module makes them
importable and unit-testable.
"""
from __future__ import annotations

import pandas as pd

MEASURE_COLS = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
OUTPUT_COLS = ["species", "island", "bill_length_mm", "bill_depth_mm",
               "flipper_length_mm", "body_mass_g", "body_mass_kg", "sex", "year"]


def clean_penguins(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the raw penguins DataFrame.

    1. Drop rows where every body measurement is missing.
    2. Impute remaining numeric gaps with the species median.
    3. Normalise ``sex`` to lower case and fill missing values with ``"unknown"``.
    4. Add ``body_mass_kg`` (grams / 1000, rounded to 3 decimals).
    5. Drop duplicates and enforce column order and types.
    """
    clean = df.copy()
    clean = clean.dropna(subset=MEASURE_COLS, how="all")
    for col in MEASURE_COLS:
        clean[col] = clean.groupby("species")[col].transform(lambda s: s.fillna(s.median()))
    clean["sex"] = clean["sex"].astype("string").str.strip().str.lower().fillna("unknown")
    clean["body_mass_kg"] = (clean["body_mass_g"] / 1000).round(3)
    clean = clean.drop_duplicates()
    clean["flipper_length_mm"] = clean["flipper_length_mm"].astype(float)
    clean["year"] = clean["year"].astype(int)
    return clean[OUTPUT_COLS].reset_index(drop=True)


def load_raw(path: str) -> pd.DataFrame:
    """Read the raw CSV, treating ``NA`` and empty strings as missing."""
    return pd.read_csv(path, na_values=["NA", ""])


if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "data/penguins.csv"
    out = clean_penguins(load_raw(src))
    print(f"{len(out)} rows, {int(out.isna().sum().sum())} missing values")
