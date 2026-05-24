# Privacy and AI Use

OpsPilot AI is a public portfolio demo and operations reporting assistant. It is designed for fictional, sample, or non-sensitive sales activity data.

## User Data Guidance

Do not upload sensitive, confidential, regulated, or private information into the public demo.

Avoid uploading:

- Real customer personally identifiable information
- Employee confidential records
- Compensation or payroll data
- Medical, legal, or regulated data
- Internal company secrets
- Proprietary pricing, contracts, or confidential business records
- Passwords, API keys, or credentials

## AI Processing

When an OpenAI token is configured, selected summary information may be sent to the AI provider to improve the manager brief.

The app is built so that:

- Rules-based KPI logic is the source of truth
- AI only improves wording, clarity, and structure
- AI should not change calculations, targets, labels, or manager priorities
- AI failure falls back silently to rules-based output
- The app does not intentionally store uploaded CSV data

## Upload Guidance

Use the included fictional sample CSV or generalized activity data.

For public demo usage, remove or anonymize real names, customer information, and internal business-sensitive details before upload.

## Input Limits

The AI helper trims long prompts before AI enhancement to improve reliability and control cost.

Future hardening should include file size limits, row-count limits, and stronger CSV validation.

## Public Demo Note

All built-in sample names, companies, and scenarios are fictional and created for portfolio demonstration purposes.
