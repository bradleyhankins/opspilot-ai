from io import StringIO

import pandas as pd
import streamlit as st

from ai_helpers import enhance_text

st.set_page_config(page_title="OpsPilot AI", page_icon="📊", layout="wide")

REQUIRED_COLUMNS = ["Date", "Rep", "Lead Source", "Leads Issued", "Demos", "Sales", "Revenue"]

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

CSS = """
<style>
.block-container{max-width:1180px;padding-top:1.35rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#111827}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label,[data-testid="stSidebar"] li{color:#f9fafb!important}
.hero{padding:1.9rem 2rem;border-radius:20px;background:linear-gradient(135deg,#111827 0%,#1f2937 52%,#334155 100%);color:#fff;box-shadow:0 18px 36px rgba(17,24,39,.18);margin-bottom:1rem;border:1px solid rgba(255,255,255,.08)}
.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:.75rem;font-weight:800;color:#93c5fd;margin-bottom:.65rem}.hero-title{font-size:2.25rem;line-height:1.08;font-weight:850;margin-bottom:.65rem}.hero-subtitle{font-size:1.02rem;line-height:1.62;color:#e5e7eb;max-width:900px}.hero-pills span{display:inline-block;padding:.35rem .65rem;margin:.75rem .28rem 0 0;border-radius:999px;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);font-weight:700;font-size:.78rem;color:#f8fafc}
.section-title{margin-top:1.25rem;margin-bottom:.55rem;font-size:1.4rem;font-weight:850;color:#111827}.section-lede{color:#4b5563;line-height:1.6;margin-bottom:1rem;max-width:950px}
.kpi-card,.brief-card,.risk-card,.upload-card,.coach-card{background:#fff;border:1px solid #e5e7eb;border-radius:18px;box-shadow:0 8px 20px rgba(15,23,42,.055)}.kpi-card{height:138px;padding:1rem;margin-bottom:.75rem}.kpi-label{color:#6b7280;font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}.kpi-value{color:#111827;font-size:1.42rem;line-height:1.16;font-weight:900;overflow-wrap:break-word}.kpi-target{margin-top:.55rem;color:#64748b;font-size:.85rem;line-height:1.35}
.upload-card,.brief-card,.risk-card,.coach-card{padding:1.15rem;margin-bottom:.8rem}.upload-card{border-left:5px solid #1d4ed8}.brief-card{border-left:5px solid #111827}.coach-card{border-left:5px solid #1d4ed8;min-height:175px}.risk-high{border-left:5px solid #dc2626}.risk-medium{border-left:5px solid #f59e0b}.risk-healthy{border-left:5px solid #059669}
.upload-card h3,.brief-card h3,.risk-card h3,.coach-card h3{font-size:1.05rem;font-weight:850;color:#111827;margin-bottom:.4rem}.upload-card p,.upload-card li,.brief-card p,.brief-card li,.risk-card p,.risk-card li,.coach-card p,.coach-card li{color:#4b5563;line-height:1.52;font-size:.93rem}.status-pill{display:inline-block;padding:.25rem .6rem;border-radius:999px;font-weight:850;font-size:.78rem;margin-bottom:.5rem}.status-high{background:#fee2e2;color:#991b1b;border:1px solid #fecaca}.status-medium{background:#fef3c7;color:#92400e;border:1px solid #fde68a}.status-healthy{background:#d1fae5;color:#065f46;border:1px solid #a7f3d0}.note-box{padding:.9rem 1rem;border-radius:14px;background:#f8fafc;color:#334155;border:1px solid #e2e8f0;font-weight:650;margin:.9rem 0;font-size:.92rem}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def money(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0


def section_title(title: str, lede: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if lede:
        st.markdown(f'<div class="section-lede">{lede}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, target: str | None = None) -> None:
    target_html = f'<div class="kpi-target">Target: {target}</div>' if target else ""
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{target_html}</div>', unsafe_allow_html=True)


def html_card(title: str, body_html: str, css_class: str = "brief-card") -> None:
    st.markdown(f'<div class="{css_class}"><h3>{title}</h3>{body_html}</div>', unsafe_allow_html=True)


def md_to_html(text: str) -> str:
    html = text.replace("\n\n", "</p><p>").replace("\n", "<br>")
    return f"<p>{html}</p>"


def clean_currency_column(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False).str.strip().replace("", "0").astype(float)


def load_data(uploaded_file) -> pd.DataFrame:
    df = pd.read_csv(uploaded_file) if uploaded_file is not None else pd.read_csv(StringIO(EDITABLE_SAMPLE_CSV))
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


def calculate_metrics(df: pd.DataFrame) -> dict:
    total_leads = df["Leads Issued"].sum()
    total_demos = df["Demos"].sum()
    total_sales = df["Sales"].sum()
    total_revenue = df["Revenue"].sum()
    return {"total_leads": total_leads, "total_demos": total_demos, "total_sales": total_sales, "total_revenue": total_revenue, "demo_rate": safe_divide(total_demos, total_leads), "close_rate": safe_divide(total_sales, total_demos), "avg_sale": safe_divide(total_revenue, total_sales), "nsli": safe_divide(total_revenue, total_leads)}


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


def evaluate_metric(value: float, target: float, metric_name: str) -> tuple[str, str, str]:
    if value >= target:
        return "Healthy", "status-healthy", f"{metric_name} is meeting or exceeding the target."
    if value >= target * 0.85:
        return "Watch", "status-medium", f"{metric_name} is close to target but should be watched."
    return "Risk", "status-high", f"{metric_name} is materially below target and needs manager attention."


def generate_diagnosis(metrics: dict, targets: dict, rep_summary: pd.DataFrame, source_summary: pd.DataFrame) -> dict:
    metric_checks = [("Demo Rate", metrics["demo_rate"], targets["demo_rate"]), ("Close Rate", metrics["close_rate"], targets["close_rate"]), ("Average Sale", metrics["avg_sale"], targets["avg_sale"]), ("NSLI", metrics["nsli"], targets["nsli"])]
    metric_gaps = [(name, safe_divide(target - value, target)) for name, value, target in metric_checks]
    primary_bottleneck, primary_gap = max(metric_gaps, key=lambda item: item[1])
    best_rep = rep_summary.sort_values("Revenue", ascending=False).iloc[0]
    review_rep = rep_summary.sort_values("NSLI", ascending=True).iloc[0]
    best_source = source_summary.sort_values("NSLI", ascending=False).iloc[0]
    review_source = source_summary.sort_values("NSLI", ascending=True).iloc[0]
    if primary_gap <= 0:
        primary_bottleneck = "No Critical Bottleneck"
        priority = "Healthy"
        likely_cause = "The selected data is meeting the configured targets."
        manager_action = "Study the top rep and strongest lead source, then document the behaviors that should become the team standard."
        coaching_move = "Use coaching time for advanced skill sharpening rather than basic correction."
        roleplay = "Customer says: 'Everything sounds good, but I want to make sure we are making the right decision.'"
    elif primary_bottleneck == "Demo Rate":
        priority = "High" if primary_gap > 0.15 else "Medium"
        likely_cause = "The team is not converting enough issued leads into completed demos."
        manager_action = "Review no-demo leads by rep and lead source. Tighten appointment confirmation and expectation setting."
        coaching_move = "Coach reps on decision-maker confirmation, urgency, and reducing no-show risk."
        roleplay = "Customer says: 'Just come out and give me a quick quote.'"
    elif primary_bottleneck == "Close Rate":
        priority = "High" if primary_gap > 0.15 else "Medium"
        likely_cause = "The team is getting demos but not converting enough into sales."
        manager_action = "Review recent unsold demos and identify the most common objection."
        coaching_move = "Coach discovery, value build, urgency, and direct commitment language."
        roleplay = "Customer says: 'We need to think about it and get a few more quotes.'"
    elif primary_bottleneck == "Average Sale":
        priority = "Medium"
        likely_cause = "The team is closing work, but project size is below target."
        manager_action = "Audit sold scopes for missed upgrades, add-ons, and incomplete value presentation."
        coaching_move = "Coach good/better/best options and complete scope positioning."
        roleplay = "Customer says: 'We just want the cheapest option that gets the job done.'"
    else:
        priority = "Medium"
        likely_cause = "Revenue per issued lead is below target."
        manager_action = "Compare NSLI by rep and lead source and reallocate focus toward stronger channels."
        coaching_move = "Coach prioritization, speed-to-lead, and conversion discipline."
        roleplay = "Customer says: 'I’m not sure if this is something we’re ready to do right now.'"
    return {"primary_bottleneck": primary_bottleneck, "priority": priority, "likely_cause": likely_cause, "manager_action": manager_action, "coaching_move": coaching_move, "roleplay": roleplay, "best_rep": best_rep, "review_rep": review_rep, "best_source": best_source, "review_source": review_source}


def build_priorities(diagnosis: dict, metrics: dict, targets: dict) -> list[str]:
    priorities = [f"Coach {diagnosis['review_rep']['Rep']} around {diagnosis['primary_bottleneck']} and review their next 3 opportunities.", f"Audit {diagnosis['review_source']['Lead Source']} lead quality before increasing spend or activity there.", f"Protect {diagnosis['best_source']['Lead Source']} and study why it is producing stronger NSLI."]
    if metrics["demo_rate"] < targets["demo_rate"]:
        priorities[0] = "Review no-demo leads and tighten appointment confirmation/expectation setting."
    if metrics["close_rate"] < targets["close_rate"]:
        priorities[0] = "Review unsold demos and roleplay the most common closing objection this week."
    return priorities[:3]


def rep_coaching_note(row: pd.Series, targets: dict) -> list[str]:
    notes = []
    if row["Demo Rate"] < targets["demo_rate"]:
        notes.append("Demo rate is below target; coach confirmation and lead commitment.")
    if row["Close Rate"] < targets["close_rate"] and row["Demos"] >= 1:
        notes.append("Close rate is below target; coach value build and objection handling.")
    if row["Average Sale"] < targets["avg_sale"] and row["Sales"] >= 1:
        notes.append("Average sale is below target; review scope completeness and upgrade positioning.")
    if row["NSLI"] < targets["nsli"]:
        notes.append("NSLI is below target; review lead quality, conversion discipline, and follow-up speed.")
    return notes or ["Performance is healthy against current targets; study and document what is working."]


def operational_health_status(metrics: dict, targets: dict) -> str:
    checks = [metrics["demo_rate"] >= targets["demo_rate"], metrics["close_rate"] >= targets["close_rate"], metrics["avg_sale"] >= targets["avg_sale"], metrics["nsli"] >= targets["nsli"]]
    passed = sum(checks)
    if passed >= 3:
        return "Stable"
    if passed == 2:
        return "Watch"
    return "Needs Attention"


def best_manager_move(diagnosis: dict) -> str:
    if diagnosis["primary_bottleneck"] == "Demo Rate":
        return "Tighten confirmation and appointment-setting standards."
    if diagnosis["primary_bottleneck"] == "Close Rate":
        return "Run objection roleplay and review unsold demos."
    if diagnosis["primary_bottleneck"] == "Average Sale":
        return "Audit scopes for missed upgrades and add-ons."
    if diagnosis["primary_bottleneck"] == "NSLI":
        return "Review lead allocation and protect stronger lead sources."
    return "Document what is working and standardize it."


def compare_periods(trends: pd.DataFrame) -> dict:
    if len(trends) < 2:
        return {"label": "Not enough data", "revenue_change": 0, "demo_change": 0, "close_change": 0, "nsli_change": 0}
    midpoint = len(trends) // 2
    first = calculate_metrics(trends.iloc[:midpoint])
    second = calculate_metrics(trends.iloc[midpoint:])
    return {"label": "Second half vs. first half", "revenue_change": second["total_revenue"] - first["total_revenue"], "demo_change": second["demo_rate"] - first["demo_rate"], "close_change": second["close_rate"] - first["close_rate"], "nsli_change": second["nsli"] - first["nsli"]}


def direction(value: float, is_money: bool = False, is_pct: bool = False) -> str:
    arrow = "▲" if value > 0 else "▼" if value < 0 else "—"
    if is_money:
        return f"{arrow} {money(abs(value))}"
    if is_pct:
        return f"{arrow} {abs(value):.1%}"
    return f"{arrow} {value}"


def build_rules_manager_brief(metrics, diagnosis, priorities, health, period_change) -> str:
    priority_lines = "\n".join(f"- {priority}" for priority in priorities)
    return f"""Operational Health: {health}

The team generated {money(metrics['total_revenue'])} from {metrics['total_sales']:,.0f} sales on {metrics['total_leads']:,.0f} leads issued.

Primary bottleneck: {diagnosis['primary_bottleneck']}
Likely cause: {diagnosis['likely_cause']}
Recommended manager action: {diagnosis['manager_action']}
Coaching move: {diagnosis['coaching_move']}
Suggested roleplay: {diagnosis['roleplay']}

Top revenue producer: {diagnosis['best_rep']['Rep']} at {money(diagnosis['best_rep']['Revenue'])}
Rep to review: {diagnosis['review_rep']['Rep']} based on lowest NSLI
Strongest lead source: {diagnosis['best_source']['Lead Source']} at {money(diagnosis['best_source']['NSLI'])} NSLI
Lead source to review: {diagnosis['review_source']['Lead Source']} at {money(diagnosis['review_source']['NSLI'])} NSLI

What changed: {period_change['label']}
Revenue: {direction(period_change['revenue_change'], is_money=True)}
Demo Rate: {direction(period_change['demo_change'], is_pct=True)}
Close Rate: {direction(period_change['close_change'], is_pct=True)}
NSLI: {direction(period_change['nsli_change'], is_money=True)}

Top manager priorities:
{priority_lines}
"""


def build_manager_prompt(rules_brief: str, metrics: dict, targets: dict) -> str:
    return f"""
You are an operations and sales performance manager.
Turn the rules-based brief into a concise manager-ready memo.
Use only the provided data. Do not invent numbers, names, or causes.
Keep it practical and action-oriented.

Metrics:
{metrics}

Targets:
{targets}

Rules-based manager brief:
{rules_brief}

Return:
1. Executive summary
2. What changed
3. Primary bottleneck
4. Coaching focus
5. Lead source focus
6. Three manager action items
"""


def build_manager_report(metrics, targets, diagnosis, priorities, health, period_change, enhanced_brief) -> str:
    priority_lines = "\n".join(f"{index + 1}. {priority}" for index, priority in enumerate(priorities))
    return f"""# OpsPilot AI Manager Report

## AI-Enhanced Manager Brief
{enhanced_brief}

## Executive Summary Scorecard
Operational Health: {health}
Primary Bottleneck: {diagnosis['primary_bottleneck']}
Best Manager Move This Week: {best_manager_move(diagnosis)}
Strongest Opportunity: Protect {diagnosis['best_source']['Lead Source']} and study why it is producing stronger NSLI.

## KPI Snapshot
Revenue: {money(metrics['total_revenue'])}
Leads Issued: {metrics['total_leads']:,.0f}
Demos: {metrics['total_demos']:,.0f}
Sales: {metrics['total_sales']:,.0f}
Demo Rate: {pct(metrics['demo_rate'])}
Close Rate: {pct(metrics['close_rate'])}
Average Sale: {money(metrics['avg_sale'])}
NSLI: {money(metrics['nsli'])}

## What Changed
{period_change['label']}
Revenue: {direction(period_change['revenue_change'], is_money=True)}
Demo Rate: {direction(period_change['demo_change'], is_pct=True)}
Close Rate: {direction(period_change['close_change'], is_pct=True)}
NSLI: {direction(period_change['nsli_change'], is_money=True)}

## Top 3 Manager Priorities
{priority_lines}

## Manager Diagnosis
Likely Cause: {diagnosis['likely_cause']}
Recommended Action: {diagnosis['manager_action']}
Coaching Move: {diagnosis['coaching_move']}
Suggested Roleplay: {diagnosis['roleplay']}

---
Generated by OpsPilot AI.
"""


with st.sidebar:
    st.title("OpsPilot AI")
    st.caption("Version 2.4")
    st.markdown("Operations intelligence for field-sales and home-service teams.")
    st.divider()
    st.header("KPI Targets")
    target_demo_rate = st.slider("Target Demo Rate", 0.30, 0.90, 0.60, 0.05)
    target_close_rate = st.slider("Target Close Rate", 0.10, 0.70, 0.35, 0.05)
    target_avg_sale = st.number_input("Target Average Sale", min_value=1000, max_value=100000, value=12000, step=500)
    target_nsli = st.number_input("Target NSLI", min_value=500, max_value=50000, value=4000, step=250)

st.markdown('<div class="hero"><div class="eyebrow">Operations Intelligence Dashboard</div><div class="hero-title">OpsPilot AI</div><div class="hero-subtitle">Turn sales activity data into KPI visibility, rep performance insights, lead source analysis, coaching priorities, manager briefs, and meeting-ready action plans.</div><div class="hero-pills"><span>Operations</span><span>RevOps</span><span>KPI Reporting</span><span>Manager Briefs</span><span>Streamlit</span></div></div>', unsafe_allow_html=True)

section_title("Upload sales activity data", "Download the editable sample CSV, replace the fictional rows with your own activity data, then upload the edited file to generate the dashboard.")
upload_info_col, upload_action_col = st.columns([2, 1])
with upload_info_col:
    html_card("CSV format", "<p>Your file must include these columns: <strong>Date, Rep, Lead Source, Leads Issued, Demos, Sales, Revenue</strong>.</p><p>The sample file uses fictional placeholder reps and lead sources for safe testing.</p>", "upload-card")
with upload_action_col:
    st.download_button("Download Editable Sample CSV", data=EDITABLE_SAMPLE_CSV, file_name="opspilot-editable-sample.csv", mime="text/csv", use_container_width=True)
    uploaded_file = st.file_uploader("Upload Edited CSV", type=["csv"])

raw_df = load_data(uploaded_file)

section_title("Data readiness check")
ready_cols = st.columns(4)
with ready_cols[0]: kpi_card("Rows Loaded", f"{len(raw_df):,.0f}")
with ready_cols[1]: kpi_card("Reps", f"{raw_df['Rep'].nunique():,.0f}")
with ready_cols[2]: kpi_card("Lead Sources", f"{raw_df['Lead Source'].nunique():,.0f}")
with ready_cols[3]: kpi_card("Date Range", f"{raw_df['Date'].min().date()} to {raw_df['Date'].max().date()}")

section_title("Filters")
f1, f2, f3 = st.columns(3)
with f1:
    rep_options = sorted(raw_df["Rep"].dropna().unique())
    selected_reps = st.multiselect("Rep", rep_options, default=rep_options)
with f2:
    source_options = sorted(raw_df["Lead Source"].dropna().unique())
    selected_sources = st.multiselect("Lead Source", source_options, default=source_options)
with f3:
    selected_dates = st.date_input("Date Range", value=(raw_df["Date"].min().date(), raw_df["Date"].max().date()))

filtered_df = raw_df[raw_df["Rep"].isin(selected_reps) & raw_df["Lead Source"].isin(selected_sources)]
if selected_dates and len(selected_dates) == 2:
    filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(selected_dates[0])) & (filtered_df["Date"] <= pd.to_datetime(selected_dates[1]))]
if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

metrics = calculate_metrics(filtered_df)
targets = {"demo_rate": target_demo_rate, "close_rate": target_close_rate, "avg_sale": float(target_avg_sale), "nsli": float(target_nsli)}
rep_summary = build_summary(filtered_df, "Rep").sort_values("Revenue", ascending=False)
source_summary = build_summary(filtered_df, "Lead Source").sort_values("NSLI", ascending=False)
trends = build_trends(filtered_df)
diagnosis = generate_diagnosis(metrics, targets, rep_summary, source_summary)
priorities = build_priorities(diagnosis, metrics, targets)
health = operational_health_status(metrics, targets)
period_change = compare_periods(trends)
rules_brief = build_rules_manager_brief(metrics, diagnosis, priorities, health, period_change)
enhanced_brief = enhance_text(build_manager_prompt(rules_brief, metrics, targets), rules_brief, f"opspilot_brief_{hash(str(metrics) + str(targets))}")

section_title("Executive summary scorecard")
score_cols = st.columns(4)
with score_cols[0]: kpi_card("Operational Health", health)
with score_cols[1]: kpi_card("Primary Bottleneck", diagnosis["primary_bottleneck"])
with score_cols[2]: kpi_card("Best Manager Move", best_manager_move(diagnosis))
with score_cols[3]: kpi_card("Strongest Opportunity", f"Protect {diagnosis['best_source']['Lead Source']}")

section_title("Executive KPI snapshot")
for kpi_row in [[("Leads Issued", f"{metrics['total_leads']:,.0f}", None), ("Revenue", money(metrics["total_revenue"]), None), ("Demo Rate", pct(metrics["demo_rate"]), pct(target_demo_rate)), ("Close Rate", pct(metrics["close_rate"]), pct(target_close_rate))], [("Sales", f"{metrics['total_sales']:,.0f}", None), ("Demos", f"{metrics['total_demos']:,.0f}", None), ("Average Sale", money(metrics["avg_sale"]), money(target_avg_sale)), ("NSLI", money(metrics["nsli"]), money(target_nsli))]]:
    cols = st.columns(4)
    for col, (label, value, target) in zip(cols, kpi_row):
        with col:
            kpi_card(label, value, target)

section_title("What changed since last period?")
change_cols = st.columns(4)
with change_cols[0]: kpi_card("Revenue", direction(period_change["revenue_change"], is_money=True), period_change["label"])
with change_cols[1]: kpi_card("Demo Rate", direction(period_change["demo_change"], is_pct=True), period_change["label"])
with change_cols[2]: kpi_card("Close Rate", direction(period_change["close_change"], is_pct=True), period_change["label"])
with change_cols[3]: kpi_card("NSLI", direction(period_change["nsli_change"], is_money=True), period_change["label"])

section_title("Operational health")
health_cols = st.columns(2)
health_items = [("Demo Rate", metrics["demo_rate"], target_demo_rate, pct(metrics["demo_rate"]), pct(target_demo_rate)), ("Close Rate", metrics["close_rate"], target_close_rate, pct(metrics["close_rate"]), pct(target_close_rate)), ("Average Sale", metrics["avg_sale"], target_avg_sale, money(metrics["avg_sale"]), money(target_avg_sale)), ("NSLI", metrics["nsli"], target_nsli, money(metrics["nsli"]), money(target_nsli))]
for index, (name, value, target, display_value, display_target) in enumerate(health_items):
    status, status_class, description = evaluate_metric(value, target, name)
    card_class = {"status-high": "risk-high", "status-medium": "risk-medium", "status-healthy": "risk-healthy"}[status_class]
    with health_cols[index % 2]:
        html_card(name, f'<span class="status-pill {status_class}">{status}</span><p>Current: {display_value}. Target: {display_target}. {description}</p>', f"risk-card {card_class}")

section_title("Top 3 manager priorities")
html_card("Recommended Next Actions", "<ol>" + "".join(f"<li>{priority}</li>" for priority in priorities) + "</ol>")

section_title("AI operations diagnosis")
d1, d2, d3 = st.columns(3)
with d1: kpi_card("Primary Bottleneck", diagnosis["primary_bottleneck"])
with d2: kpi_card("Priority Level", diagnosis["priority"])
with d3: kpi_card("Rep to Review", diagnosis["review_rep"]["Rep"])
html_card("Manager Diagnosis", f"<p><strong>Likely cause:</strong> {diagnosis['likely_cause']}</p><p><strong>Recommended manager action:</strong> {diagnosis['manager_action']}</p><p><strong>Recommended coaching move:</strong> {diagnosis['coaching_move']}</p><p><strong>Suggested roleplay:</strong> {diagnosis['roleplay']}</p>")

section_title("Trend analysis", "Trend charts show whether performance is improving or slipping across the filtered date range.")
tabs = st.tabs(["Revenue", "Demo Rate", "Close Rate", "NSLI"])
with tabs[0]: st.line_chart(trends.set_index("Date")["Revenue"])
with tabs[1]: st.line_chart(trends.set_index("Date")["Demo Rate"])
with tabs[2]: st.line_chart(trends.set_index("Date")["Close Rate"])
with tabs[3]: st.line_chart(trends.set_index("Date")["NSLI"])

section_title("Rep performance")
st.dataframe(format_summary_table(rep_summary), use_container_width=True, hide_index=True)
st.bar_chart(rep_summary.set_index("Rep")["Revenue"])

section_title("Rep coaching cards")
coach_cols = st.columns(2)
for position, (_, row) in enumerate(rep_summary.iterrows()):
    notes = rep_coaching_note(row, targets)
    with coach_cols[position % 2]:
        html_card(row["Rep"], f"<p><strong>Revenue:</strong> {money(row['Revenue'])} | <strong>NSLI:</strong> {money(row['NSLI'])}</p><ul>" + "".join(f"<li>{note}</li>" for note in notes[:3]) + "</ul>", "coach-card")

section_title("Lead source performance")
st.dataframe(format_summary_table(source_summary), use_container_width=True, hide_index=True)
st.bar_chart(source_summary.set_index("Lead Source")["NSLI"])

section_title("Manager brief")
html_card("Executive Summary", md_to_html(enhanced_brief))

section_title("Weekly sales meeting agenda")
html_card("Recommended Agenda", f"<ol><li><strong>Wins:</strong> Recognize {diagnosis['best_rep']['Rep']} and {diagnosis['best_source']['Lead Source']}.</li><li><strong>Numbers in focus:</strong> Review demo rate, close rate, average sale, and NSLI against targets.</li><li><strong>Bottleneck discussion:</strong> Focus on {diagnosis['primary_bottleneck']}.</li><li><strong>Roleplay:</strong> {diagnosis['roleplay']}</li><li><strong>Action commitments:</strong> Each rep commits to one measurable action before the next meeting.</li></ol>")

section_title("Downloads")
report = build_manager_report(metrics, targets, diagnosis, priorities, health, period_change, enhanced_brief)
download_col1, download_col2 = st.columns(2)
with download_col1:
    st.download_button("Download Manager Report", data=report, file_name="opspilot-manager-report.md", mime="text/markdown", use_container_width=True)
with download_col2:
    st.download_button("Download Filtered Data CSV", data=filtered_df.to_csv(index=False), file_name="opspilot-filtered-data.csv", mime="text/csv", use_container_width=True)

section_title("What this app demonstrates")
html_card("Portfolio Skills Shown", "<ul><li>AI-enhanced manager brief with rules-based fallback</li><li>CSV intake and data validation</li><li>KPI calculation and target comparison</li><li>Rules-based operational diagnosis</li><li>Trend comparison logic</li><li>Manager-ready reporting and exports</li></ul>", "coach-card")

with st.expander("How to use OpsPilot AI"):
    st.markdown("1. Download or upload a CSV.\n2. Adjust KPI targets in the sidebar.\n3. Review the executive scorecard, KPI snapshot, operational health, and trend comparison.\n4. Review rep and lead source performance.\n5. Download the manager report or filtered data CSV.")

st.markdown('<div class="note-box">Privacy note: Uploaded CSV files are processed during the active app session and are not saved by this app.</div>', unsafe_allow_html=True)
with st.expander("View filtered raw data"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
