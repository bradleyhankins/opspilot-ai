from io import StringIO

import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="OpsPilot AI",
    page_icon="📊",
    layout="wide",
)

# -----------------------------------------------------------------------------
# Data configuration
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

EDITABLE_SAMPLE_CSV = """Date,Rep,Lead Source,Leads Issued,Demos,Sales,Revenue
2026-01-05,Alex Carter,Website,10,7,3,42000
2026-01-05,Jordan Lee,Referral,8,6,3,39000
2026-01-06,Taylor Brooks,Canvassing,12,6,2,24000
2026-01-06,Morgan Reed,Partner Lead,6,5,2,30000
2026-01-07,Casey Nguyen,Website,9,7,2,28000
2026-01-07,Alex Carter,Referral,7,6,3,45000
2026-01-08,Jordan Lee,Canvassing,11,6,2,26000
2026-01-08,Taylor Brooks,Paid Search,6,3,1,13500
2026-01-09,Morgan Reed,Website,8,6,2,31000
2026-01-09,Casey Nguyen,Event,5,3,1,14500
2026-01-10,Alex Carter,Partner Lead,5,5,2,33500
2026-01-10,Jordan Lee,Website,9,7,3,41000
2026-01-11,Taylor Brooks,Referral,6,5,2,29500
2026-01-11,Morgan Reed,Canvassing,10,5,1,15500
2026-01-12,Casey Nguyen,Paid Search,7,4,1,16000
"""

# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
.block-container {
    max-width: 1180px;
    padding-top: 1.35rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #111827;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #f9fafb !important;
}

.hero {
    padding: 1.9rem 2rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #111827 0%, #1f2937 52%, #334155 100%);
    color: #ffffff;
    box-shadow: 0 18px 36px rgba(17, 24, 39, .18);
    margin-bottom: 1rem;
    border: 1px solid rgba(255, 255, 255, .08);
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
    font-size: 2.25rem;
    line-height: 1.08;
    font-weight: 850;
    margin-bottom: .65rem;
}

.hero-subtitle {
    font-size: 1.02rem;
    line-height: 1.62;
    color: #e5e7eb;
    max-width: 900px;
}

.hero-pills span {
    display: inline-block;
    padding: .35rem .65rem;
    margin: .75rem .28rem 0 0;
    border-radius: 999px;
    background: rgba(255, 255, 255, .10);
    border: 1px solid rgba(255, 255, 255, .16);
    font-weight: 700;
    font-size: .78rem;
    color: #f8fafc;
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
    max-width: 950px;
}

.kpi-card,
.brief-card,
.risk-card,
.upload-card,
.coach-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, .055);
}

.kpi-card {
    height: 138px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    margin-bottom: .75rem;
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
    font-size: 1.52rem;
    line-height: 1.16;
    font-weight: 900;
    overflow-wrap: break-word;
}

.kpi-target {
    margin-top: .55rem;
    color: #64748b;
    font-size: .85rem;
    line-height: 1.35;
}

.upload-card,
.brief-card,
.risk-card,
.coach-card {
    padding: 1.15rem;
    margin-bottom: .8rem;
}

.upload-card {
    border-left: 5px solid #1d4ed8;
}

.brief-card {
    border-left: 5px solid #111827;
}

.coach-card {
    border-left: 5px solid #1d4ed8;
    min-height: 185px;
}

.upload-card h3,
.brief-card h3,
.risk-card h3,
.coach-card h3 {
    font-size: 1.05rem;
    font-weight: 850;
    color: #111827;
    margin-bottom: .4rem;
}

.upload-card p,
.upload-card li,
.brief-card p,
.brief-card li,
.risk-card p,
.risk-card li,
.coach-card p,
.coach-card li {
    color: #4b5563;
    line-height: 1.52;
    font-size: .93rem;
}

.risk-high {
    border-left: 5px solid #dc2626;
}

.risk-medium {
    border-left: 5px solid #f59e0b;
}

.risk-healthy {
    border-left: 5px solid #059669;
}

.status-pill {
    display: inline-block;
    padding: .25rem .6rem;
    border-radius: 999px;
    font-weight: 850;
    font-size: .78rem;
    margin-bottom: .5rem;
}

.status-high {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

.status-medium {
    background: #fef3c7;
    color: #92400e;
    border: 1px solid #fde68a;
}

.status-healthy {
    background: #d1fae5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}

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
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Formatting helpers
# -----------------------------------------------------------------------------


def money(value: float) -> str:
    """Format a number as whole-dollar currency."""
    return f"${value:,.0f}"


def pct(value: float) -> str:
    """Format a decimal as a percentage."""
    return f"{value:.1%}"


def safe_divide(numerator: float, denominator: float) -> float:
    """Divide safely and return zero when the denominator is zero."""
    return numerator / denominator if denominator else 0

# -----------------------------------------------------------------------------
# UI helpers
# -----------------------------------------------------------------------------


def section_title(title: str, lede: str | None = None) -> None:
    """Render a consistent section heading."""
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if lede:
        st.markdown(f'<div class="section-lede">{lede}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, target: str | None = None) -> None:
    """Render a KPI card."""
    target_html = f'<div class="kpi-target">Target: {target}</div>' if target else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {target_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_card(title: str, status: str, status_class: str, description: str) -> None:
    """Render an operational health card."""
    card_class_by_status = {
        "status-high": "risk-high",
        "status-medium": "risk-medium",
        "status-healthy": "risk-healthy",
    }
    card_class = card_class_by_status.get(status_class, "risk-medium")

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


def brief_card(title: str, body_html: str) -> None:
    """Render a manager brief card."""
    st.markdown(
        f"""
        <div class="brief-card">
            <h3>{title}</h3>
            {body_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Data processing helpers
# -----------------------------------------------------------------------------


def clean_currency_column(series: pd.Series) -> pd.Series:
    """Clean currency values that may include dollar signs or commas."""
    return (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace("", "0")
        .astype(float)
    )


def load_data(uploaded_file) -> pd.DataFrame:
    """Load uploaded CSV data or fall back to the public-safe sample data."""
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        try:
            df = pd.read_csv("sample_data.csv")
        except FileNotFoundError:
            df = pd.read_csv(StringIO(EDITABLE_SAMPLE_CSV))

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        st.stop()

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for column in ["Leads Issued", "Demos", "Sales"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    df["Revenue"] = clean_currency_column(df["Revenue"])
    df = df.dropna(subset=["Date"])

    if df.empty:
        st.error("The uploaded file did not contain usable dated rows after cleanup.")
        st.stop()

    return df


def filter_data(
    df: pd.DataFrame,
    selected_reps: list[str],
    selected_sources: list[str],
    selected_dates,
) -> pd.DataFrame:
    """Apply rep, lead source, and date-range filters."""
    filtered_df = df[
        df["Rep"].isin(selected_reps)
        & df["Lead Source"].isin(selected_sources)
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

    return filtered_df


def calculate_metrics(df: pd.DataFrame) -> dict:
    """Calculate high-level dashboard metrics."""
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
    """Build grouped rep or lead-source performance summaries."""
    summary = df.groupby(group_col, as_index=False).agg(
        {
            "Leads Issued": "sum",
            "Demos": "sum",
            "Sales": "sum",
            "Revenue": "sum",
        }
    )

    summary["Demo Rate"] = summary.apply(
        lambda row: safe_divide(row["Demos"], row["Leads Issued"]),
        axis=1,
    )
    summary["Close Rate"] = summary.apply(
        lambda row: safe_divide(row["Sales"], row["Demos"]),
        axis=1,
    )
    summary["Average Sale"] = summary.apply(
        lambda row: safe_divide(row["Revenue"], row["Sales"]),
        axis=1,
    )
    summary["NSLI"] = summary.apply(
        lambda row: safe_divide(row["Revenue"], row["Leads Issued"]),
        axis=1,
    )

    return summary


def build_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Build date-based trend metrics."""
    trends = df.groupby("Date", as_index=False).agg(
        {
            "Leads Issued": "sum",
            "Demos": "sum",
            "Sales": "sum",
            "Revenue": "sum",
        }
    )
    trends = trends.sort_values("Date")
    trends["Demo Rate"] = trends.apply(
        lambda row: safe_divide(row["Demos"], row["Leads Issued"]),
        axis=1,
    )
    trends["Close Rate"] = trends.apply(
        lambda row: safe_divide(row["Sales"], row["Demos"]),
        axis=1,
    )
    trends["NSLI"] = trends.apply(
        lambda row: safe_divide(row["Revenue"], row["Leads Issued"]),
        axis=1,
    )
    return trends


def format_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Format summary tables for display."""
    formatted_df = df.copy()

    for column in ["Revenue", "Average Sale", "NSLI"]:
        formatted_df[column] = formatted_df[column].apply(money)

    for column in ["Demo Rate", "Close Rate"]:
        formatted_df[column] = formatted_df[column].apply(pct)

    return formatted_df

# -----------------------------------------------------------------------------
# Diagnosis and coaching logic
# -----------------------------------------------------------------------------


def evaluate_metric(value: float, target: float, metric_name: str) -> tuple[str, str, str]:
    """Evaluate a metric against its configured target."""
    if value >= target:
        return "Healthy", "status-healthy", f"{metric_name} is meeting or exceeding the target."

    if value >= target * 0.85:
        return "Watch", "status-medium", f"{metric_name} is close to target but should be watched."

    return "Risk", "status-high", f"{metric_name} is materially below target and needs manager attention."


def generate_diagnosis(
    metrics: dict,
    targets: dict,
    rep_summary: pd.DataFrame,
    source_summary: pd.DataFrame,
) -> dict:
    """Generate a rules-based operations diagnosis from KPI gaps."""
    metric_checks = [
        ("Demo Rate", metrics["demo_rate"], targets["demo_rate"]),
        ("Close Rate", metrics["close_rate"], targets["close_rate"]),
        ("Average Sale", metrics["avg_sale"], targets["avg_sale"]),
        ("NSLI", metrics["nsli"], targets["nsli"]),
    ]

    metric_gaps = [
        (name, safe_divide(target - value, target))
        for name, value, target in metric_checks
    ]
    primary_bottleneck, primary_gap = max(metric_gaps, key=lambda item: item[1])

    best_rep = rep_summary.sort_values("Revenue", ascending=False).iloc[0]
    review_rep = rep_summary.sort_values("NSLI", ascending=True).iloc[0]
    best_source = source_summary.sort_values("NSLI", ascending=False).iloc[0]
    review_source = source_summary.sort_values("NSLI", ascending=True).iloc[0]

    diagnosis_map = {
        "Demo Rate": {
            "priority": "High" if primary_gap > 0.15 else "Medium",
            "likely_cause": "The team is not converting enough issued leads into completed demos. This may point to weak appointment setting, poor confirmation, low customer commitment, scheduling friction, or lead quality issues.",
            "manager_action": "Review issued leads that did not demo. Look for patterns by rep, lead source, appointment window, and confirmation process.",
            "coaching_move": "Coach reps on expectation setting, decision-maker confirmation, urgency, and reducing no-show risk.",
            "roleplay": "Customer says: 'Just come out and give me a quick quote. I may not have much time.'",
        },
        "Close Rate": {
            "priority": "High" if primary_gap > 0.15 else "Medium",
            "likely_cause": "The team is getting demos but not converting enough into sales. This may point to weak discovery, poor value build, price resistance, lack of urgency, or inconsistent closing language.",
            "manager_action": "Review recent unsold demos and identify the most common objection. Build the next meeting around that single closing skill.",
            "coaching_move": "Coach reps on discovery, value stacking, financing confidence, urgency, and direct commitment language.",
            "roleplay": "Customer says: 'We need to think about it and get a few more quotes.'",
        },
        "Average Sale": {
            "priority": "Medium",
            "likely_cause": "The team is closing work, but project size is below target. This may indicate incomplete scopes, weak upgrade positioning, missed add-ons, or reps defaulting to the lowest option.",
            "manager_action": "Audit recent sold jobs and compare the presented scope against the full opportunity. Look for missed upgrades, add-ons, and scope completeness.",
            "coaching_move": "Coach reps on good/better/best options, long-term value, and add-ons that solve real customer problems.",
            "roleplay": "Customer says: 'We just want the cheapest option that gets the job done.'",
        },
        "NSLI": {
            "priority": "Medium",
            "likely_cause": "Revenue per issued lead is below target. This may come from lead quality, rep assignment, low demo rate, low close rate, or smaller job size.",
            "manager_action": "Compare NSLI by rep and lead source. Shift attention toward the best-performing source and review whether low-performing sources need better qualification.",
            "coaching_move": "Coach the team on prioritizing high-intent opportunities, follow-up speed, and conversion discipline on every issued lead.",
            "roleplay": "Customer says: 'I’m not sure if this is something we’re ready to do right now.'",
        },
    }

    if primary_gap <= 0:
        diagnosis = {
            "priority": "Healthy",
            "likely_cause": "The selected data is meeting the configured targets. Protect what is working and standardize the behaviors behind the strongest results.",
            "manager_action": "Study the top rep and strongest lead source, then document the process that should become the team standard.",
            "coaching_move": "Use coaching time for advanced skill sharpening rather than basic correction.",
            "roleplay": "Customer says: 'Everything sounds good, but I want to make sure we are making the right decision.'",
        }
        primary_bottleneck = "No Critical Bottleneck"
    else:
        diagnosis = diagnosis_map[primary_bottleneck]

    return {
        "primary_bottleneck": primary_bottleneck,
        "priority": diagnosis["priority"],
        "likely_cause": diagnosis["likely_cause"],
        "manager_action": diagnosis["manager_action"],
        "coaching_move": diagnosis["coaching_move"],
        "roleplay": diagnosis["roleplay"],
        "best_rep": best_rep,
        "review_rep": review_rep,
        "best_source": best_source,
        "review_source": review_source,
    }


def build_priorities(diagnosis: dict, metrics: dict, targets: dict) -> list[str]:
    """Build the top three manager priorities."""
    priorities = [
        f"Coach {diagnosis['review_rep']['Rep']} around {diagnosis['primary_bottleneck']} and review their next 3 opportunities.",
        f"Audit {diagnosis['review_source']['Lead Source']} lead quality before increasing spend or activity there.",
        f"Protect {diagnosis['best_source']['Lead Source']} and study why it is producing stronger NSLI.",
    ]

    if metrics["demo_rate"] < targets["demo_rate"]:
        priorities[0] = "Review no-demo leads and tighten appointment confirmation/expectation setting."

    if metrics["close_rate"] < targets["close_rate"]:
        priorities[0] = "Review unsold demos and roleplay the most common closing objection this week."

    if metrics["avg_sale"] < targets["avg_sale"]:
        priorities.append("Audit sold scopes for missed upgrades, add-ons, and incomplete project value presentation.")

    return priorities[:3]


def rep_coaching_note(row: pd.Series, targets: dict) -> list[str]:
    """Create coaching notes for a single rep summary row."""
    notes = []

    if row["Leads Issued"] < 5:
        notes.append("Lead volume is low, so review activity volume before judging conversion.")

    if row["Demo Rate"] < targets["demo_rate"]:
        notes.append("Demo rate is below target; coach confirmation, expectation setting, and lead commitment.")

    if row["Close Rate"] < targets["close_rate"] and row["Demos"] >= 1:
        notes.append("Close rate is below target; coach discovery, value build, urgency, and objection handling.")

    if row["Average Sale"] < targets["avg_sale"] and row["Sales"] >= 1:
        notes.append("Average sale is below target; review scope completeness and upgrade/add-on positioning.")

    if row["NSLI"] < targets["nsli"]:
        notes.append("NSLI is below target; review lead quality, conversion discipline, and follow-up speed.")

    if not notes:
        notes.append("Performance is healthy against current targets; study and document what is working.")

    return notes

# -----------------------------------------------------------------------------
# Report generation
# -----------------------------------------------------------------------------


def build_manager_report(metrics: dict, targets: dict, diagnosis: dict, priorities: list[str]) -> str:
    """Generate the downloadable Markdown manager report."""
    priority_lines = "\n".join(
        f"{index + 1}. {priority}"
        for index, priority in enumerate(priorities)
    )

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

## Top 3 Manager Priorities

{priority_lines}

## Likely Cause

{diagnosis['likely_cause']}

## Recommended Manager Action

{diagnosis['manager_action']}

## Recommended Coaching Move

{diagnosis['coaching_move']}

## Suggested Roleplay

{diagnosis['roleplay']}

---

Generated by OpsPilot AI.
"""

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

with st.sidebar:
    st.title("OpsPilot AI")
    st.caption("Version 2.2")
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
        <div class="hero-pills">
            <span>Operations</span><span>RevOps</span><span>KPI Reporting</span><span>Manager Briefs</span><span>Streamlit</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Upload workflow
# -----------------------------------------------------------------------------

section_title(
    "Upload sales activity data",
    "Download the editable sample CSV, replace the fictional rows with your own activity data, then upload the edited file to generate the dashboard.",
)

upload_info_col, upload_action_col = st.columns([2, 1])
with upload_info_col:
    st.markdown(
        """
        <div class="upload-card">
            <h3>CSV format</h3>
            <p>Your file must include these columns: <strong>Date, Rep, Lead Source, Leads Issued, Demos, Sales, Revenue</strong>.</p>
            <p>The sample file uses fictional placeholder reps and lead sources so it can be safely edited for testing.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with upload_action_col:
    st.download_button(
        "Download Editable Sample CSV",
        data=EDITABLE_SAMPLE_CSV,
        file_name="opspilot-editable-sample.csv",
        mime="text/csv",
        use_container_width=True,
    )
    uploaded_file = st.file_uploader("Upload Edited CSV", type=["csv"])

raw_df = load_data(uploaded_file)

# -----------------------------------------------------------------------------
# Data readiness and filters
# -----------------------------------------------------------------------------

section_title("Data readiness check")
readiness_col1, readiness_col2, readiness_col3, readiness_col4 = st.columns(4)
with readiness_col1:
    kpi_card("Rows Loaded", f"{len(raw_df):,.0f}")
with readiness_col2:
    kpi_card("Reps", f"{raw_df['Rep'].nunique():,.0f}")
with readiness_col3:
    kpi_card("Lead Sources", f"{raw_df['Lead Source'].nunique():,.0f}")
with readiness_col4:
    date_range = f"{raw_df['Date'].min().date()} to {raw_df['Date'].max().date()}"
    kpi_card("Date Range", date_range)

section_title("Filters")
filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    rep_options = sorted(raw_df["Rep"].dropna().unique())
    selected_reps = st.multiselect("Rep", rep_options, default=rep_options)
with filter_col2:
    source_options = sorted(raw_df["Lead Source"].dropna().unique())
    selected_sources = st.multiselect("Lead Source", source_options, default=source_options)
with filter_col3:
    selected_dates = st.date_input(
        "Date Range",
        value=(raw_df["Date"].min().date(), raw_df["Date"].max().date()),
    )

filtered_df = filter_data(raw_df, selected_reps, selected_sources, selected_dates)

# -----------------------------------------------------------------------------
# Core calculations
# -----------------------------------------------------------------------------

metrics = calculate_metrics(filtered_df)
targets = {
    "demo_rate": target_demo_rate,
    "close_rate": target_close_rate,
    "avg_sale": float(target_avg_sale),
    "nsli": float(target_nsli),
}

rep_summary = build_summary(filtered_df, "Rep").sort_values("Revenue", ascending=False)
source_summary = build_summary(filtered_df, "Lead Source").sort_values("NSLI", ascending=False)
trends = build_trends(filtered_df)
diagnosis = generate_diagnosis(metrics, targets, rep_summary, source_summary)
priorities = build_priorities(diagnosis, metrics, targets)

# -----------------------------------------------------------------------------
# Executive KPI snapshot
# -----------------------------------------------------------------------------

section_title("Executive KPI snapshot")

kpi_rows = [
    [
        ("Leads Issued", f"{metrics['total_leads']:,.0f}", None),
        ("Revenue", money(metrics["total_revenue"]), None),
        ("Demo Rate", pct(metrics["demo_rate"]), pct(target_demo_rate)),
        ("Close Rate", pct(metrics["close_rate"]), pct(target_close_rate)),
    ],
    [
        ("Sales", f"{metrics['total_sales']:,.0f}", None),
        ("Demos", f"{metrics['total_demos']:,.0f}", None),
        ("Average Sale", money(metrics["avg_sale"]), money(target_avg_sale)),
        ("NSLI", money(metrics["nsli"]), money(target_nsli)),
    ],
]

for kpi_row in kpi_rows:
    kpi_cols = st.columns(4)
    for col, (label, value, target) in zip(kpi_cols, kpi_row):
        with col:
            kpi_card(label, value, target)

# -----------------------------------------------------------------------------
# Operational health and priorities
# -----------------------------------------------------------------------------

section_title("Operational health")
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

section_title("Top 3 manager priorities")
priority_list_html = "".join(f"<li>{priority}</li>" for priority in priorities)
brief_card("Recommended Next Actions", f"<ol>{priority_list_html}</ol>")

# -----------------------------------------------------------------------------
# AI operations diagnosis
# -----------------------------------------------------------------------------

section_title("AI operations diagnosis")
diagnosis_col1, diagnosis_col2, diagnosis_col3 = st.columns(3)
with diagnosis_col1:
    kpi_card("Primary Bottleneck", diagnosis["primary_bottleneck"])
with diagnosis_col2:
    kpi_card("Priority Level", diagnosis["priority"])
with diagnosis_col3:
    kpi_card("Rep to Review", diagnosis["review_rep"]["Rep"])

brief_card(
    "Manager Diagnosis",
    f"""
    <p><strong>Likely cause:</strong> {diagnosis['likely_cause']}</p>
    <p><strong>Recommended manager action:</strong> {diagnosis['manager_action']}</p>
    <p><strong>Recommended coaching move:</strong> {diagnosis['coaching_move']}</p>
    <p><strong>Suggested roleplay:</strong> {diagnosis['roleplay']}</p>
    """,
)

# -----------------------------------------------------------------------------
# Trend analysis
# -----------------------------------------------------------------------------

section_title(
    "Trend analysis",
    "Trend charts show whether performance is improving or slipping across the filtered date range.",
)
trend_tabs = st.tabs(["Revenue", "Demo Rate", "Close Rate", "NSLI"])
with trend_tabs[0]:
    st.line_chart(trends.set_index("Date")["Revenue"])
with trend_tabs[1]:
    st.line_chart(trends.set_index("Date")["Demo Rate"])
with trend_tabs[2]:
    st.line_chart(trends.set_index("Date")["Close Rate"])
with trend_tabs[3]:
    st.line_chart(trends.set_index("Date")["NSLI"])

# -----------------------------------------------------------------------------
# Rep and lead source performance
# -----------------------------------------------------------------------------

section_title("Rep performance")
st.dataframe(format_summary_table(rep_summary), use_container_width=True, hide_index=True)
st.bar_chart(rep_summary.set_index("Rep")["Revenue"])

section_title("Rep coaching cards")
coach_cols = st.columns(2)
for position, (_, row) in enumerate(rep_summary.iterrows()):
    notes = rep_coaching_note(row, targets)
    note_items = "".join(f"<li>{note}</li>" for note in notes[:3])
    card_html = f"""
    <div class="coach-card">
        <h3>{row['Rep']}</h3>
        <p><strong>Revenue:</strong> {money(row['Revenue'])} | <strong>NSLI:</strong> {money(row['NSLI'])}</p>
        <ul>{note_items}</ul>
    </div>
    """
    with coach_cols[position % 2]:
        st.markdown(card_html, unsafe_allow_html=True)

section_title("Lead source performance")
st.dataframe(format_summary_table(source_summary), use_container_width=True, hide_index=True)
st.bar_chart(source_summary.set_index("Lead Source")["NSLI"])

# -----------------------------------------------------------------------------
# Manager brief and meeting agenda
# -----------------------------------------------------------------------------

best_rep = diagnosis["best_rep"]
review_rep = diagnosis["review_rep"]
best_source = diagnosis["best_source"]
review_source = diagnosis["review_source"]

section_title("Manager brief")
brief_card(
    "Executive Summary",
    f"""
    <p>The team generated <strong>{money(metrics['total_revenue'])}</strong> from <strong>{metrics['total_sales']:,.0f} sales</strong> on <strong>{metrics['total_leads']:,.0f} leads issued</strong>.</p>
    <ul>
        <li><strong>Top revenue producer:</strong> {best_rep['Rep']} at {money(best_rep['Revenue'])}</li>
        <li><strong>Rep to review:</strong> {review_rep['Rep']} based on lowest NSLI</li>
        <li><strong>Strongest lead source:</strong> {best_source['Lead Source']} at {money(best_source['NSLI'])} NSLI</li>
        <li><strong>Lead source to review:</strong> {review_source['Lead Source']} at {money(review_source['NSLI'])} NSLI</li>
    </ul>
    """,
)

section_title("Weekly sales meeting agenda")
brief_card(
    "Recommended Agenda",
    f"""
    <ol>
        <li><strong>Wins:</strong> Recognize {best_rep['Rep']} and the strongest lead source, {best_source['Lead Source']}.</li>
        <li><strong>Numbers in focus:</strong> Review demo rate, close rate, average sale, and NSLI against targets.</li>
        <li><strong>Bottleneck discussion:</strong> Focus on {diagnosis['primary_bottleneck']}.</li>
        <li><strong>Roleplay:</strong> {diagnosis['roleplay']}</li>
        <li><strong>Action commitments:</strong> Each rep commits to one measurable action before the next meeting.</li>
    </ol>
    """,
)

# -----------------------------------------------------------------------------
# Downloads and supporting notes
# -----------------------------------------------------------------------------

section_title("Downloads")
download_col1, download_col2 = st.columns(2)
with download_col1:
    manager_report = build_manager_report(metrics, targets, diagnosis, priorities)
    st.download_button(
        "Download Manager Report",
        data=manager_report,
        file_name="opspilot-manager-report.md",
        mime="text/markdown",
        use_container_width=True,
    )
with download_col2:
    st.download_button(
        "Download Filtered Data CSV",
        data=filtered_df.to_csv(index=False),
        file_name="opspilot-filtered-data.csv",
        mime="text/csv",
        use_container_width=True,
    )

with st.expander("How to use OpsPilot AI"):
    st.markdown(
        """
        1. Download the editable sample CSV.
        2. Replace the fictional sample rows with your own sales activity data.
        3. Upload the edited CSV file.
        4. Adjust KPI targets in the sidebar.
        5. Review the KPI snapshot, operational health, trend analysis, AI diagnosis, manager priorities, rep coaching cards, manager brief, and meeting agenda.
        6. Download the manager report or filtered data CSV.

        Required CSV columns: Date, Rep, Lead Source, Leads Issued, Demos, Sales, Revenue.
        """
    )

st.markdown(
    '<div class="note-box">Privacy note: Uploaded CSV files are processed during the active app session and are not saved by this app.</div>',
    unsafe_allow_html=True,
)

with st.expander("View filtered raw data"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
