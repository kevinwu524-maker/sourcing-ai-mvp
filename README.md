# Client Profile & Route Recommender V10

V10 focuses on employee-friendly usage and safer review flow.

## What changed in V10

- Added a clear scope notice: this tool is mainly for ecommerce sellers, brands, creators/KOL/KOC, distributors, and channel-related clients.
- Added low-scope warning when the input does not look like ecommerce/distribution/customer-commerce context.
- Added scoring explanation for Adjusted Score, Priority, Evidence, and Confidence.
- Added Compliance Override help text for Auto / Green / Gray / Red.
- Added safer Human Final Review logic: if the user disagrees with the system route, they must choose a final route before exporting.
- Clarified KOL/KOC Seeding vs Creator Affiliate Sales / CPS.
- Updated CSV export filename to V10.

## How to run locally

```bash
cd ~/Downloads/sourcing_ai_mvp_v10
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Files to upload to GitHub

Upload:

- app.py
- requirements.txt
- README.md
- ACKNOWLEDGEMENTS.md
- SAMPLE_CASES.md
- data/

Do not upload:

- __pycache__
- zip files
- old local cache files
