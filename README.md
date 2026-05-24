# OpsPilot AI

OpsPilot AI is an operations intelligence dashboard for field-sales and home-service teams. It converts daily sales activity into KPI reporting, rep performance insights, lead source analysis, trend visibility, coaching priorities, and manager-ready action plans.

## Live Demo

[Launch OpsPilot AI](https://opspilot-ai.streamlit.app/)

## Why this project exists

Small and mid-sized businesses often rely on scattered spreadsheets, CRM exports, daily reports, and manager notes to make operational decisions. OpsPilot AI gives operators a simple way to identify what is working, what needs attention, and what actions should happen next.

The goal is to help small and mid-sized businesses make faster, cleaner, data-driven decisions without needing enterprise-level RevOps software.

## Who this helps

OpsPilot AI is designed for:

- Home-service companies
- Field-sales teams
- Sales managers and operations leaders
- Small business owners who need better visibility
- Teams that manage leads, demos, sales activity, revenue, and follow-up performance

## Current Version: v2.2

OpsPilot AI v2.2 includes:

- Editable sample CSV download
- Public-safe fictional sample data
- CSV upload workflow
- Data readiness check
- Adjustable KPI targets
- Executive KPI snapshot
- Operational health grading
- Trend charts by date
- Rep performance analysis
- Lead source performance analysis
- AI-style operations diagnosis
- Top 3 manager priorities
- Rep coaching cards
- Manager brief
- Weekly sales meeting agenda
- Downloadable manager report
- Downloadable filtered data CSV

## What it analyzes

The dashboard calculates and evaluates:

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

## AI Operations Diagnosis

OpsPilot AI includes a rules-based AI-style diagnosis engine that translates KPI performance into practical management recommendations.

The diagnosis engine identifies:

- Primary operational bottleneck
- Priority level
- Likely cause
- Recommended manager action
- Recommended coaching move
- Suggested sales meeting roleplay
- Strongest rep
- Rep needing review
- Strongest lead source
- Lead source needing review

## Manager Outputs

OpsPilot AI generates manager-ready outputs, including:

- Top 3 manager priorities
- Rep coaching cards
- Executive manager brief
- Weekly sales meeting agenda
- Downloadable Markdown manager report
- Filtered CSV export based on current dashboard filters

## Screenshots

### KPI Dashboard

![OpsPilot AI KPI Dashboard](screenshots/dashboard-kpis.png)

### Rep Performance

![OpsPilot AI Rep Performance](screenshots/rep-performance.png)

### Lead Source Performance

![OpsPilot AI Lead Source Performance](screenshots/lead-source-performance.png)

### Manager Brief

![OpsPilot AI Manager Brief](screenshots/manager-brief.png)

### Weekly Sales Meeting Agenda

![OpsPilot AI Weekly Sales Meeting Agenda](screenshots/weekly-sales-agenda.png)

### AI Operations Diagnosis

![OpsPilot AI Operations Diagnosis](screenshots/ai-operations-diagnosis.png)

### Download Manager Report

![OpsPilot AI Download Manager Report](screenshots/download-manager-report.png)

## Tech Stack

- Python
- Streamlit
- Pandas
- GitHub
- Streamlit Community Cloud
- CSV-based workflow
- Markdown report export

## Public Demo Note

All sample data, names, companies, and scenarios used in this project are fictional and created for public portfolio demonstration purposes.

## Built By

Bradley Hankins  
Operations & Revenue Leader | AI Workflow Automation | RevOps & Process Improvement
