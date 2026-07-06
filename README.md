# Sourcing AI MVP V8.1

V8.1 keeps the built-in sample interview cases and adds project acknowledgements for Handbook and Live Conversation Toolkit contributors.

## Acknowledgements

- Handbook input: Special thanks to Frank and Jack for their input on the DHgate MyyBiz SP Follow-up Handbook.
- Live Conversation Toolkit input: Special thanks to Ouna for her input on the Live Conversation & Interview Toolkit.

These inputs helped shape the interview flow, scoring benchmarks, route recommendation, and personalized follow-up logic.

## How to run

```bash
cd sourcing_ai_mvp_v8
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Open: http://localhost:8501

## What's new in V8

- Built-in sample cases inside Step 0 Interview Analyzer.
- Six fictional but realistic training cases:
  - Shopify seller needing sourcing + affiliate growth
  - Creator suitable for Co-Creation
  - Brand suitable for Myyshop / Product Seeding
  - Merchant suitable for CPL distributor lead gen
  - Low-readiness client for Nurture / Self-service
  - Gray compliance case requiring approval first
- Expected route and training note included for each sample.

## Files to upload to GitHub

Upload:
- app.py
- requirements.txt
- README.md
- GRADING_BENCHMARK.md
- INTERVIEW_SIGNAL_MAP.md
- PERSONALIZED_ACTION_LOGIC.md
- SAMPLE_CASES.md
- ACKNOWLEDGEMENTS.md
- data/

Do not upload:
- __pycache__
- README_old.md
- zip file
