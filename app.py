import pandas as pd
import streamlit as st

from ai_helpers import enhance_text, stable_cache_key
from core.data_loader import data_quality_warnings, parse_csv
from core.diagnostics import (
    best_manager_move,
    build_priorities,
    evaluate_metric,
    generate_diagnosis,
    operational_health_status,
    rep_coaching_note,
)
from core.formatters import direction, md_to_html, money, pct
from core.metrics import build_summary, build_trends, calculate_metrics, compare_periods, format_summary_table
from core.prompts import build_manager_prompt
from core.report_builder import build_manager_report, build_rules_manager_brief
from data.sample_data import EDITABLE_SAMPLE_CSV, PRIVACY_NOTE
from pdf_helpers import markdown_to_pdf

st.set_page_config(page_title="OpsPilot AI", page_icon="📊", layout="wide")

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


def section_title(title: str, lede: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if lede:
        st.markdown(f'<div class="section-lede">{lede}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, target: str | None = None) -> None:
    target_html = f'<div class="kpi-target">Target: {target}</div>' if target else ""
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{target_html}</div>', unsafe_allow_html=True)


def html_card(title: str, body_html: str, css_class: str = "brief-card") -> None:
    st.markdown(f'<div class="{css_class}"><h3>{title}</h3>{body_html}</div>', unsafe_allow_html=True)


def render_sidebar() -> dict:
    with st.sidebar:
        st.title("OpsPilot AI")
        st.caption("Version 2.6")
        st.markdown("Operations intelligence for field-sales and home-service teams.")
        st.divider()
        st.header("KPI Targets")
        target_demo_rate = st.slider("Target Demo Rate", 0.30, 0.90, 0.60, 0.05)
        target_close_rate = st.slider("Target Close Rate", 0.10, 0.70, 0.35, 0.05)
        target_avg_sale = st.number_input("Target Average Sale", min_value=1000, max_value=100000, value=12000, step=500)
        target_nsli = st.number_input("Target NSLI", min_value=500, max_value=50000, value=4000, step=250)
    return {
        "demo_rate": target_demo_rate,
        "close_rate": target_close_rate,
        "avg_sale": float(target_avg_sale),
        "nsli": float(target_nsli),
    }


def render_hero() -> None:
    st.markdown(
        '<div class="hero"><div class="eyebrow">Operations Intelligence Dashboard</div><div class="hero-title">OpsPilot AI</div><div class="hero-subtitle">Turn sales activity data into KPI visibility, rep performance insights, lead source analysis, coaching priorities, manager briefs, and meeting-ready action plans.</div><div class="hero-pills"><span>Operations</span><span>RevOps</span><span>KPI Reporting</span><span>Manager Briefs</span><span>Streamlit</span></div></div>',
        unsafe_allow_html=True,
    )


def render_upload_section():
    section_title("Upload sales activity data", "Download the editable sample CSV, replace the fictional rows with your own activity data, then upload the edited file to generate the dashboard.")
    upload_info_col, upload_action_col = st.columns([2, 1])
    with upload_info_col:
        html_card(
            "CSV format",
            "<p>Your file must include these columns: <strong>Date, Rep, Lead Source, Leads Issued, Demos, Sales, Revenue</strong>.</p><p>The sample file uses fictional placeholder reps and lead sources for safe testing.</p>",
            "upload-card",
        )
    with upload_action_col:
        st.download_button("Download Editable Sample CSV", data=EDITABLE_SAMPLE_CSV, file_name="opspilot-editable-sample.csv", mime="text/csv", use_container_width=True)
        return st.file_uploader("Upload Edited CSV", type=["csv"])


def load_dashboard_data(uploaded_file):
    try:
        raw_df = parse_csv(uploaded_file)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    warnings = data_quality_warnings(raw_df)
    if warnings:
        st.warning("Data quality warning: " + " ".join(warnings))
    return raw_df


def render_data_readiness(raw_df: pd.DataFrame) -> None:
    section_title("Data readiness check")
    ready_cols = st.columns(4)
    with ready_cols[0]:
        kpi_card("Rows Loaded", f"{len(raw_df):,.0f}")
    with ready_cols[1]:
        kpi_card("Reps", f"{raw_df['Rep'].nunique():,.0f}")
    with ready_cols[2]:
        kpi_card("Lead Sources", f"{raw_df['Lead Source'].nunique():,.0f}")
    with ready_cols[3]:
        kpi_card("Date Range", f"{raw_df['Date'].min().date()} to {raw_df['Date'].max().date()}")


def apply_filters(raw_df: pd.DataFrame) -> pd.DataFrame:
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
    return filtered_df


def build_analysis(filtered_df: pd.DataFrame, targets: dict) -> dict:
    metrics = calculate_metrics(filtered_df)
    rep_summary = build_summary(filtered_df, "Rep").sort_values("Revenue", ascending=False)
    source_summary = build_summary(filtered_df, "Lead Source").sort_values("NSLI", ascending=False)
    trends = build_trends(filtered_df)
    diagnosis = generate_diagnosis(metrics, targets, rep_summary, source_summary)
    priorities = build_priorities(diagnosis, metrics, targets)
    health = operational_health_status(metrics, targets)
    period_change = compare_periods(trends)
    rules_brief = build_rules_manager_brief(metrics, diagnosis, priorities, health, period_change)
    enhanced_brief = enhance_text(
        build_manager_prompt(rules_brief, metrics, targets),
        rules_brief,
        stable_cache_key("opspilot_brief", {"metrics": metrics, "targets": targets}),
    )
    return {
        "metrics": metrics,
        "rep_summary": rep_summary,
        "source_summary": source_summary,
        "trends": trends,
        "diagnosis": diagnosis,
        "priorities": priorities,
        "health": health,
        "period_change": period_change,
        "enhanced_brief": enhanced_brief,
    }


def render_scorecards(analysis: dict, targets: dict) -> None:
    metrics = analysis["metrics"]
    diagnosis = analysis["diagnosis"]
    period_change = analysis["period_change"]

    section_title("Executive summary scorecard")
    score_cols = st.columns(4)
    with score_cols[0]:
        kpi_card("Operational Health", analysis["health"])
    with score_cols[1]:
        kpi_card("Primary Bottleneck", diagnosis["primary_bottleneck"])
    with score_cols[2]:
        kpi_card("Best Manager Move", best_manager_move(diagnosis))
    with score_cols[3]:
        kpi_card("Strongest Opportunity", f"Protect {diagnosis['best_source']['Lead Source']}")

    section_title("Executive KPI snapshot")
    for kpi_row in [
        [("Leads Issued", f"{metrics['total_leads']:,.0f}", None), ("Revenue", money(metrics["total_revenue"]), None), ("Demo Rate", pct(metrics["demo_rate"]), pct(targets["demo_rate"])), ("Close Rate", pct(metrics["close_rate"]), pct(targets["close_rate"]))],
        [("Sales", f"{metrics['total_sales']:,.0f}", None), ("Demos", f"{metrics['total_demos']:,.0f}", None), ("Average Sale", money(metrics["avg_sale"]), money(targets["avg_sale"])), ("NSLI", money(metrics["nsli"]), money(targets["nsli"]))],
    ]:
        cols = st.columns(4)
        for col, (label, value, target) in zip(cols, kpi_row):
            with col:
                kpi_card(label, value, target)

    section_title("What changed since last period?")
    change_cols = st.columns(4)
    with change_cols[0]:
        kpi_card("Revenue", direction(period_change["revenue_change"], is_money=True), period_change["label"])
    with change_cols[1]:
        kpi_card("Demo Rate", direction(period_change["demo_change"], is_pct=True), period_change["label"])
    with change_cols[2]:
        kpi_card("Close Rate", direction(period_change["close_change"], is_pct=True), period_change["label"])
    with change_cols[3]:
        kpi_card("NSLI", direction(period_change["nsli_change"], is_money=True), period_change["label"])


def render_operational_health(metrics: dict, targets: dict) -> None:
    section_title("Operational health")
    health_cols = st.columns(2)
    health_items = [
        ("Demo Rate", metrics["demo_rate"], targets["demo_rate"], pct(metrics["demo_rate"]), pct(targets["demo_rate"])),
        ("Close Rate", metrics["close_rate"], targets["close_rate"], pct(metrics["close_rate"]), pct(targets["close_rate"])),
        ("Average Sale", metrics["avg_sale"], targets["avg_sale"], money(metrics["avg_sale"]), money(targets["avg_sale"])),
        ("NSLI", metrics["nsli"], targets["nsli"], money(metrics["nsli"]), money(targets["nsli"])),
    ]
    for index, (name, value, target, display_value, display_target) in enumerate(health_items):
        status, status_class, description = evaluate_metric(value, target, name)
        card_class = {"status-high": "risk-high", "status-medium": "risk-medium", "status-healthy": "risk-healthy"}[status_class]
        with health_cols[index % 2]:
            html_card(name, f'<span class="status-pill {status_class}">{status}</span><p>Current: {display_value}. Target: {display_target}. {description}</p>', f"risk-card {card_class}")


def render_diagnosis(analysis: dict) -> None:
    diagnosis = analysis["diagnosis"]
    section_title("Top 3 manager priorities")
    html_card("Recommended Next Actions", "<ol>" + "".join(f"<li>{priority}</li>" for priority in analysis["priorities"]) + "</ol>")

    section_title("AI operations diagnosis")
    d1, d2, d3 = st.columns(3)
    with d1:
        kpi_card("Primary Bottleneck", diagnosis["primary_bottleneck"])
    with d2:
        kpi_card("Priority Level", diagnosis["priority"])
    with d3:
        kpi_card("Rep to Review", diagnosis["review_rep"]["Rep"])
    html_card("Manager Diagnosis", f"<p><strong>Likely cause:</strong> {diagnosis['likely_cause']}</p><p><strong>Recommended manager action:</strong> {diagnosis['manager_action']}</p><p><strong>Recommended coaching move:</strong> {diagnosis['coaching_move']}</p><p><strong>Suggested roleplay:</strong> {diagnosis['roleplay']}</p>")


def render_trends(trends: pd.DataFrame) -> None:
    section_title("Trend analysis", "Trend charts show whether performance is improving or slipping across the filtered date range.")
    tabs = st.tabs(["Revenue", "Demo Rate", "Close Rate", "NSLI"])
    with tabs[0]:
        st.line_chart(trends.set_index("Date")["Revenue"])
    with tabs[1]:
        st.line_chart(trends.set_index("Date")["Demo Rate"])
    with tabs[2]:
        st.line_chart(trends.set_index("Date")["Close Rate"])
    with tabs[3]:
        st.line_chart(trends.set_index("Date")["NSLI"])


def render_rep_and_source_sections(analysis: dict, targets: dict) -> None:
    rep_summary = analysis["rep_summary"]
    source_summary = analysis["source_summary"]

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


def render_manager_outputs(analysis: dict, filtered_df: pd.DataFrame, targets: dict) -> None:
    diagnosis = analysis["diagnosis"]
    section_title("Manager brief")
    html_card("Executive Summary", md_to_html(analysis["enhanced_brief"]))

    section_title("Weekly sales meeting agenda")
    html_card("Recommended Agenda", f"<ol><li><strong>Wins:</strong> Recognize {diagnosis['best_rep']['Rep']} and {diagnosis['best_source']['Lead Source']}.</li><li><strong>Numbers in focus:</strong> Review demo rate, close rate, average sale, and NSLI against targets.</li><li><strong>Bottleneck discussion:</strong> Focus on {diagnosis['primary_bottleneck']}.</li><li><strong>Roleplay:</strong> {diagnosis['roleplay']}</li><li><strong>Action commitments:</strong> Each rep commits to one measurable action before the next meeting.</li></ol>")

    section_title("Downloads")
    report = build_manager_report(analysis["metrics"], targets, diagnosis, analysis["priorities"], analysis["health"], analysis["period_change"], analysis["enhanced_brief"])
    pdf_report = markdown_to_pdf(report, title="OpsPilot AI Manager Report")
    download_col1, download_col2 = st.columns(2)
    with download_col1:
        st.download_button("Download Manager Report PDF", data=pdf_report, file_name="opspilot-manager-report.pdf", mime="application/pdf", use_container_width=True)
    with download_col2:
        st.download_button("Download Filtered Data CSV", data=filtered_df.to_csv(index=False), file_name="opspilot-filtered-data.csv", mime="text/csv", use_container_width=True)


def main() -> None:
    targets = render_sidebar()
    render_hero()
    st.markdown(f'<div class="note-box">{PRIVACY_NOTE}</div>', unsafe_allow_html=True)

    uploaded_file = render_upload_section()
    raw_df = load_dashboard_data(uploaded_file)
    render_data_readiness(raw_df)
    filtered_df = apply_filters(raw_df)

    analysis = build_analysis(filtered_df, targets)
    render_scorecards(analysis, targets)
    render_operational_health(analysis["metrics"], targets)
    render_diagnosis(analysis)
    render_trends(analysis["trends"])
    render_rep_and_source_sections(analysis, targets)
    render_manager_outputs(analysis, filtered_df, targets)

    section_title("What this app demonstrates")
    html_card("Portfolio Skills Shown", "<ul><li>Modular Streamlit architecture</li><li>AI-enhanced manager brief with rules-based fallback</li><li>CSV intake and data validation</li><li>KPI calculation and target comparison</li><li>Rules-based operational diagnosis</li><li>User-friendly PDF manager reporting</li></ul>", "coach-card")

    with st.expander("How to use OpsPilot AI"):
        st.markdown("1. Download or upload a CSV.\n2. Adjust KPI targets in the sidebar.\n3. Review the executive scorecard, KPI snapshot, operational health, and trend comparison.\n4. Review rep and lead source performance.\n5. Download the manager report PDF or filtered data CSV.")

    st.markdown(f'<div class="note-box">{PRIVACY_NOTE}</div>', unsafe_allow_html=True)
    with st.expander("View filtered raw data"):
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
