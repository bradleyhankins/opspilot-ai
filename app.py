import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="OpsPilot AI",
    page_icon="📊",
    layout="wide",
)

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

REQUIRED_COLUMNS = [
    "Date",
    "Rep",
    "Lead Source",
    "Leads Issued",
    "Demos",
    "Sales",
    "Revenue",
]

SAMPLE_TEMPLATE = """Date,Rep,Lead Source,Leads Issued,Demos,Sales,Revenue
2026-01-01,Alex Carter,Website,10,7,3,42000
2026-01-01,Jordan Lee,Referral,8,6,3,39000
2026-01-02,Taylor Brooks,Canvassing,12,6,2,24000
2026-01-02,Alex Carter,Partner Lead,6,5,2,30000
2026-01-03,Jordan Lee,Website,9,7,2,28000
"""

# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 1.35rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 1.8rem 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #334155 100%);
        color: #ffffff;
        box-shadow: 0 18px 36px rgba(17,24,39,.18);
        margin-bottom: 1rem;
    }

    .eyebrow {
        text-transform: uppercase;
        letter-spacing: .13em;
        font-size: .75rem;
        font-weight: 800;
        color: #93c5fd;
        margin-bottom: .65rem;
    }

    .hero-title {
        font-size: 2.2rem;
        line-height: 1.1;
        font-weight: 850;
        margin-bottom: .65rem;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        line-height: 1.6;
        color: #e5e7eb;
        max-width: 900px;
    }

    .section-title {
        margin-top: 1.25rem;
        margin-bottom: .55rem;
        font-size: 1.4rem;
        font-weight: 850;
        color: #111827;
    }

    .section-lede {
        color: #4b5563;
        line-height: 1.6;
        margin-bottom: 1rem;
        max-width: 940px;
    }

    .kpi-card,
    .insight-card,
    .brief-card,
    .risk-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        box-shadow: 0 8px 20px rgba(15,23,42,.055);
    }

    .kpi-card {
        height: 138px;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    .kpi-label {
        color: #6b7280;
        font-size: .78rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .05em;
        margin-bottom: .5rem;
    }

    .kpi-value {
        color: #111827;
        font-size: 1.55rem;
        line-height: 1.15;
        font-weight: 900;
        overflow-wrap: break-word;
    }

    .kpi-target {
        margin-top: .55rem;
        color: #64748b;
        font-size: .85rem;
        line-height: 1.35;
    }

    .insight-card,
    .brief-card,
    .risk-card {
        padding: 1.15rem;
        margin-bottom: .8rem;
    }

    .insight-card h3,
    .brief-card h3,
    .risk-card h3 {
        font-size: 1.05rem;
        font-weight: 850;
        color: #111827;
        margin-bottom: .4rem;
    }

    .insight-card p,
    .brief-card p,
    .risk-card p,
    .insight-card li,
    .brief-card li,
    .risk-card li {
        color: #4b5563;
        line-height: 1.52;
        font-size: .93rem;
    }

    .risk-high { border-left: 5px solid #dc2626; }
    .risk-medium { border-left: 5px solid #f59e0b; }
    .risk-healthy { border-left: 5px solid #059669; }

    .status-pill {
        display: inline-block;
        padding: .25rem .6rem;
        border-radius: 999px;
        font-weight: 850;
        font-size: .78rem;
        margin-bottom: .5rem;
    }

    .status-high { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .status-medium { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .status-healthy { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }

    .note-box {
        padding: .9rem 1rem;
        border-radius: 14px;
        background: #f8fafc;
        color: #334155;
        border: 1px solid #e2e8f0;
        font-weight: 650;
        margin: .9rem 0;
        font-size: .92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def money(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0


def clean_currency_column(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace("", "0")
        .astype(float)
    )


def load_data(uploaded_file) -> pd.DataFrame:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        try:
            df = pd.read_csv("sample_data.csv")
        except FileNotFoundError:
            from io import StringIO
            df = pd.read_csv(StringIO(SAMPLE_TEMPLATE))

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        st.stop()

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for column in ["Leads Issued", "Demos", "Sales"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    df["Revenue"] = clean_currency_column(df["Revenue"])
    return df.dropna(subset=["Date"])


def build_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    summary = df.groupby(group_col, as_index=False).agg(
        {
            "Leads Issued": "sum",
            "Demos": "sum",
            "Sales": "sum",
            "Revenue": "sum",
        }
    )

    summary["Demo Rate"] = summary.apply(lambda row: safe_divide(row["Demos"], row["Leads Issued"]), axis=1)
    summary["Close Rate"] = summary.apply(lambda row: safe_divide(row["Sales"], row["Demos"]), axis=1)
    summary["Average Sale"] = summary.apply(lambda row: safe_divide(row["Revenue"], row["Sales"]), axis=1)
    summary["NSLI"] = summary.apply(lambda row: safe_divide(row["Revenue"], row["Leads Issued"]), axis=1)
    return summary


def format_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    formatted = df.copy()
    for column in ["Revenue", "Average Sale", "NSLI"]:
        formatted[column] = formatted[column].apply(money)
    for column in ["Demo Rate", "Close Rate"]:
        formatted[column] = formatted[column].apply(pct)
    return formatted


def evaluate_metric(value: float, target: float, metric_name: str) -> tuple[str, str, str]:
    if value >= target:
        return "Healthy", "status-healthy", f"{metric_name} is meeting or exceeding the target."
    if value >= target * 0.85:
        return "Watch", "status-medium", f"{metric_name} is close to target but should be watched."
    return "Risk", "status-high", f"{metric_name} is materially below target and needs manager attention."


def kpi_card(label: str, value: str, target: str | None = None) -> None:
    target_html = f'<div class="kpi-target">Target: {target}</div>' if target else ""
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{target_html}</div>',
        unsafe_allow_html=True,
    )


def risk_card(title: str, status: str, status_class: str, description: str) -> None:
    card_class = {
        "status-high": "risk-high",
        "status-medium": "risk-medium",
        "status-healthy": "risk-healthy",
    }.get(status_class, "risk-medium")

    st.markdown(
        f"""
        <div class="risk-card {card_class}">
            <span class="status-pill {status_class}">{status}</span>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def generate_diagnosis(metrics: dict, targets: dict, rep_summary: pd.DataFrame, source_summary: pd.DataFrame) -> dict:
    checks = [
        ("Demo Rate", metrics["demo_rate"], targets["demo_rate"]),
        ("Close Rate", metrics["close_rate"], targets["close_rate"]),
        ("Average Sale", metrics["avg_sale"], targets["avg_sale"]),
        ("NSLI", metrics["nsli"], targets["nsli"]),
    ]

    gaps = []
    for name, value, target in checks:
        gap = safe_divide(target - value, target)
        gaps.append((name, gap, value, target))

    primary_name, primary_gap, primary_value, primary_target = max(gaps, key=lambda item: item[1])

    best_rep = rep_summary.sort_values("Revenue", ascending=False).iloc[0]
    review_rep = rep_summary.sort_values("NSLI", ascending=True).iloc[0]
    best_source = source_summary.sort_values("NSLI", ascending=False).iloc[0]
    review_source = source_summary.sort_values("NSLI", ascending=True).iloc[0]

    if primary_gap <= 0:
        priority = "Healthy"
        likely_cause = "The selected data is meeting the configured targets. The main opportunity is to protect what is working and standardize the behaviors behind the strongest results."
        manager_action = "Study the top rep and strongest lead source, then document the process that should become the team standard."
        coaching_move = "Use coaching time for advanced skill sharpening rather than basic correction."
        roleplay = "Homeowner says: 'Everything sounds good, but I want to make sure we are making the right decision.'"
    elif primary_name == "Demo Rate":
        priority = "High" if primary_gap > 0.15 else "Medium"
        likely_cause = "The team is not converting enough issued leads into completed demos. This may point to weak appointment setting, poor confirmation, low homeowner commitment, scheduling friction, or lead quality issues."
        manager_action = "Review issued leads that did not demo. Look for patterns by rep, lead source, appointment window, and confirmation process."
        coaching_move = "Coach reps on expectation setting, decision-maker confirmation, urgency, and reducing no-show risk."
        roleplay = "Homeowner says: 'Just come out and give me a quick quote. I may not have much time.'"
    elif primary_name == "Close Rate":
        priority = "High" if primary_gap > 0.15 else "Medium"
        likely_cause = "The team is getting demos but not converting enough into sales. This may point to weak discovery, poor value build, price resistance, lack of urgency, or inconsistent closing language."
        manager_action = "Review recent unsold demos and identify the most common objection. Build the next meeting around that single closing skill."
        coaching_move = "Coach reps on discovery, value stacking, financing confidence, urgency, and direct commitment language."
        roleplay = "Homeowner says: 'We need to think about it and get a few more quotes.'"
    elif primary_name == "Average Sale":
        priority = "Medium"
        likely_cause = "The team is closing work, but project size is below target. This may indicate incomplete scopes, weak upgrade positioning, missed add-ons, or reps defaulting to the lowest option."
        manager_action = "Audit recent sold jobs and compare the presented scope against the full opportunity. Look for missed upgrades, add-ons, and scope completeness."
        coaching_move = "Coach reps on good/better/best options, long-term value, and add-ons that solve real customer problems."
        roleplay = "Homeowner says: 'We just want the cheapest option that gets the job done.'"
    else:
        priority = "Medium"
        likely_cause = "Revenue per issued lead is below target. This may come from lead quality, rep assignment, low demo rate, low close rate, or smaller job size."
        manager_action = "Compare NSLI by rep and lead source. Shift attention toward the best-performing source and review whether low-performing sources need better qualification."
        coaching_move = "Coach the team on prioritizing high-intent opportunities, follow-up speed, and conversion discipline on every issued lead."
        roleplay = "Homeowner says: 'I’m not sure if this is something we’re ready to do right now.'"

    return {
        "primary_bottleneck": primary_name if primary_gap > 0 else "No Critical Bottleneck",
        "priority": priority,
        "likely_cause": likely_cause,
        "manager_action": manager_action,
        "coaching_move": coaching_move,
        "roleplay": roleplay,
        "best_rep": best_rep,
        "review_rep": review_rep,
        "best_source": best_source,
        "review_source": review_source,
    }


def build_manager_report(metrics: dict, targets: dict, diagnosis: dict) -> str:
    return f"""# OpsPilot AI Manager Report

## Executive Summary

The team generated **{money(metrics['total_revenue'])}** from **{metrics['total_sales']:,.0f} sales** on **{metrics['total_leads']:,.0f} leads issued**.

## KPI Snapshot

| Metric | Result | Target |
|---|---:|---:|
| Leads Issued | {metrics['total_leads']:,.0f} | - |
| Demos | {metrics['total_demos']:,.0f} | - |
| Sales | {metrics['total_sales']:,.0f} | - |
| Revenue | {money(metrics['total_revenue'])} | - |
| Demo Rate | {pct(metrics['demo_rate'])} | {pct(targets['demo_rate'])} |
| Close Rate | {pct(metrics['close_rate'])} | {pct(targets['close_rate'])} |
| Average Sale | {money(metrics['avg_sale'])} | {money(targets['avg_sale'])} |
| NSLI | {money(metrics['nsli'])} | {money(targets['nsli'])} |

## Operations Diagnosis

| Category | Result |
|---|---|
| Primary Bottleneck | {diagnosis['primary_bottleneck']} |
| Priority Level | {diagnosis['priority']} |
| Strongest Rep | {diagnosis['best_rep']['Rep']} |
| Rep to Review | {diagnosis['review_rep']['Rep']} |
| Strongest Lead Source | {diagnosis['best_source']['Lead Source']} |
| Lead Source to Review | {diagnosis['review_source']['Lead Source']} |

## Likely Cause

{diagnosis['likely_cause']}

## Recommended Manager Action

{diagnosis['manager_action']}

## Recommended Coaching Move

{diagnosis['coaching_move']}

## Suggested Roleplay

{diagnosis['roleplay']}

## Weekly Action Plan

1. Review unsold demos and assign follow-up actions.
2. Coach the rep needing review on the highest-impact bottleneck.
3. Protect or increase activity around the strongest lead source.
4. Audit the weakest lead source before spending more time or money there.
5. Use the next sales meeting to roleplay the most common objection or bottleneck.

---

Generated by OpsPilot AI.
"""

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

with st.sidebar:
    st.title("OpsPilot AI")
    st.caption("Version 2.0")
    st.markdown(
        """
        Operations intelligence for field-sales and home-service teams.

        Adjust KPI targets below to match the business model being analyzed.
        """
    )

    st.divider()
    st.header("KPI Targets")
    target_demo_rate = st.slider("Target Demo Rate", 0.30, 0.90, 0.60, 0.05)
    target_close_rate = st.slider("Target Close Rate", 0.10, 0.70, 0.35, 0.05)
    target_avg_sale = st.number_input("Target Average Sale", min_value=1000, max_value=100000, value=12000, step=500)
    target_nsli = st.number_input("Target NSLI", min_value=500, max_value=50000, value=4000, step=250)

# -----------------------------------------------------------------------------
# Hero
# -----------------------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Operations Intelligence Dashboard</div>
        <div class="hero-title">OpsPilot AI</div>
        <div class="hero-subtitle">
            Turn sales activity data into KPI visibility, rep performance insights, lead source analysis,
            coaching priorities, manager briefs, and meeting-ready action plans.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data upload
# -----------------------------------------------------------------------------

st.markdown('<div class="section-title">Upload sales activity data</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-lede">Use the sample data to explore the dashboard, or upload a CSV using the required format.</div>',
    unsafe_allow_html=True,
)

upload_col1, upload_col2 = st.columns([1, 2])
with upload_col1:
    st.download_button(
        label="Download CSV Template",
        data=SAMPLE_TEMPLATE,
        file_name="opspilot-csv-template.csv",
        mime="text/csv",
        use_container_width=True,
    )
with upload_col2:
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

raw_df = load_data(uploaded_file)

# -----------------------------------------------------------------------------
# Filters
# -----------------------------------------------------------------------------

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    rep_options = sorted(raw_df["Rep"].dropna().unique())
    selected_reps = st.multiselect("Rep", rep_options, default=rep_options)

with filter_col2:
    source_options = sorted(raw_df["Lead Source"].dropna().unique())
    selected_sources = st.multiselect("Lead Source", source_options, default=source_options)

with filter_col3:
    min_date = raw_df["Date"].min().date()
    max_date = raw_df["Date"].max().date()
    selected_dates = st.date_input("Date Range", value=(min_date, max_date))

filtered_df = raw_df[
    raw_df["Rep"].isin(selected_reps)
    & raw_df["Lead Source"].isin(selected_sources)
]

if selected_dates and len(selected_dates) == 2:
    start_date = pd.to_datetime(selected_dates[0])
    end_date = pd.to_datetime(selected_dates[1])
    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date)
        & (filtered_df["Date"] <= end_date)
    ]

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# -----------------------------------------------------------------------------
# KPI calculations
# -----------------------------------------------------------------------------

total_leads = filtered_df["Leads Issued"].sum()
total_demos = filtered_df["Demos"].sum()
total_sales = filtered_df["Sales"].sum()
total_revenue = filtered_df["Revenue"].sum()

metrics = {
    "total_leads": total_leads,
    "total_demos": total_demos,
    "total_sales": total_sales,
    "total_revenue": total_revenue,
    "demo_rate": safe_divide(total_demos, total_leads),
    "close_rate": safe_divide(total_sales, total_demos),
    "avg_sale": safe_divide(total_revenue, total_sales),
    "nsli": safe_divide(total_revenue, total_leads),
}

targets = {
    "demo_rate": target_demo_rate,
    "close_rate": target_close_rate,
    "avg_sale": float(target_avg_sale),
    "nsli": float(target_nsli),
}

# -----------------------------------------------------------------------------
# KPI cards
# -----------------------------------------------------------------------------

st.markdown('<div class="section-title">Executive KPI snapshot</div>', unsafe_allow_html=True)

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    kpi_card("Leads Issued", f"{total_leads:,.0f}")
with kpi_col2:
    kpi_card("Revenue", money(total_revenue))
with kpi_col3:
    kpi_card("Demo Rate", pct(metrics["demo_rate"]), pct(target_demo_rate))
with kpi_col4:
    kpi_card("Close Rate", pct(metrics["close_rate"]), pct(target_close_rate))

kpi_col5, kpi_col6, kpi_col7, kpi_col8 = st.columns(4)
with kpi_col5:
    kpi_card("Sales", f"{total_sales:,.0f}")
with kpi_col6:
    kpi_card("Demos", f"{total_demos:,.0f}")
with kpi_col7:
    kpi_card("Average Sale", money(metrics["avg_sale"]), money(target_avg_sale))
with kpi_col8:
    kpi_card("NSLI", money(metrics["nsli"]), money(target_nsli))

# -----------------------------------------------------------------------------
# Summaries and diagnosis
# -----------------------------------------------------------------------------

rep_summary = build_summary(filtered_df, "Rep").sort_values("Revenue", ascending=False)
source_summary = build_summary(filtered_df, "Lead Source").sort_values("NSLI", ascending=False)
diagnosis = generate_diagnosis(metrics, targets, rep_summary, source_summary)

st.markdown('<div class="section-title">Operational health</div>', unsafe_allow_html=True)
health_col1, health_col2 = st.columns(2)

health_items = [
    ("Demo Rate", metrics["demo_rate"], target_demo_rate, pct(metrics["demo_rate"]), pct(target_demo_rate)),
    ("Close Rate", metrics["close_rate"], target_close_rate, pct(metrics["close_rate"]), pct(target_close_rate)),
    ("Average Sale", metrics["avg_sale"], target_avg_sale, money(metrics["avg_sale"]), money(target_avg_sale)),
    ("NSLI", metrics["nsli"], target_nsli, money(metrics["nsli"]), money(target_nsli)),
]

for index, (name, value, target, display_value, display_target) in enumerate(health_items):
    status, status_class, description = evaluate_metric(value, target, name)
    with [health_col1, health_col2][index % 2]:
        risk_card(
            name,
            status,
            status_class,
            f"Current: {display_value}. Target: {display_target}. {description}",
        )

st.markdown('<div class="section-title">AI operations diagnosis</div>', unsafe_allow_html=True)

diag_col1, diag_col2, diag_col3 = st.columns(3)
with diag_col1:
    kpi_card("Primary Bottleneck", diagnosis["primary_bottleneck"])
with diag_col2:
    kpi_card("Priority Level", diagnosis["priority"])
with diag_col3:
    kpi_card("Rep to Review", diagnosis["review_rep"]["Rep"])

st.markdown(
    f"""
    <div class="brief-card">
        <h3>Manager Diagnosis</h3>
        <p><strong>Likely cause:</strong> {diagnosis['likely_cause']}</p>
        <p><strong>Recommended manager action:</strong> {diagnosis['manager_action']}</p>
        <p><strong>Recommended coaching move:</strong> {diagnosis['coaching_move']}</p>
        <p><strong>Suggested roleplay:</strong> {diagnosis['roleplay']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Tables and charts
# -----------------------------------------------------------------------------

st.markdown('<div class="section-title">Rep performance</div>', unsafe_allow_html=True)
st.dataframe(format_summary_table(rep_summary), use_container_width=True, hide_index=True)
st.bar_chart(rep_summary.set_index("Rep")["Revenue"])

st.markdown('<div class="section-title">Lead source performance</div>', unsafe_allow_html=True)
st.dataframe(format_summary_table(source_summary), use_container_width=True, hide_index=True)
st.bar_chart(source_summary.set_index("Lead Source")["NSLI"])

# -----------------------------------------------------------------------------
# Manager brief and agenda
# -----------------------------------------------------------------------------

best_rep = diagnosis["best_rep"]
review_rep = diagnosis["review_rep"]
best_source = diagnosis["best_source"]
review_source = diagnosis["review_source"]

st.markdown('<div class="section-title">Manager brief</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="brief-card">
        <h3>Executive Summary</h3>
        <p>The team generated <strong>{money(total_revenue)}</strong> from <strong>{total_sales:,.0f} sales</strong> on <strong>{total_leads:,.0f} leads issued</strong>.</p>
        <ul>
            <li><strong>Top revenue producer:</strong> {best_rep['Rep']} at {money(best_rep['Revenue'])}</li>
            <li><strong>Rep to review:</strong> {review_rep['Rep']} based on lowest NSLI</li>
            <li><strong>Strongest lead source:</strong> {best_source['Lead Source']} at {money(best_source['NSLI'])} NSLI</li>
            <li><strong>Lead source to review:</strong> {review_source['Lead Source']} at {money(review_source['NSLI'])} NSLI</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Weekly sales meeting agenda</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="brief-card">
        <h3>Recommended Agenda</h3>
        <ol>
            <li><strong>Wins:</strong> Recognize {best_rep['Rep']} and the strongest lead source, {best_source['Lead Source']}.</li>
            <li><strong>Numbers in focus:</strong> Review demo rate, close rate, average sale, and NSLI against targets.</li>
            <li><strong>Bottleneck discussion:</strong> Focus on {diagnosis['primary_bottleneck']}.</li>
            <li><strong>Roleplay:</strong> {diagnosis['roleplay']}</li>
            <li><strong>Action commitments:</strong> Each rep commits to one measurable action before the next meeting.</li>
        </ol>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Report download and app notes
# -----------------------------------------------------------------------------

st.markdown('<div class="section-title">Download manager report</div>', unsafe_allow_html=True)
manager_report = build_manager_report(metrics, targets, diagnosis)
st.download_button(
    label="Download Manager Report",
    data=manager_report,
    file_name="opspilot-manager-report.md",
    mime="text/markdown",
    use_container_width=True,
)

with st.expander("How to use OpsPilot AI"):
    st.markdown(
        """
        1. Download the CSV template.
        2. Replace the sample rows with sales activity data.
        3. Upload the completed CSV file.
        4. Adjust KPI targets in the sidebar.
        5. Review the KPI snapshot, operational health, AI diagnosis, manager brief, and meeting agenda.
        6. Download the manager report for coaching or meeting prep.

        Required CSV columns: Date, Rep, Lead Source, Leads Issued, Demos, Sales, Revenue.
        """
    )

st.markdown(
    '<div class="note-box">Privacy note: Uploaded CSV files are processed during the active app session and are not saved by this app.</div>',
    unsafe_allow_html=True,
)

with st.expander("View filtered raw data"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
