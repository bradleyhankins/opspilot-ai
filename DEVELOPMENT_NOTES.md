# Development Notes

## Build Philosophy

OpsPilot AI is designed as a lightweight operations intelligence tool, not a heavy enterprise analytics platform.

The goal is to show how practical Python and Streamlit workflows can turn sales activity data into manager-ready insight.

## Engineering Priorities

1. Clear CSV input workflow
2. Transparent KPI calculations
3. Rules-based operational diagnosis
4. Manager-ready reporting
5. Public-safe sample data
6. Simple deployment on Streamlit Community Cloud

## Current Tradeoffs

The app currently keeps all deployment logic in `app.py` for simplicity. This makes the live app easier to deploy and inspect, but less modular than a production codebase.

## Future Refactor Plan

A future production-oriented version should split the app into:

```text
src/data_loader.py
src/metrics.py
src/diagnosis.py
src/reports.py
src/components.py
src/styles.css
```

## Testing Opportunities

The most valuable future tests would cover:

- CSV schema validation
- KPI formulas
- Period-over-period comparison logic
- Operational health grading
- Bottleneck diagnosis logic
- Manager report generation

## Code Quality Roadmap

Potential future tooling:

- Ruff for linting and formatting
- Pytest for utility tests
- Pre-commit hooks
- GitHub Actions smoke checks
