# Architecture

OpsPilot AI is a Streamlit operations intelligence dashboard designed for field-sales and home-service teams.

## Current Architecture

The current version is optimized for simple Streamlit Community Cloud deployment while keeping the workflow easy to review in GitHub.

```text
app.py
README.md
requirements.txt
screenshots/
```

## Application Layers

The app is currently deployed from one Streamlit entrypoint, but the logic is organized conceptually into distinct layers:

```text
Configuration
- Required CSV columns
- Sample data
- KPI target defaults

Data Processing
- CSV loading
- Data validation
- Currency cleanup
- KPI calculations
- Rep and lead source summaries

Business Logic
- Operational health checks
- Bottleneck diagnosis
- Period-over-period comparison
- Manager priority generation
- Rep coaching note logic

Reporting
- Manager brief
- Weekly sales meeting agenda
- Downloadable Markdown report
- Filtered CSV export

Presentation
- Streamlit layout
- KPI cards
- Charts
- Tables
- Dashboard sections
```

## Design Choices

OpsPilot intentionally uses rules-based analytics instead of relying on hidden model output. This makes the tool easier to inspect, explain, and adapt for business users.

Key design goals:

- Clear KPI definitions
- Transparent calculations
- Editable sample CSV workflow
- Manager-ready output
- Lightweight deployment
- Public-safe fictional sample data

## Why Single-File for This Version

The current portfolio version keeps the deployment simple and easy to inspect. For a production codebase, the app would be split into modules.

## Future Production Layout

```text
app.py
src/
  config.py
  data_loader.py
  metrics.py
  diagnosis.py
  reports.py
  components.py
  styles.css
tests/
  test_metrics.py
  test_diagnosis.py
```

## Future Refactor Plan

1. Move dashboard CSS into `styles.css`
2. Move KPI and diagnosis calculations into `src/metrics.py` and `src/diagnosis.py`
3. Move report generation into `src/reports.py`
4. Add unit tests for KPI calculations
5. Add CSV schema validation tests
6. Add Ruff formatting and linting checks
