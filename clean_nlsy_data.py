from pathlib import Path
import pandas as pd
from pandas.api.types import CategoricalDtype

pd.options.mode.copy_on_write = True

# Ordered categorical type for BPI items
_BPI_CAT = CategoricalDtype(
    categories=["not true", "sometimes true", "often true"],
    ordered=True,
)


def _to_ordered_bpi_item(series: pd.Series) -> pd.Series:
    """Convert a raw BPI item to an ordered categorical with 3 levels."""
    s = series.copy()

    # negative numeric codes indicate missing → set to NA
    s = s.mask(s < 0)

    # direct mapping for the codes/labels we see in the data
    mapping = {
        # numeric codes (in case some items use them)
        0: "not true",
        1: "sometimes true",
        2: "often true",
        3: "often true",
        # string labels (as in BEHAVIOR_PROBLEMS_INDEX.dta)
        "NOT TRUE": "not true",
        "SOMETIMES TRUE": "sometimes true",
        "OFTEN TRUE": "often true",
    }

    s = s.map(mapping)
    return s.astype(_BPI_CAT)


def _subscale_score(items: pd.DataFrame) -> pd.Series:
    """Convert BPI items to 0/1 and average across columns."""
    numeric = items.replace(
        {
            "not true": 0,
            "sometimes true": 1,
            "often true": 1,
        }
    ).astype("Float64")
    return numeric.mean(axis=1)


def manage_nlsy_data(raw, info):
    pass


def _clean_one_wave(raw: pd.DataFrame, year: int, info: pd.DataFrame) -> pd.DataFrame:
    """
    Clean NLSY BPI data for a single survey wave.

    Parameters
    ----------
    raw : pandas.DataFrame
        Full raw NLSY dataset (like BEHAVIOR_PROBLEMS_INDEX.dta).
    year : int
        Survey year to extract and clean (even years, 1986–2010).
    info : pandas.DataFrame
        Metadata from bpi_variable_info.csv. Must contain:
        - 'nlsy_name' : raw NLSY variable name (e.g., C0564000)
        - 'readable_name' : sensible variable name (e.g., anxiety_mood)
        - 'survey_year' : year as a string (e.g., '1986')
        plus the invariant variables (childid, momid, etc.).

    Returns
    -------
    pandas.DataFrame
        Cleaned data for that wave with index ['childid', 'year'], containing:
        - one column per BPI item (ordered categorical)
        - subscale scores for antisocial, anxiety, headstrong,
          hyperactive, peer, and dependence.
    """
    # never modify the original raw DataFrame
    df = raw.copy()

    # we do NOT subset rows by year (each row is a child);
    # instead, we select the columns that belong to this survey year
    year_str = str(year)

    # metadata for this wave
    info_wave = info[info["survey_year"] == year_str].copy()

    # identify BPI items using the prefix of readable_name
    # prefixes correspond to subscales:
    # antisocial_, anxiety_, headstrong_, hyperactive_, peer_, dependent_
    prefix_to_subscale = {
        "antisocial": "antisocial",
        "anxiety": "anxiety",
        "headstrong": "headstrong",
        "hyperactive": "hyperactive",
        "peer": "peer",
        "dependent": "dependence",  # 'dependent_' items form the dependence subscale
    }

    # extract prefix (part before the first "_")
    info_wave["prefix"] = info_wave["readable_name"].str.split("_", n=1).str[0]

    # keep only rows that correspond to BPI items
    bpi_info = info_wave[info_wave["prefix"].isin(prefix_to_subscale.keys())].copy()

    # DataFrame to store cleaned variables, same rows as raw
    clean = pd.DataFrame(index=df.index)

    # 1) Clean each BPI item using the metadata
    for _, row in bpi_info.iterrows():
        raw_name = row["nlsy_name"]
        target_name = row["readable_name"]

        if raw_name not in df.columns:
            # some items may be absent in some waves; skip them
            continue

        clean[target_name] = _to_ordered_bpi_item(df[raw_name])

    # 2) Compute subscale scores
    required_subscales = ["antisocial", "anxiety", "headstrong",
                          "hyperactive", "peer", "dependence"]

    # map prefixes to the canonical subscale names
    bpi_info["subscale"] = bpi_info["prefix"].map(prefix_to_subscale)

    for sub in required_subscales:
        item_names = bpi_info.loc[bpi_info["subscale"] == sub, "readable_name"].tolist()
        item_names = [name for name in item_names if name in clean.columns]

        if not item_names:
            continue  # no items for this subscale in this wave

        sub_items = clean[item_names]
        score_name = f"bpi_{sub}_nlsy"
        clean[score_name] = _subscale_score(sub_items)

    # 3) Add childid and year, and set index to [childid, year]
    # childid column is defined in info as invariant with readable_name == 'childid'
    childid_row = info[info["readable_name"] == "childid"].iloc[0]
    childid_col = childid_row["nlsy_name"]

    clean["childid"] = df[childid_col].astype("Int64")
    clean["year"] = pd.Series(year, index=clean.index, dtype="Int64")

    clean = clean.set_index(["childid", "year"]).sort_index()

    return clean


if __name__ == "__main__":
    # load the raw dataset
    # load the info
    # call the cleaning function
    # save the clean dataset in the bld folder
    pass
