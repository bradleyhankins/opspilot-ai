import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="OpsPilot AI",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Helper functions
# -----------------------------

def money(value):
    return f"${value:,.0f}"

def pct(value):
    return f"{value:.1%}"

def safe_divide(numerator, denominator):
    return numerator / denominator if denominator else 0

def clean_currency_column(series):
    return (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace("", "0")
        .astype(float)
    )

def build_summary(df, group_col):
    summary = df.groupby(group_col, as_index=False).agg({
        "Leads Issued": "sum",
        "Demos": "sum",
        "Sales": "sum",
        "Revenue": "sum"
    })

    summary["Demo Rate"] = summary.apply(
        lambda row: safe_divide(row["Demos"], row["Leads Issued"]),
        axis=1
    )
    summary["Close Rate"] = summary.apply(
        lambda row: safe_divide(row["Sales"], row["Demos"]),
        axis=1
    )
    summary["Average Sale"] = summary.apply(
        lambda row: safe_divide(row["Revenue"], row["Sales"]),
        axis=1
    )
    summary["NSLI"] = summary.apply(
        lambda row: safe_divide(row["Revenue"], row["Leads Issued"]),
        axis=1
    )
    return summary

def format_summary_table(df):
    formatted = df.copy()
    for col in ["Revenue", "Average Sale", "NSLI"]:
        if col in formatted.columns:
            formatted[col] = formatted[col].apply(money)
    for col in ["Demo Rate", "Close Rate"]:
        if col in formatted.columns:
            formatted[col] = formatted[col].apply(pct)
    return formatted

# -----------------------------
# Header
# -----------------------------

st.title("📊 OpsPilot AI")
st.subheader("Operations intelligence for field-sales and home-service teams")

st.markdown("""
OpsPilot AI turns daily sales activity into KPI visibility, rep performance insights,
lead source analysis, coaching priorities, and manager-ready action plans.
""")

# -----------------------------
# Data loading
# -----------------------------

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("sample_data.csv")

required_columns = ["Date", "Rep", "Lead Source", "Leads Issued", "Demos", "Sales", "Revenue"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

for col in ["Leads Issued", "Demos", "Sales"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["Revenue"] = clean_currency_column(df["Revenue"])

# -----------------------------
# Sidebar filters
# -----------------------------

st.sidebar.header("Filters")

rep_options = sorted(df["Rep"].dropna().unique())
source_options = sorted(df["Lead Source"].dropna().unique())

selected_reps = st.sidebar.multiselect("Rep", rep_options, default=rep_options)
selected_sources = st.sidebar.multiselect("Lead Source", source_options, default=source_options)

min_date = df["Date"].min()
max_date = df["Date"].max()

if pd.notna(min_date) and pd.notna(max_date):
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date.date(), max_date.date())
    )
else:
    date_range = None

filtered_df = df[
    df["Rep"].isin(selected_reps) &
    df["Lead Source"].isin(selected_sources)
]

if date_range and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date) &
        (filtered_df["Date"] <= end_date)
    ]

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# -----------------------------
# KPI calculations
# -----------------------------

total_leads = filtered_df["Leads Issued"].sum()
total_demos = filtered_df["Demos"].sum()
total_sales = filtered_df["Sales"].sum()
total_revenue = filtered_df["Revenue"].sum()

demo_rate = safe_divide(total_demos, total_leads)
close_rate = safe_divide(total_sales, total_demos)
avg_sale = safe_divide(total_revenue, total_sales)
nsli = safe_divide(total_revenue, total_leads)

st.divider()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Leads Issued", f"{total_leads:,.0f}")
col2.metric("Demos", f"{total_demos:,.0f}", f"{pct(demo_rate)} demo rate")
col3.metric("Sales", f"{total_sales:,.0f}", f"{pct(close_rate)} close rate")
col4.metric("Revenue", money(total_revenue))
col5.metric("NSLI", money(nsli))

# -----------------------------
# Health flags
# -----------------------------

st.header("Operational Health")

flags = []

if demo_rate < 0.60:
    flags.append(("Demo Rate Risk", "Demo rate is below 60%. Review appointment quality, confirmation process, and lead assignment."))
else:
    flags.append(("Demo Rate Healthy", "Demo rate is at or above 60%. The team is getting a solid percentage of issued leads to presentation."))

if close_rate < 0.35:
    flags.append(("Close Rate Risk", "Close rate is below 35%. Review presentation quality, financing confidence, price objections, and same-day close strategy."))
else:
    flags.append(("Close Rate Healthy", "Close rate is at or above 35%. Sales execution appears productive."))

if avg_sale < 12000:
    flags.append(("Average Sale Watch", "Average sale is under $12,000. Review product mix, financing options, add-ons, and scope completeness."))
else:
    flags.append(("Average Sale Healthy", "Average sale is strong enough to support premium home-service revenue goals."))

if nsli < 4000:
    flags.append(("NSLI Watch", "Net sales per lead issued is under $4,000. Review lead source quality and rep assignment."))
else:
    flags.append(("NSLI Healthy", "Net sales per lead issued is strong. Current lead flow is producing meaningful revenue."))

flag_cols = st.columns(2)

for index, (title, description) in enumerate(flags):
    with flag_cols[index % 2]:
        st.info(f"**{title}**\n\n{description}")

# -----------------------------
# Rep performance
# -----------------------------

st.header("Rep Performance")

rep_summary = build_summary(filtered_df, "Rep")
rep_summary = rep_summary.sort_values("Revenue", ascending=False)

st.dataframe(
    format_summary_table(rep_summary),
    use_container_width=True,
    hide_index=True
)

st.bar_chart(rep_summary.set_index("Rep")["Revenue"])

# -----------------------------
# Lead source performance
# -----------------------------

st.header("Lead Source Performance")

source_summary = build_summary(filtered_df, "Lead Source")
source_summary = source_summary.sort_values("NSLI", ascending=False)

st.dataframe(
    format_summary_table(source_summary),
    use_container_width=True,
    hide_index=True
)

st.bar_chart(source_summary.set_index("Lead Source")["NSLI"])

# -----------------------------
# Coaching opportunities
# -----------------------------

st.header("Coaching Opportunities")

coaching_notes = []

for _, row in rep_summary.iterrows():
    rep = row["Rep"]

    if row["Leads Issued"] < 5:
        coaching_notes.append(f"**{rep}:** Needs more lead volume before performance can be fairly judged.")

    if row["Demo Rate"] < 0.60 and row["Leads Issued"] >= 5:
        coaching_notes.append(f"**{rep}:** Demo rate is low. Coach appointment setting, confirmation, and homeowner commitment.")

    if row["Close Rate"] < 0.35 and row["Demos"] >= 3:
        coaching_notes.append(f"**{rep}:** Close rate is low. Coach discovery, value build, urgency, financing, and objection handling.")

    if row["Average Sale"] < 12000 and row["Sales"] >= 1:
        coaching_notes.append(f"**{rep}:** Average sale is low. Review scope completeness, add-ons, and product positioning.")

if coaching_notes:
    for note in coaching_notes:
        st.markdown(f"- {note}")
else:
    st.success("No major coaching flags found in the current filtered data.")

# -----------------------------
# Manager Brief
# -----------------------------

st.header("Manager Brief")

best_rep = rep_summary.sort_values("Revenue", ascending=False).iloc[0]
lowest_rep = rep_summary.sort_values("NSLI", ascending=True).iloc[0]
best_source = source_summary.sort_values("NSLI", ascending=False).iloc[0]
weakest_source = source_summary.sort_values("NSLI", ascending=True).iloc[0]

brief = f"""
### Executive Summary

The team generated **{money(total_revenue)}** from **{total_sales:,.0f} sales** on **{total_leads:,.0f} leads issued**.

Core performance:
- Demo Rate: **{pct(demo_rate)}**
- Close Rate: **{pct(close_rate)}**
- Average Sale: **{money(avg_sale)}**
- Net Sales Per Lead Issued: **{money(nsli)}**

### Top Performer

**{best_rep['Rep']}** is leading revenue production with **{money(best_rep['Revenue'])}**.

### Lead Source Insight

The strongest lead source by NSLI is **{best_source['Lead Source']}** at **{money(best_source['NSLI'])}** per lead issued.

The weakest lead source by NSLI is **{weakest_source['Lead Source']}** at **{money(weakest_source['NSLI'])}** per lead issued.

### Recommended Manager Action Plan

1. Review unsold demos and assign same-day follow-up tasks.
2. Coach the lowest NSLI rep, **{lowest_rep['Rep']}**, on the highest-impact bottleneck.
3. Protect or increase activity around **{best_source['Lead Source']}** if capacity allows.
4. Audit **{weakest_source['Lead Source']}** before spending more time or money there.
5. Use the next sales meeting to focus on one constraint: demo rate, close rate, average sale, or lead quality.
"""

st.markdown(brief)

# -----------------------------
# Meeting agenda
# -----------------------------

st.header("Auto-Generated Weekly Sales Meeting Agenda")

agenda = f"""
### 1. Wins
- Recognize **{best_rep['Rep']}** for leading total revenue.
- Highlight the best-performing source: **{best_source['Lead Source']}**.

### 2. Numbers in Focus
- Leads Issued: **{total_leads:,.0f}**
- Demos: **{total_demos:,.0f}**
- Sales: **{total_sales:,.0f}**
- Revenue: **{money(total_revenue)}**
- Demo Rate: **{pct(demo_rate)}**
- Close Rate: **{pct(close_rate)}**
- NSLI: **{money(nsli)}**

### 3. Bottleneck Discussion
- Is the biggest issue lead volume, demo rate, close rate, average sale, or lead source quality?

### 4. Coaching Focus
- Review rep-specific coaching opportunities from the dashboard.
- Pick one roleplay scenario based on the weakest metric.

### 5. Action Commitments
- Each rep commits to one measurable action before the next meeting.
"""

st.markdown(agenda)

# -----------------------------
# Raw data
# -----------------------------

with st.expander("View Raw Data"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
