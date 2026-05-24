import streamlit as st

from ai_helpers import generate_ai_text

st.set_page_config(page_title="OpsPilot AI - AI Manager Brief", page_icon="📊", layout="wide")

st.title("AI Manager Brief")
st.caption("Optional AI enhancement for turning KPI results into a manager-ready performance memo.")

st.info(
    "This page is optional. The main OpsPilot dashboard still works without AI. "
    "Set OPENAI_TOKEN in the deployment environment to enable AI output."
)

kpi_context = st.text_area(
    "KPI results / dashboard notes",
    height=220,
    placeholder="Paste KPI snapshot, trends, rep performance notes, lead source notes, or manager priorities from OpsPilot.",
)
manager_focus = st.selectbox(
    "Manager focus",
    ["Weekly performance memo", "Sales meeting prep", "Rep coaching plan", "Lead source review", "Branch health summary"],
)
team_context = st.text_area(
    "Optional team context",
    height=140,
    placeholder="Add context such as team size, goals, recent changes, staffing issues, or current focus areas.",
)

if st.button("Generate AI Manager Brief", use_container_width=True):
    prompt = f"""
You are an operations and sales performance manager.
Turn the KPI notes into a concise manager-ready brief.
Use the provided data only. Do not invent numbers.
Make the output practical and action-oriented.

Manager focus: {manager_focus}

KPI results / dashboard notes:
{kpi_context}

Team context:
{team_context}

Return:
1. Executive summary
2. What changed
3. Primary bottleneck
4. Rep or team coaching focus
5. Lead source or pipeline focus
6. Recommended meeting agenda
7. Three manager action items
"""
    with st.spinner("Generating AI manager brief..."):
        st.markdown(generate_ai_text(prompt))

st.divider()
st.markdown(
    "**AI positioning:** This page adds a natural-language manager memo layer on top of OpsPilot's KPI calculations and rules-based diagnosis."
)
