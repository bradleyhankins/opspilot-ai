# Project Structure

```text
.
├── app.py                  # Streamlit application entrypoint
├── README.md               # Project overview, case study, and test flow
├── ARCHITECTURE.md         # Architecture and design decisions
├── PROJECT_STRUCTURE.md    # Repository structure reference
├── DEVELOPMENT_NOTES.md    # Implementation notes and future refactor plan
├── requirements.txt        # Python dependencies
└── screenshots/            # README screenshots
```

## Current File Responsibilities

### `app.py`

Contains the deployed Streamlit dashboard.

Responsibilities:

- Page configuration
- Sample CSV data
- CSV upload and validation
- KPI calculations
- Operational diagnosis logic
- Trend comparison logic
- Rep and lead source summaries
- Manager report generation
- Streamlit UI rendering

### `README.md`

Public-facing project documentation including live demo, business context, test flow, and case study.

### `ARCHITECTURE.md`

Explains the conceptual application layers and future production architecture.

### `DEVELOPMENT_NOTES.md`

Documents engineering decisions, tradeoffs, and future refactor ideas.

## Future Production Structure

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

The current repo keeps deployment lightweight while documenting the intended path toward a more modular production layout.
