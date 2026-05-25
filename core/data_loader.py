from io import StringIO

import pandas as pd

from data.sample_data import EDITABLE_SAMPLE_CSV, REQUIRED_COLUMNS

MAX_UPLOAD_BYTES = 1_000_000
MAX_ROWS = 5000


def clean_currency_column(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace("", "0")
        .astype(float)
    )


def parse_csv(uploaded_file=None) -> pd.DataFrame:
    if uploaded_file is not None and getattr(uploaded_file, "size", 0) > MAX_UPLOAD_BYTES:
        raise ValueError(f"Uploaded CSV is too large. Please upload a file under {MAX_UPLOAD_BYTES // 1000} KB.")

    df = pd.read_csv(uploaded_file) if uploaded_file is not None else pd.read_csv(StringIO(EDITABLE_SAMPLE_CSV))

    if len(df) > MAX_ROWS:
        raise ValueError(f"Uploaded CSV has too many rows. Please upload {MAX_ROWS:,} rows or fewer.")

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for column in ["Leads Issued", "Demos", "Sales"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    df["Revenue"] = clean_currency_column(df["Revenue"])
    df = df.dropna(subset=["Date"])

    numeric_columns = ["Leads Issued", "Demos", "Sales", "Revenue"]
    if (df[numeric_columns] < 0).any().any():
        raise ValueError("Uploaded CSV contains negative numeric values. Please correct the data and try again.")

    if df.empty:
        raise ValueError("The uploaded file did not contain usable dated rows after cleanup.")

    return df


def data_quality_warnings(df: pd.DataFrame) -> list[str]:
    warnings = []
    duplicate_count = df.duplicated().sum()
    if duplicate_count:
        warnings.append(f"{duplicate_count} duplicate row(s) detected.")
    if (df["Demos"] > df["Leads Issued"]).any():
        warnings.append("Some rows have more demos than leads issued.")
    if (df["Sales"] > df["Demos"]).any():
        warnings.append("Some rows have more sales than demos.")
    return warnings
