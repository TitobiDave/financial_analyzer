# Financial Analyzer (Sample Implementation)

This repository is a compact implementation of the Fund-Screener Intern project.

## Quickstart

1. Create a venv and install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the CLI:
   ```
   python -m src.main --ticker NVDA --output nvda.json
   ```
3. Run tests:
   ```
   pytest -q
   ```

## Notes
- This is a simple, functional skeleton intended for extension.
- The data_fetcher uses `yfinance`. Network access required when running live.
