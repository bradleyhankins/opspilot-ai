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

def generate_operations_diagnosis(demo_rate, close_rate, avg_sale, nsli, rep_summary, source_summary):
    """
    Generates a rules-based AI-style operations diagnosis.

    This keeps the app free and deployable without requiring an API key,
    while still translating sales data into practical manager actions.
    """

    diagnosis = {
        "primary_bottleneck": "",
        "likely_cause": "",
        "manager_action": "",
        "coaching_move": "",
        "roleplay": "",
        "priority_level": ""
    }

    if demo_rate < 0.60:
        diagnosis["primary_bottleneck"] = "Demo Rate"
        diagnosis["priority_level"] = "High"
        diagnosis["likely_cause"] = (
            "The team is not converting enough issued leads into completed demos. "
            "This usually points to weak appointment setting, poor confirmation process, "
            "low homeowner commitment, bad lead quality, or scheduling friction."
        )
        diagnosis["manager_action"] = (
            "Review the most recent issued leads that did not demo. Look for patterns by rep, "
            "lead source, appointment time, and confirmation process."
        )
        diagnosis["coaching_move"] = (
            "Coach reps on setting stronger expectations, confirming all decision-makers, "
            "building urgency before the appointment, and reducing no-show risk."
        )
        diagnosis["roleplay"] = (
            "Homeowner says: 'Just come out and give me a quick quote. I may not have much time.'"
        )

    elif close_rate < 0.35:
        diagnosis["primary_bottleneck"] = "Close Rate"
        diagnosis["priority_level"] = "High"
        diagnosis["likely_cause"] = (
            "The team is getting enough demos, but not converting enough of them into sales. "
            "This usually points to weak discovery, poor value build, price resistance, "
            "lack of urgency, or inconsistent closing confidence."
        )
        diagnosis["manager_action"] = (
            "Review the last several unsold demos and identify the most common objection. "
            "Use that pattern to build the next sales meeting around one specific closing skill."
        )
        diagnosis["coaching_move"] = (
            "Coach reps on deeper discovery, stronger problem awareness, financing confidence, "
            "value stacking, and direct same-day closing language."
        )
        diagnosis["roleplay"] = (
            "Homeowner says: 'We need to think about it and get a few more quotes.'"
        )

    elif avg_sale < 12000:
        diagnosis["primary_bottleneck"] = "Average Sale"
        diagnosis["priority_level"] = "Medium"
        diagnosis["likely_cause"] = (
            "The team is closing deals, but project size is lower than expected. "
            "This may indicate incomplete scopes, weak upgrade positioning, missed add-ons, "
            "or reps defaulting to the cheapest option."
        )
        diagnosis["manager_action"] = (
            "Audit recent sold jobs and compare the presented scope against the full opportunity. "
            "Look for missed upgrades, accessories, financing options, and scope completeness."
        )
        diagnosis["coaching_move"] = (
            "Coach reps on presenting good/better/best options, explaining long-term value, "
            "and confidently offering add-ons where they solve a real customer problem."
        )
        diagnosis["roleplay"] = (
            "Homeowner says: 'We just want the cheapest option that gets the job done.'"
        )

    elif nsli < 4000:
        diagnosis["primary_bottleneck"] = "Net Sales Per Lead Issued"
        diagnosis["priority_level"] = "Medium"
        diagnosis["likely_cause"] = (
            "The total revenue produced per issued lead is low. This can come from weak lead quality, "
            "poor rep assignment, low demo rate, low close rate, or smaller-than-expected job sizes."
        )
        diagnosis["manager_action"] = (
            "Compare NSLI by lead source and by rep. Shift attention toward the best-performing "
            "source and review whether low-performing sources need better qualification."
        )
        diagnosis["coaching_move"] = (
            "Coach the team on prioritizing high-intent opportunities, improving follow-up speed, "
            "and increasing conversion discipline on every issued lead."
        )
        diagnosis["roleplay"] = (
            "Homeowner says: 'I’m not sure if this is something we’re ready to do right now.'"
        )

    else:
        diagnosis["primary_bottleneck"] = "No Critical Bottleneck"
        diagnosis["priority_level"] = "Healthy"
        diagnosis["likely_cause"] = (
            "The current metrics are within a healthy operating range. The team appears to be generating demos, "
            "closing opportunities, and producing meaningful revenue per lead."
        )
        diagnosis["manager_action"] = (
            "Protect what is working. Study the top-performing rep and lead source, then document the behaviors "
            "that should become the team standard."
        )
        diagnosis["coaching_move"] = (
            "Use coaching time to reinforce winning behaviors, sharpen advanced objection handling, "
            "and build consistency across the team."
        )
        diagnosis["roleplay"] = (
            "Homeowner says: 'Everything sounds good, but I want to make sure we are making the right decision.'"
        )

    best_rep = rep_summary.sort_values("Revenue", ascending=False).iloc[0]
    weakest_rep = rep_summary.sort_values("NSLI", ascending=True).iloc[0]
    best_source = source_summary.sort_values("NSLI", ascending=False).iloc[0]
    weakest_source = source_summary.sort_values("NSLI", ascending=True).iloc[0]

    diagnosis["best_rep"] = best_rep["Rep"]
    diagnosis["weakest_rep"] = weakest_rep["Rep"]
    diagnosis["best_source"] = best_source["Lead Source"]
    diagnosis["weakest_source"] = weakest_source["Lead Source"]

    return diagnosis

def build_manager_report(
    total_leads,
    total_demos,
    total_sales,
    total_revenue,
    demo_rate,
    close_rate,
    avg_sale,
    nsli,
    diagnosis,
    best_rep,
    lowest_rep,
    best_source,
    weakest_source
):
    """
    Builds a downloadable manager report in Markdown format.
    """

    report = f"""
# OpsPilot AI Manager Report

## Executive Summary

The team generated **${total_revenue:,.0f}** from **{total_sales:,.0f} sales** on **{total_leads:,.0f} leads issued**.

## Core KPIs

| Metric | Result |
|---|---:|
| Leads Issued | {total_leads:,.0f} |
| Demos | {total_demos:,.0f} |
| Sales | {total_sales:,.0f} |
| Revenue | ${total_revenue:,.0f} |
| Demo Rate | {demo_rate:.1%} |
| Close Rate | {close_rate:.1%} |
| Average Sale | ${avg_sale:,.0f} |
| Net Sales Per Lead Issued | ${nsli:,.0f} |

## AI Operations Diagnosis

| Category | Result |
|---|---|
| Primary Bottleneck | {diagnosis["primary_bottleneck"]} |
| Priority Level | {diagnosis["priority_level"]} |
| Rep to Review | {diagnosis["weakest_rep"]} |
| Strongest Rep | {diagnosis["best_rep"]} |
| Strongest Lead Source | {diagnosis["best_source"]} |
| Lead Source to Review | {diagnosis["weakest_source"]} |

## Likely Cause

{diagnosis["likely_cause"]}

## Recommended Manager Action

{diagnosis["manager_action"]}

## Recommended Coaching Move

{diagnosis["coaching_move"]}

## Suggested Sales Meeting Roleplay

{diagnosis["roleplay"]}

## Manager Action Plan

1. Review unsold demos and assign follow-up actions.
2. Coach the rep needing review on the highest-impact bottleneck.
3. Protect or increase activity around the strongest lead source.
4. Audit the weakest lead source before spending more time or money there.
5. Use the next sales meeting to roleplay the most common objection or bottleneck.

## Weekly Sales Meeting Focus

- Recognize the top performer: {best_rep["Rep"]}
- Review the rep needing performance attention: {lowest_rep["Rep"]}
- Highlight strongest lead source: {best_source["Lead Source"]}
- Review weakest lead source: {weakest_source["Lead Source"]}
- Focus coaching around: {diagnosis["primary_bottleneck"]}

---

Generated by OpsPilot AI.
"""
    return report

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
st.header("Upload Sales Activity Data")

st.markdown("""
Use the sample data to explore the dashboard, or upload your own CSV file using the required format.
""")

with open("sample_data.csv", "r") as file:
    sample_csv = file.read()

st.download_button(
    label="Download Sample CSV Template",
    data=sample_csv,
    file_name="opspilot-sample-data.csv",
    mime="text/csv"
)

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

st.sidebar.title("OpsPilot AI")
st.sidebar.caption("Version 1.0 MVP")

st.sidebar.markdown("""
**Built by Bradley Hankins**

OpsPilot AI is a practical operations intelligence tool for field-sales and home-service teams.

It helps managers turn daily activity data into KPI visibility, coaching priorities, and manager-ready action plans.
""")

st.sidebar.divider()

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
# AI Operations Diagnosis
# -----------------------------

st.header("AI Operations Diagnosis")

diagnosis = generate_operations_diagnosis(
    demo_rate,
    close_rate,
    avg_sale,
    nsli,
    rep_summary,
    source_summary
)

diag_col1, diag_col2, diag_col3 = st.columns(3)

diag_col1.metric("Primary Bottleneck", diagnosis["primary_bottleneck"])
diag_col2.metric("Priority Level", diagnosis["priority_level"])
diag_col3.metric("Rep to Review", diagnosis["weakest_rep"])

st.markdown(f"""
### Diagnosis

**Likely Cause:**  
{diagnosis["likely_cause"]}

**Recommended Manager Action:**  
{diagnosis["manager_action"]}

**Recommended Coaching Move:**  
{diagnosis["coaching_move"]}

**Suggested Sales Meeting Roleplay:**  
_{diagnosis["roleplay"]}_

### Pattern Recognition

- Strongest revenue producer: **{diagnosis["best_rep"]}**
- Rep needing review by NSLI: **{diagnosis["weakest_rep"]}**
- Strongest lead source: **{diagnosis["best_source"]}**
- Lead source needing review: **{diagnosis["weakest_source"]}**
""")

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
# Downloadable Manager Report
# -----------------------------

st.header("Download Manager Report")

manager_report = build_manager_report(
    total_leads,
    total_demos,
    total_sales,
    total_revenue,
    demo_rate,
    close_rate,
    avg_sale,
    nsli,
    diagnosis,
    best_rep,
    lowest_rep,
    best_source,
    weakest_source
)

st.download_button(
    label="Download Manager Report",
    data=manager_report,
    file_name="opspilot-manager-report.md",
    mime="text/markdown"
)

with st.expander("How to use OpsPilot AI"):
    st.markdown("""
    1. Download the sample CSV template.
    2. Replace the sample rows with your own sales activity data.
    3. Upload the completed CSV file.
    4. Use the sidebar filters to analyze reps, lead sources, and date ranges.
    5. Review the KPI dashboard, AI Operations Diagnosis, Manager Brief, and Weekly Sales Meeting Agenda.
    6. Download the Manager Report for use in meetings or coaching sessions.

    Required CSV columns:

    - Date
    - Rep
    - Lead Source
    - Leads Issued
    - Demos
    - Sales
    - Revenue
    """)

st.info(
    "Privacy note: Uploaded CSV files are processed during the active app session and are not saved by this app."
)

# -----------------------------
# Raw data
# -----------------------------

# -----------------------------
# Consulting / Portfolio CTA
# -----------------------------

st.header("Built for Practical AI Operations Consulting")

st.markdown("""
OpsPilot AI is an example of how small and mid-sized businesses can use lightweight AI-assisted workflows
to improve visibility, coaching, reporting, and operational decision-making without needing enterprise-level software.

This project demonstrates:

- Sales operations analysis
- KPI dashboarding
- Workflow automation
- Manager reporting
- AI-style operational diagnosis
- Field-sales coaching support
- Practical business intelligence for home-service teams

Built by **Bradley Hankins** as part of an AI operations and workflow automation portfolio.
""")

with st.expander("View Raw Data"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
