import pandas as pd

from core.formatters import money, pct, safe_divide


def calculate_metrics(df: pd.DataFrame) -> dict:
    total_leads = df["Leads Issued"].sum()
    total_demos = df["Demos"].sum()
    total_sales = df["Sales"].sum()
    total_revenue = df["Revenue"].sum()
    return {
        "total_leads": total_leads,
        "total_demos": total_demos,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "demo_rate": safe_divide(total_demos, total_leads),
        "close_rate": safe_divide(total_sales, total_demos),
        "avg_sale": safe_divide(total_revenue, total_sales),
        "nsli": safe_divide(total_revenue, total_leads),
    }


def build_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    summary = df.groupby(group_col, as_index=False).agg({"Leads Issued": "sum", "Demos": "sum", "Sales": "sum", "Revenue": "sum"})
    summary["Demo Rate"] = summary.apply(lambda row: safe_divide(row["Demos"], row["Leads Issued"]), axis=1)
    summary["Close Rate"] = summary.apply(lambda row: safe_divide(row["Sales"], row["Demos"]), axis=1)
    summary["Average Sale"] = summary.apply(lambda row: safe_divide(row["Revenue"], row["Sales"]), axis=1)
    summary["NSLI"] = summary.apply(lambda row: safe_divide(row["Revenue"], row["Leads Issued"]), axis=1)
    return summary


def build_trends(df: pd.DataFrame) -> pd.DataFrame:
    trends = df.groupby("Date", as_index=False).agg({"Leads Issued": "sum", "Demos": "sum", "Sales": "sum", "Revenue": "sum"}).sort_values("Date")
    trends["Demo Rate"] = trends.apply(lambda row: safe_divide(row["Demos"], row["Leads Issued"]), axis=1)
    trends["Close Rate"] = trends.apply(lambda row: safe_divide(row["Sales"], row["Demos"]), axis=1)
    trends["NSLI"] = trends.apply(lambda row: safe_divide(row["Revenue"], row["Leads Issued"]), axis=1)
    return trends


def format_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    formatted_df = df.copy()
    for column in ["Revenue", "Average Sale", "NSLI"]:
        formatted_df[column] = formatted_df[column].apply(money)
    for column in ["Demo Rate", "Close Rate"]:
        formatted_df[column] = formatted_df[column].apply(pct)
    return formatted_df


def compare_periods(trends: pd.DataFrame) -> dict:
    if len(trends) < 2:
        return {"label": "Not enough data", "revenue_change": 0, "demo_change": 0, "close_change": 0, "nsli_change": 0}
    midpoint = len(trends) // 2
    first = calculate_metrics(trends.iloc[:midpoint])
    second = calculate_metrics(trends.iloc[midpoint:])
    return {
        "label": "Second half vs. first half",
        "revenue_change": second["total_revenue"] - first["total_revenue"],
        "demo_change": second["demo_rate"] - first["demo_rate"],
        "close_change": second["close_rate"] - first["close_rate"],
        "nsli_change": second["nsli"] - first["nsli"],
    }
