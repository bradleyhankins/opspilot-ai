from __future__ import annotations

import pandas as pd

MAX_UPLOAD_BYTES = 1_000_000
MAX_ROWS = 5_000
NUMERIC_COLUMNS = ["Leads Issued", "Demos", "Sales", "Revenue"]


def validate_uploaded_file(uploaded_file) -> list[str]:
    """Return user-friendly validation errors for uploaded CSV files."""
    errors: list[str] = []
    if uploaded_file is None:
        return errors

    size = getattr(uploaded_file, "size", None)
    if size is not None and size > MAX_UPLOAD_BYTES:
        errors.append("Uploaded CSV is too large for the public demo. Please keep files under 1 MB or use summarized sample data.")

    return errors


def validate_dataframe(df: pd.DataFrame) -> list[str]:
    """Return user-friendly validation errors for OpsPilot activity data."""
    errors: list[str] = []

    if len(df) > MAX_ROWS:
        errors.append(f"Uploaded CSV has {len(df):,} rows. Please keep public-demo uploads under {MAX_ROWS:,} rows.")

    for column in NUMERIC_COLUMNS:
        if column in df.columns and (pd.to_numeric(df[column], errors="coerce").fillna(0) < 0).any():
            errors.append(f"{column} contains negative values. Please remove or correct negative activity data before uploading.")

    if "Revenue" in df.columns:
        revenue = pd.to_numeric(df["Revenue"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False), errors="coerce").fillna(0)
        if (revenue > 1_000_000).any():
            errors.append("One or more Revenue rows are unusually high for the public demo. Please verify the CSV before continuing.")

    return errors
