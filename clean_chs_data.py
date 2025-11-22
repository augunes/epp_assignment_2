from pathlib import Path
import pandas as pd
import numpy as np

pd.options.mode.copy_on_write = True

def _to_pandas_missing(s: pd.Series) -> pd.Series:
    """Replace negative values with pandas missing codes."""
    # In this dataset, negative numbers indicate missing data
    return s.where(~(s < 0), other=pd.NA)

def clean_chs_data(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the CHS data by renaming variables and setting the index.

    This function selects the relevant columns, maps them to intelligible
    names, handles missing values, and creates a MultiIndex based on
    child identifier and year.
    """
    df = raw.copy()

    # Map BPI variables to sensible names
    bpi_map = {
        "bpiA": "bpi_antisocial_chs",
        "bpiB": "bpi_anxiety_chs",
        "bpiC": "bpi_headstrong_chs",
        "bpiD": "bpi_hyperactive_chs",
        "bpiE": "bpi_peer_chs",
    }

    # Clean BPI variables: convert special missings to NA
    for raw_name, clean_name in bpi_map.items():
        df[clean_name] = _to_pandas_missing(df[raw_name])

    # Clean momid and convert to nullable integer
    df["momid"] = df["momid"].astype("Int64")

    # Age can be integer (two-year bins)
    df["age"] = df["age"].astype("Int64")

    # Set index using nullable integers
    df["childid"] = df["childid"].astype("Int64")
    df["year"] = df["year"].astype("Int64")
    df = df.set_index(["childid", "year"])

    # Keep only relevant columns (plus momid and age)
    keep_cols = ["momid", "age"] + list(bpi_map.values())
    df = df[keep_cols]

    return df.sort_index()

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    bld_dir = project_root / "bld"


    chs_path = bld_dir / "chs_data.dta"
    
    if not chs_path.exists():
         chs_path = bld_dir / "original_data" / "chs_data.dta"

    if chs_path.exists():
        raw_chs = pd.read_stata(chs_path)
        clean_chs = clean_chs_data(raw_chs)

        out_path = bld_dir / "chs_clean.parquet"
        clean_chs.to_parquet(out_path)
        print(f"Success! Cleaned data saved to: {out_path}")
    else:
        print(f"Error: Could not find 'chs_data.dta' in {bld_dir}")
