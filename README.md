# Sourcing AI MVP V7

V7 adds a more personalized recommendation layer on top of the V6 benchmark scoring.

## What changed in V7

- Interview Analyzer still detects signals from natural call notes / transcript.
- Route recommendation still compares MyyBiz Store, CPC, CPL, CPS/Affiliate, Co-Creation, Myyshop/Product Seeding, Sourcing Support, and Nurture.
- New personalized recommendation block:
  - recommended strategy
  - customer strengths
  - risks / shortfalls
  - first next step
  - route-specific next steps
  - route-specific follow-up talk track
  - things not to do yet
  - personalized follow-up questions

## Run locally

```bash
cd ~/Downloads/sourcing_ai_mvp_v7
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Deploy update

Upload these files to the existing GitHub repo:

- app.py
- requirements.txt
- README.md
- GRADING_BENCHMARK.md
- INTERVIEW_SIGNAL_MAP.md
- data/

Do not upload:

- __pycache__
- README_old.md
- zip file
