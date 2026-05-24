# OpsPilot AI

OpsPilot AI is an AI-enhanced operations intelligence dashboard for field-sales and home-service teams. It converts daily sales activity into KPI reporting, rep performance insights, lead source analysis, trend visibility, coaching priorities, manager-ready action plans, and downloadable reports.

## Live Demo

[Launch OpsPilot AI](https://opspilot-ai.streamlit.app/)

## Current Version: v2.4

OpsPilot AI combines a rules-based KPI engine with embedded AI-enhanced manager brief generation.

The app is designed to work in two layers:

1. **Rules-based core:** validates CSV data, calculates KPIs, compares targets, analyzes reps and lead sources, detects bottlenecks, and creates manager priorities.
2. **Embedded AI layer:** when an OpenAI token is available, the app quietly enhances the Manager Brief with a more polished, manager-ready performance memo.

If the AI call fails or an API key is unavailable, the app silently falls back to the rules-based manager brief. The dashboard still works normally.

## Why this project exists

Small and mid-sized businesses often rely on scattered spreadsheets, CRM exports, daily reports, and manager notes to make operational decisions. OpsPilot AI gives operators a simple way to identify what is working, what needs attention, and what actions should happen next.

## What it analyzes

- Leads issued
- Demos
- Sales
- Revenue
- Demo rate
- Close rate
- Average sale
- Net sales per lead issued (NSLI)
- Rep performance
- Lead source performance
- Performance trends over time
- Coaching opportunities
- Manager action priorities

## Workflow Outputs

- Editable sample CSV download
- CSV upload workflow
- Data readiness check
- Adjustable KPI targets
- Executive summary scorecard
- Operational health status
- Primary bottleneck detection
- Period-over-period trend comparison
- Executive KPI snapshot
- Rep performance analysis
- Lead source performance analysis
- AI-enhanced manager brief with rules-based fallback
- Top 3 manager priorities
- Rep coaching cards
- Weekly sales meeting agenda
- Downloadable manager report
- Downloadable filtered data CSV

## Export Strategy

Current exports:

- Markdown manager report (`.md`) for GitHub-friendly and developer-friendly documentation
- Filtered CSV export for continued analysis

Planned next upgrade:

- PDF manager report for a more user-friendly executive/manager deliverable

The markdown export is useful for transparency and version control, but PDF is the better format for non-technical users.

## Required CSV Format

Users can download the editable sample CSV, replace the fictional data with their own activity data, and re-upload it.

Required columns:

```csv
Date,Rep,Lead Source,Leads Issued,Demos,Sales,Revenue
```

Example row:

```csv
2026-01-05,Alex Carter,Website,10,7,3,42000
```

## Suggested Test Flow

1. Launch the live demo.
2. Download the sample CSV from the app.
3. Re-upload the sample CSV or use the built-in sample workflow.
4. Review the executive scorecard, KPI snapshot, operational health grade, and trend comparison.
5. Review rep performance and lead source performance.
6. Review the embedded AI-enhanced Manager Brief.
7. Download the manager report.

## Screenshots

### Executive Scorecard and KPI Snapshot

![OpsPilot AI Executive Scorecard](screenshots/executive-scorecard.svg)

## Tech Stack

- Python
- Streamlit
- Pandas
- OpenAI API integration
- Rules-based KPI and diagnostic logic
- Silent AI fallback pattern
- CSV-based workflow
- Markdown report export
- GitHub
- Streamlit Community Cloud

## Run Locally

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Environment Variables

To enable embedded AI output:

```bash
OPENAI_TOKEN=your_api_key_here
```

The app still works without this token by using the rules-based fallback.

## Public Demo Note

All sample data, names, companies, and scenarios used in this project are fictional and created for public portfolio demonstration purposes.

## Case Study

### Problem

Small and mid-sized businesses often have sales activity data, but the information is scattered across spreadsheets, daily reports, CRM exports, and manager notes. This makes it harder to identify bottlenecks, coach reps, and decide what should happen next.

### Solution

OpsPilot AI converts sales activity data into a manager-ready operations dashboard with KPI visibility, trend analysis, rep performance, lead source performance, operational diagnosis, manager priorities, a meeting agenda, and downloadable reports. The embedded AI layer improves the manager brief when available while preserving a reliable rules-based fallback.

### Business Value

OpsPilot AI helps managers move from raw activity data to practical action. It can support faster performance reviews, better coaching conversations, cleaner meeting preparation, and stronger lead source visibility.

## Built By

Bradley Hankins  
Operations & Revenue Leader | AI Workflow Automation | RevOps & Process Improvement
