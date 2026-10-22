from pathlib import Path

import pandas as pd
import pytest

from src.penguins_clean import OUTPUT_COLS, clean_penguins, load_raw

DATA = Path(__file__).resolve().parents[1] / "data" / "penguins.csv"


@pytest.fixture(scope="module")
def raw():
    return load_raw(DATA)


@pytest.fixture(scope="module")
def clean(raw):
    return clean_penguins(raw)


def test_raw_shape(raw):
    assert raw.shape[0] == 344


def test_raw_species_counts(raw):
    counts = raw["species"].value_counts().to_dict()
    assert counts == {"Adelie": 152, "Gentoo": 124, "Chinstrap": 68}


def test_raw_missing_values(raw):
    assert raw["bill_length_mm"].isna().sum() == 2
    assert raw["flipper_length_mm"].isna().sum() == 2
    assert raw["body_mass_g"].isna().sum() == 2
    assert raw["sex"].isna().sum() == 11


def test_clean_drops_empty_rows(clean):
    assert len(clean) == 342


def test_clean_has_no_missing_values(clean):
    assert int(clean.isna().sum().sum()) == 0


def test_clean_columns(clean):
    assert list(clean.columns) == OUTPUT_COLS


def test_body_mass_kg(clean):
    assert (clean["body_mass_kg"] - clean["body_mass_g"] / 1000).abs().max() < 1e-3


def test_sex_values(clean):
    assert set(clean["sex"].unique()) <= {"male", "female", "unknown"}


def test_spark_filter_count(clean):
    # Mirrors the Spark filter body_mass_kg >= 4.0
    assert int((clean["body_mass_kg"] >= 4.0).sum()) == 177


def test_imputation_uses_species_median():
    df = pd.DataFrame({
        "species": ["A", "A", "A"], "island": ["X"] * 3,
        "bill_length_mm": [1.0, 3.0, None], "bill_depth_mm": [1.0, 1.0, 1.0],
        "flipper_length_mm": [10.0, 10.0, 10.0], "body_mass_g": [1000.0, 1000.0, 1000.0],
        "sex": ["MALE", None, "female"], "year": [2007, 2008, 2009],
    })
    out = clean_penguins(df)
    assert out.loc[2, "bill_length_mm"] == 2.0
    assert list(out["sex"]) == ["male", "unknown", "female"]
