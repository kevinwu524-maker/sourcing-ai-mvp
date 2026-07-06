# Sourcing AI MVP V9 — Client Profile & Route Recommender

V9 is redesigned to be more employee-friendly:

1. **Profile first, score later** — employees see the client profile, recommended route, priority, confidence, and next action before detailed scoring.
2. **Guided workflow** — four clear modes: Analyze Interview, Quick Assessment, Training Sample, and Benchmark/Credits.
3. **Copy-ready output** — the app generates internal next steps, client-facing follow-up, CRM note, and CSV export.
4. **Human final review** — employees can agree, partially agree, or override the system recommendation.
5. **Training mode** — sample cases are included for onboarding and route calibration.

## Run locally

```bash
cd ~/Downloads/sourcing_ai_mvp_v9
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Upload to GitHub / Streamlit

Upload these files to the repo root:

- `app.py`
- `requirements.txt`
- `README.md`
- `ACKNOWLEDGEMENTS.md`
- `SAMPLE_CASES.md`
- `data/`

Do not upload:

- `__pycache__`
- `.zip` files
- old README files

## Data caution

Use client codes instead of real client names when possible. Avoid putting phone numbers, emails, Stripe details, or full sensitive conversations into public systems.
