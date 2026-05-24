import streamlit as st
import pandas as pd

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

st.markdown("""
<style>
.block-container{max-width:1180px;padding-top:1.35rem;padding-bottom:3rem}[data-testid="stSidebar"]{background:#111827}[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label{color:#f9fafb!important}.hero{padding:1.9rem 2rem;border-radius:20px;background:linear-gradient(135deg,#111827 0%,#1f2937 52%,#334155 100%);color:#fff;box-shadow:0 18px 36px rgba(17,24,39,.18);margin-bottom:1rem;border:1px solid rgba(255,255,255,.08)}.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:.75rem;font-weight:800;color:#93c5fd;margin-bottom:.65rem}.hero-title{font-size:2.25rem;line-height:1.08;font-weight:850;margin-bottom:.65rem}.hero-subtitle{font-size:1.02rem;line-height:1.62;color:#e5e7eb;max-width:900px}.hero-pills span{display:inline-block;padding:.35rem .65rem;margin:.75rem .28rem 0 0;border-radius:999px;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);font-weight:700;font-size:.78rem;color:#f8fafc}.section-title{margin-top:1.25rem;margin-bottom:.55rem;font-size:1.4rem;font-weight:850;color:#111827}.section-lede{color:#4b5563;line-height:1.6;margin-bottom:1rem;max-width:950px}.kpi-card,.brief-card,.risk-card,.upload-card,.coach-card{background:#fff;border:1px solid #e5e7eb;border-radius:18px;box-shadow:0 8px 20px rgba(15,23,42,.055)}.kpi-card{height:138px;padding:1rem;display:flex;flex-direction:column;justify-content:flex-start;margin-bottom:.75rem}.kpi-label{color:#6b7280;font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}.kpi-value{color:#111827;font-size:1.52rem;line-height:1.16;font-weight:900;overflow-wrap:break-word}.kpi-target{margin-top:.55rem;color:#64748b;font-size:.85rem;line-height:1.35}.upload-card,.brief-card,.risk-card,.coach-card{padding:1.15rem;margin-bottom:.8rem}.upload-card{border-left:5px solid #1d4ed8}.brief-card{border-left:5px solid #111827}.coach-card{border-left:5px solid #1d4ed8;min-height:185px}.upload-card h3,.brief-card h3,.risk-card h3,.coach-card h3{font-size:1.05rem;font-weight:850;color:#111827;margin-bottom:.4rem}.upload-card p,.upload-card li,.brief-card p,.brief-card li,.risk-card p,.risk-card li,.coach-card p,.coach-card li{color:#4b5563;line-height:1.52;font-size:.93rem}.risk-high{border-left:5px solid #dc2626}.risk-medium{border-left:5px solid #f59e0b}.risk-healthy{border-left:5px solid #059669}.status-pill{display:inline-block;padding:.25rem .6rem;border-radius:999px;font-weight:850;font-size:.78rem;margin-bottom:.5rem}.status-high{background:#fee2e2;color:#991b1b;border:1px solid #fecaca}.status-medium{background:#fef3c7;color:#92400e;border:1px solid #fde68a}.status-healthy{background:#d1fae5;color:#065f46;border:1px solid #a7f3d0}.note-box{padding:.9rem 1rem;border-radius:14px;background:#f8fafc;color:#334155;border:1px solid #e2e8f0;font-weight:650;margin:.9rem 0;font-size:.92rem}
</style>
""", unsafe_allow_html=True)

def money(v): return f"${v:,.0f}"
def pct(v): return f"{v:.1%}"
def safe_divide(n, d): return n / d if d else 0

def clean_currency_column(series):
    return series.astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False).str.strip().replace("", "0").astype(float)

def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        from io import StringIO
        try: df = pd.read_csv("sample_data.csv")
        except FileNotFoundError: df = pd.read_csv(StringIO(EDITABLE_SAMPLE_CSV))
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}"); st.stop()
    df = df.copy(); df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for c in ["Leads Issued", "Demos", "Sales"]: df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["Revenue"] = clean_currency_column(df["Revenue"])
    df = df.dropna(subset=["Date"])
    if df.empty: st.error("The uploaded file did not contain usable dated rows after cleanup."); st.stop()
    return df

def build_summary(df, group_col):
    s = df.groupby(group_col, as_index=False).agg({"Leads Issued":"sum","Demos":"sum","Sales":"sum","Revenue":"sum"})
    s["Demo Rate"] = s.apply(lambda r: safe_divide(r["Demos"], r["Leads Issued"]), axis=1)
    s["Close Rate"] = s.apply(lambda r: safe_divide(r["Sales"], r["Demos"]), axis=1)
    s["Average Sale"] = s.apply(lambda r: safe_divide(r["Revenue"], r["Sales"]), axis=1)
    s["NSLI"] = s.apply(lambda r: safe_divide(r["Revenue"], r["Leads Issued"]), axis=1)
    return s

def format_summary_table(df):
    f = df.copy()
    for c in ["Revenue", "Average Sale", "NSLI"]: f[c] = f[c].apply(money)
    for c in ["Demo Rate", "Close Rate"]: f[c] = f[c].apply(pct)
    return f

def evaluate_metric(value, target, metric_name):
    if value >= target: return "Healthy", "status-healthy", f"{metric_name} is meeting or exceeding the target."
    if value >= target * .85: return "Watch", "status-medium", f"{metric_name} is close to target but should be watched."
    return "Risk", "status-high", f"{metric_name} is materially below target and needs manager attention."

def kpi_card(label, value, target=None):
    target_html = f'<div class="kpi-target">Target: {target}</div>' if target else ""
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{target_html}</div>', unsafe_allow_html=True)

def risk_card(title, status, status_class, description):
    card_class = {"status-high":"risk-high","status-medium":"risk-medium","status-healthy":"risk-healthy"}.get(status_class,"risk-medium")
    st.markdown(f'<div class="risk-card {card_class}"><span class="status-pill {status_class}">{status}</span><h3>{title}</h3><p>{description}</p></div>', unsafe_allow_html=True)

def build_trends(df):
    t = df.groupby("Date", as_index=False).agg({"Leads Issued":"sum","Demos":"sum","Sales":"sum","Revenue":"sum"}).sort_values("Date")
    t["Demo Rate"] = t.apply(lambda r: safe_divide(r["Demos"], r["Leads Issued"]), axis=1)
    t["Close Rate"] = t.apply(lambda r: safe_divide(r["Sales"], r["Demos"]), axis=1)
    t["NSLI"] = t.apply(lambda r: safe_divide(r["Revenue"], r["Leads Issued"]), axis=1)
    return t

def generate_diagnosis(metrics, targets, rep_summary, source_summary):
    checks = [("Demo Rate", metrics["demo_rate"], targets["demo_rate"]), ("Close Rate", metrics["close_rate"], targets["close_rate"]), ("Average Sale", metrics["avg_sale"], targets["avg_sale"]), ("NSLI", metrics["nsli"], targets["nsli"])]
    gaps = [(n, safe_divide(t-v, t), v, t) for n, v, t in checks]
    primary_name, primary_gap, _, _ = max(gaps, key=lambda x: x[1])
    best_rep = rep_summary.sort_values("Revenue", ascending=False).iloc[0]
    review_rep = rep_summary.sort_values("NSLI", ascending=True).iloc[0]
    best_source = source_summary.sort_values("NSLI", ascending=False).iloc[0]
    review_source = source_summary.sort_values("NSLI", ascending=True).iloc[0]
    if primary_gap <= 0:
        priority, likely, action, coaching, roleplay = "Healthy", "The selected data is meeting the configured targets. Protect what is working and standardize the behaviors behind the strongest results.", "Study the top rep and strongest lead source, then document the process that should become the team standard.", "Use coaching time for advanced skill sharpening rather than basic correction.", "Customer says: 'Everything sounds good, but I want to make sure we are making the right decision.'"
    elif primary_name == "Demo Rate":
        priority, likely, action, coaching, roleplay = ("High" if primary_gap > .15 else "Medium"), "The team is not converting enough issued leads into completed demos. This may point to weak appointment setting, poor confirmation, low customer commitment, scheduling friction, or lead quality issues.", "Review issued leads that did not demo. Look for patterns by rep, lead source, appointment window, and confirmation process.", "Coach reps on expectation setting, decision-maker confirmation, urgency, and reducing no-show risk.", "Customer says: 'Just come out and give me a quick quote. I may not have much time.'"
    elif primary_name == "Close Rate":
        priority, likely, action, coaching, roleplay = ("High" if primary_gap > .15 else "Medium"), "The team is getting demos but not converting enough into sales. This may point to weak discovery, poor value build, price resistance, lack of urgency, or inconsistent closing language.", "Review recent unsold demos and identify the most common objection. Build the next meeting around that single closing skill.", "Coach reps on discovery, value stacking, financing confidence, urgency, and direct commitment language.", "Customer says: 'We need to think about it and get a few more quotes.'"
    elif primary_name == "Average Sale":
        priority, likely, action, coaching, roleplay = "Medium", "The team is closing work, but project size is below target. This may indicate incomplete scopes, weak upgrade positioning, missed add-ons, or reps defaulting to the lowest option.", "Audit recent sold jobs and compare the presented scope against the full opportunity. Look for missed upgrades, add-ons, and scope completeness.", "Coach reps on good/better/best options, long-term value, and add-ons that solve real customer problems.", "Customer says: 'We just want the cheapest option that gets the job done.'"
    else:
        priority, likely, action, coaching, roleplay = "Medium", "Revenue per issued lead is below target. This may come from lead quality, rep assignment, low demo rate, low close rate, or smaller job size.", "Compare NSLI by rep and lead source. Shift attention toward the best-performing source and review whether low-performing sources need better qualification.", "Coach the team on prioritizing high-intent opportunities, follow-up speed, and conversion discipline on every issued lead.", "Customer says: 'I’m not sure if this is something we’re ready to do right now.'"
    return {"primary_bottleneck": primary_name if primary_gap > 0 else "No Critical Bottleneck", "priority": priority, "likely_cause": likely, "manager_action": action, "coaching_move": coaching, "roleplay": roleplay, "best_rep": best_rep, "review_rep": review_rep, "best_source": best_source, "review_source": review_source}

def build_priorities(diagnosis, metrics, targets):
    items = [f"Coach {diagnosis['review_rep']['Rep']} around {diagnosis['primary_bottleneck']} and review their next 3 opportunities.", f"Audit {diagnosis['review_source']['Lead Source']} lead quality before increasing spend or activity there.", f"Protect {diagnosis['best_source']['Lead Source']} and study why it is producing stronger NSLI."]
    if metrics["demo_rate"] < targets["demo_rate"]: items[0] = "Review no-demo leads and tighten appointment confirmation/expectation setting."
    if metrics["close_rate"] < targets["close_rate"]: items[0] = "Review unsold demos and roleplay the most common closing objection this week."
    if metrics["avg_sale"] < targets["avg_sale"]: items.append("Audit sold scopes for missed upgrades, add-ons, and incomplete project value presentation.")
    return items[:3]

def rep_coaching_note(row, targets):
    issues = []
    if row["Leads Issued"] < 5: issues.append("Lead volume is low, so review activity volume before judging conversion.")
    if row["Demo Rate"] < targets["demo_rate"]: issues.append("Demo rate is below target; coach confirmation, expectation setting, and lead commitment.")
    if row["Close Rate"] < targets["close_rate"] and row["Demos"] >= 1: issues.append("Close rate is below target; coach discovery, value build, urgency, and objection handling.")
    if row["Average Sale"] < targets["avg_sale"] and row["Sales"] >= 1: issues.append("Average sale is below target; review scope completeness and upgrade/add-on positioning.")
    if row["NSLI"] < targets["nsli"]: issues.append("NSLI is below target; review lead quality, conversion discipline, and follow-up speed.")
    if not issues: issues.append("Performance is healthy against current targets; study and document what is working.")
    return issues

def build_manager_report(metrics, targets, diagnosis, priorities):
    priority_lines = "\n".join([f"{i+1}. {p}" for i, p in enumerate(priorities)])
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

with st.sidebar:
    st.title("OpsPilot AI"); st.caption("Version 2.2")
    st.markdown("Operations intelligence for field-sales and home-service teams. Adjust KPI targets below to match the business model being analyzed.")
    st.divider(); st.header("KPI Targets")
    target_demo_rate = st.slider("Target Demo Rate", .30, .90, .60, .05)
    target_close_rate = st.slider("Target Close Rate", .10, .70, .35, .05)
    target_avg_sale = st.number_input("Target Average Sale", min_value=1000, max_value=100000, value=12000, step=500)
    target_nsli = st.number_input("Target NSLI", min_value=500, max_value=50000, value=4000, step=250)

st.markdown('<div class="hero"><div class="eyebrow">Operations Intelligence Dashboard</div><div class="hero-title">OpsPilot AI</div><div class="hero-subtitle">Turn sales activity data into KPI visibility, rep performance insights, lead source analysis, coaching priorities, manager briefs, and meeting-ready action plans.</div><div class="hero-pills"><span>Operations</span><span>RevOps</span><span>KPI Reporting</span><span>Manager Briefs</span><span>Streamlit</span></div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Upload sales activity data</div>', unsafe_allow_html=True)
st.markdown('<div class="section-lede">Download the editable sample CSV, replace the fictional rows with your own activity data, then upload the edited file to generate the dashboard.</div>', unsafe_allow_html=True)
up1, up2 = st.columns([2, 1])
with up1:
    st.markdown('<div class="upload-card"><h3>CSV format</h3><p>Your file must include these columns: <strong>Date, Rep, Lead Source, Leads Issued, Demos, Sales, Revenue</strong>.</p><p>The sample file uses fictional placeholder reps and lead sources so it can be safely edited for testing.</p></div>', unsafe_allow_html=True)
with up2:
    st.download_button("Download Editable Sample CSV", data=EDITABLE_SAMPLE_CSV, file_name="opspilot-editable-sample.csv", mime="text/csv", use_container_width=True)
    uploaded_file = st.file_uploader("Upload Edited CSV", type=["csv"])
raw_df = load_data(uploaded_file)

st.markdown('<div class="section-title">Data readiness check</div>', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
with r1: kpi_card("Rows Loaded", f"{len(raw_df):,.0f}")
with r2: kpi_card("Reps", f"{raw_df['Rep'].nunique():,.0f}")
with r3: kpi_card("Lead Sources", f"{raw_df['Lead Source'].nunique():,.0f}")
with r4: kpi_card("Date Range", f"{raw_df['Date'].min().date()} to {raw_df['Date'].max().date()}")

st.markdown('<div class="section-title">Filters</div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)
with f1:
    reps = sorted(raw_df["Rep"].dropna().unique()); selected_reps = st.multiselect("Rep", reps, default=reps)
with f2:
    sources = sorted(raw_df["Lead Source"].dropna().unique()); selected_sources = st.multiselect("Lead Source", sources, default=sources)
with f3:
    selected_dates = st.date_input("Date Range", value=(raw_df["Date"].min().date(), raw_df["Date"].max().date()))
filtered_df = raw_df[raw_df["Rep"].isin(selected_reps) & raw_df["Lead Source"].isin(selected_sources)]
if selected_dates and len(selected_dates) == 2:
    filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(selected_dates[0])) & (filtered_df["Date"] <= pd.to_datetime(selected_dates[1]))]
if filtered_df.empty: st.warning("No data matches the selected filters."); st.stop()

total_leads, total_demos, total_sales, total_revenue = filtered_df["Leads Issued"].sum(), filtered_df["Demos"].sum(), filtered_df["Sales"].sum(), filtered_df["Revenue"].sum()
metrics = {"total_leads":total_leads,"total_demos":total_demos,"total_sales":total_sales,"total_revenue":total_revenue,"demo_rate":safe_divide(total_demos,total_leads),"close_rate":safe_divide(total_sales,total_demos),"avg_sale":safe_divide(total_revenue,total_sales),"nsli":safe_divide(total_revenue,total_leads)}
targets = {"demo_rate":target_demo_rate,"close_rate":target_close_rate,"avg_sale":float(target_avg_sale),"nsli":float(target_nsli)}

st.markdown('<div class="section-title">Executive KPI snapshot</div>', unsafe_allow_html=True)
for cols in [("Leads Issued",f"{total_leads:,.0f}",None,"Revenue",money(total_revenue),None,"Demo Rate",pct(metrics["demo_rate"]),pct(target_demo_rate),"Close Rate",pct(metrics["close_rate"]),pct(target_close_rate)), ("Sales",f"{total_sales:,.0f}",None,"Demos",f"{total_demos:,.0f}",None,"Average Sale",money(metrics["avg_sale"]),money(target_avg_sale),"NSLI",money(metrics["nsli"]),money(target_nsli))]:
    c = st.columns(4)
    for i in range(4):
        with c[i]: kpi_card(cols[i*3], cols[i*3+1], cols[i*3+2])

rep_summary = build_summary(filtered_df, "Rep").sort_values("Revenue", ascending=False)
source_summary = build_summary(filtered_df, "Lead Source").sort_values("NSLI", ascending=False)
diagnosis = generate_diagnosis(metrics, targets, rep_summary, source_summary)
priorities = build_priorities(diagnosis, metrics, targets)

st.markdown('<div class="section-title">Operational health</div>', unsafe_allow_html=True)
h1, h2 = st.columns(2)
health_items = [("Demo Rate",metrics["demo_rate"],target_demo_rate,pct(metrics["demo_rate"]),pct(target_demo_rate)), ("Close Rate",metrics["close_rate"],target_close_rate,pct(metrics["close_rate"]),pct(target_close_rate)), ("Average Sale",metrics["avg_sale"],target_avg_sale,money(metrics["avg_sale"]),money(target_avg_sale)), ("NSLI",metrics["nsli"],target_nsli,money(metrics["nsli"]),money(target_nsli))]
for i, (name, value, target, shown, target_shown) in enumerate(health_items):
    status, status_class, desc = evaluate_metric(value, target, name)
    with [h1, h2][i % 2]: risk_card(name, status, status_class, f"Current: {shown}. Target: {target_shown}. {desc}")

st.markdown('<div class="section-title">Top 3 manager priorities</div>', unsafe_allow_html=True)
st.markdown('<div class="brief-card"><h3>Recommended Next Actions</h3><ol>' + ''.join([f'<li>{p}</li>' for p in priorities]) + '</ol></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">AI operations diagnosis</div>', unsafe_allow_html=True)
d1, d2, d3 = st.columns(3)
with d1: kpi_card("Primary Bottleneck", diagnosis["primary_bottleneck"])
with d2: kpi_card("Priority Level", diagnosis["priority"])
with d3: kpi_card("Rep to Review", diagnosis["review_rep"]["Rep"])
st.markdown(f'<div class="brief-card"><h3>Manager Diagnosis</h3><p><strong>Likely cause:</strong> {diagnosis["likely_cause"]}</p><p><strong>Recommended manager action:</strong> {diagnosis["manager_action"]}</p><p><strong>Recommended coaching move:</strong> {diagnosis["coaching_move"]}</p><p><strong>Suggested roleplay:</strong> {diagnosis["roleplay"]}</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Trend analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="section-lede">Trend charts show whether performance is improving or slipping across the filtered date range.</div>', unsafe_allow_html=True)
trends = build_trends(filtered_df)
tab1, tab2, tab3, tab4 = st.tabs(["Revenue", "Demo Rate", "Close Rate", "NSLI"])
with tab1: st.line_chart(trends.set_index("Date")["Revenue"])
with tab2: st.line_chart(trends.set_index("Date")["Demo Rate"])
with tab3: st.line_chart(trends.set_index("Date")["Close Rate"])
with tab4: st.line_chart(trends.set_index("Date")["NSLI"])

st.markdown('<div class="section-title">Rep performance</div>', unsafe_allow_html=True)
st.dataframe(format_summary_table(rep_summary), use_container_width=True, hide_index=True)
st.bar_chart(rep_summary.set_index("Rep")["Revenue"])

st.markdown('<div class="section-title">Rep coaching cards</div>', unsafe_allow_html=True)
coach_cols = st.columns(2)
for position, (_, row) in enumerate(rep_summary.iterrows()):
    notes = rep_coaching_note(row, targets)
    html = f'<div class="coach-card"><h3>{row["Rep"]}</h3><p><strong>Revenue:</strong> {money(row["Revenue"])} | <strong>NSLI:</strong> {money(row["NSLI"])}</p><ul>' + ''.join([f'<li>{n}</li>' for n in notes[:3]]) + '</ul></div>'
    with coach_cols[position % 2]: st.markdown(html, unsafe_allow_html=True)

st.markdown('<div class="section-title">Lead source performance</div>', unsafe_allow_html=True)
st.dataframe(format_summary_table(source_summary), use_container_width=True, hide_index=True)
st.bar_chart(source_summary.set_index("Lead Source")["NSLI"])

best_rep, review_rep, best_source, review_source = diagnosis["best_rep"], diagnosis["review_rep"], diagnosis["best_source"], diagnosis["review_source"]
st.markdown('<div class="section-title">Manager brief</div>', unsafe_allow_html=True)
st.markdown(f'<div class="brief-card"><h3>Executive Summary</h3><p>The team generated <strong>{money(total_revenue)}</strong> from <strong>{total_sales:,.0f} sales</strong> on <strong>{total_leads:,.0f} leads issued</strong>.</p><ul><li><strong>Top revenue producer:</strong> {best_rep["Rep"]} at {money(best_rep["Revenue"])}</li><li><strong>Rep to review:</strong> {review_rep["Rep"]} based on lowest NSLI</li><li><strong>Strongest lead source:</strong> {best_source["Lead Source"]} at {money(best_source["NSLI"])} NSLI</li><li><strong>Lead source to review:</strong> {review_source["Lead Source"]} at {money(review_source["NSLI"])} NSLI</li></ul></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Weekly sales meeting agenda</div>', unsafe_allow_html=True)
st.markdown(f'<div class="brief-card"><h3>Recommended Agenda</h3><ol><li><strong>Wins:</strong> Recognize {best_rep["Rep"]} and the strongest lead source, {best_source["Lead Source"]}.</li><li><strong>Numbers in focus:</strong> Review demo rate, close rate, average sale, and NSLI against targets.</li><li><strong>Bottleneck discussion:</strong> Focus on {diagnosis["primary_bottleneck"]}.</li><li><strong>Roleplay:</strong> {diagnosis["roleplay"]}</li><li><strong>Action commitments:</strong> Each rep commits to one measurable action before the next meeting.</li></ol></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Downloads</div>', unsafe_allow_html=True)
dl1, dl2 = st.columns(2)
with dl1:
    manager_report = build_manager_report(metrics, targets, diagnosis, priorities)
    st.download_button("Download Manager Report", data=manager_report, file_name="opspilot-manager-report.md", mime="text/markdown", use_container_width=True)
with dl2:
    st.download_button("Download Filtered Data CSV", data=filtered_df.to_csv(index=False), file_name="opspilot-filtered-data.csv", mime="text/csv", use_container_width=True)

with st.expander("How to use OpsPilot AI"):
    st.markdown("""
    1. Download the editable sample CSV.
    2. Replace the fictional sample rows with your own sales activity data.
    3. Upload the edited CSV file.
    4. Adjust KPI targets in the sidebar.
    5. Review the KPI snapshot, operational health, trend analysis, AI diagnosis, manager priorities, rep coaching cards, manager brief, and meeting agenda.
    6. Download the manager report or filtered data CSV.

    Required CSV columns: Date, Rep, Lead Source, Leads Issued, Demos, Sales, Revenue.
    """)
st.markdown('<div class="note-box">Privacy note: Uploaded CSV files are processed during the active app session and are not saved by this app.</div>', unsafe_allow_html=True)
with st.expander("View filtered raw data"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
