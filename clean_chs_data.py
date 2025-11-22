from pathlib import Path
import pandas as pd


def _clean_bpi(series: pd.Series) -> pd.Series:
    """Helper: convert special missing codes (negative values) to pandas NA."""
    cleaned = series.copy()
    cleaned = cleaned.mask(cleaned < 0)
    return cleaned


def clean_chs_data(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the CHS dataset and return a new DataFrame
    with cleaned BPI variables, momid, age,
    and a MultiIndex [childid, year].
    """
    df = raw.copy()

    # Mapping raw → sensible names
    mapping = {
        "bpiA": "bpi_antisocial_chs",
        "bpiB": "bpi_anxiety_chs",
        "bpiC": "bpi_headstrong_chs",
        "bpiD": "bpi_hyperactive_chs",
        "bpiE": "bpi_peer_chs",
    }

    clean = pd.DataFrame()

    # Clean BPI columns
    for raw_name, new_name in mapping.items():
        clean[new_name] = _clean_bpi(df[raw_name])

    # momid with a good dtype (nullable integer)
    clean["momid"] = df["momid"].astype("Int64")

    # age (integer bins)
    clean["age"] = df["age"].astype("Int64")

    # Index variables with suitable dtypes
    clean["childid"] = df["childid"].astype("Int64")
    clean["year"] = df["year"].astype("Int64")

    # Set MultiIndex
    clean = clean.set_index(["childid", "year"])

    return clean


if __name__ == "__main__":
    # project root is the folder where this script sits
    project_root = Path(__file__).resolve().parent

    # load raw dataset from bld (created by unzip.py)
    raw_path = project_root / "bld" / "chs_data.dta"
    raw_df = pd.read_stata(raw_path)

    # clean the data
    clean_df = clean_chs_data(raw_df)

    # save clean dataset (generated → stays in bld, ignored by git)
    out_path = project_root / "bld" / "chs_data_clean.csv"
    clean_df.to_csv(out_path)
