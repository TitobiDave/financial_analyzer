# Fund-Screener Intern Project: Financial Analysis Pipeline

## 📌 Project Overview
This project implements a **production-grade financial analysis pipeline** that:
- Ingests stock **price and fundamental data** from the Yahoo Finance API (via `yfinance`).
- Validates raw data with **Pydantic schemas**.
- Merges **daily price data** with **quarterly fundamentals** using forward-fill.
- Calculates technical indicators:
  - 50-day and 200-day Simple Moving Averages (SMA).
  - 52-week high and % difference from the high.
- Computes fundamental ratios:
  - Book Value Per Share (BVPS).
  - Price-to-Book (P/B) ratio.
  - Enterprise Value (EV).
- Detects trading signals:
  - **Golden Cross** (50-day SMA crosses above 200-day SMA).
  - **Death Cross** (50-day SMA crosses below 200-day SMA).
- Persists metrics and signals to **SQLite** with an idempotent schema.
- Exposes results via a **CLI** with JSON export.

This mirrors real-world **data engineering and software design challenges**.

---

## ⚙️ Setup Instructions

### Prerequisites
- Python **3.9+**
- [uv](https://github.com/astral-sh/uv) or [poetry](https://python-poetry.org/)

### Installation (using `uv` - recommended)
```bash
uv init financial_analyzer
cd financial_analyzer
uv add pandas yfinance pydantic "typer[all]" sqlalchemy pyyaml
uv add --dev ruff pytest
```

### Installation (using `poetry`)
```bash
poetry new financial_analyzer
cd financial_analyzer
poetry add pandas yfinance pydantic "typer[all]" sqlalchemy pyyaml
poetry add --group dev ruff pytest
```

---

## 🚀 Usage

### CLI Examples
```bash
# US stock
python -m src.main --ticker NVDA --output nvda_analysis.json

# Indian stock
python -m src.main --ticker RELIANCE.NS --output reliance_analysis.json

# Recent IPO (India)
python -m src.main --ticker SWIGGY.NS --output swiggy_analysis.json
```

Output: JSON file with latest metrics, signal dates, and data quality assessment.

---

## 🗄 Database Schema

SQLite database contains three main tables:

### `tickers`
| Column   | Type   | Description              |
|----------|--------|--------------------------|
| ticker   | String | Stock ticker symbol (PK) |
| name     | String | Company name             |

### `daily_metrics`
| Column   | Type   | Description              |
|----------|--------|--------------------------|
| ticker   | String | Stock ticker symbol (PK) |
| date     | Date   | Trading date (PK)        |
| close    | Float  | Closing price            |
| SMA50    | Float  | 50-day SMA               |
| SMA200   | Float  | 200-day SMA              |

### `signal_events`
| Column   | Type   | Description                      |
|----------|--------|----------------------------------|
| id       | Int    | Primary key (autoincrement)      |
| ticker   | String | Stock ticker symbol              |
| date     | Date   | Signal date                      |
| type     | String | "GoldenCross" or "DeathCross"    |

**Idempotency:** Inserts use `INSERT OR REPLACE` to avoid duplicates.

---

## 🛠 Design Decisions

### Frequency Mismatch (Daily vs Quarterly Data)
- Fundamentals are reported quarterly.
- Strategy: **forward-fill** fundamentals across trading days until the next report.
- Reasoning: A quarterly balance sheet is assumed valid until the next filing.

### Missing or Incomplete Fundamental Data
- **Primary source:** `quarterly_balance_sheet`.
- **Fallbacks:**
  - `balance_sheet` (annual).
  - `info` dictionary (basic ratios, EV).
- If still missing, synthetic values = `NaN` (documented in output).

### Why Forward-Fill Fundamentals?

Fundamentals (balance sheet and financial reports) are reported **quarterly**, but stock prices are updated **daily**.  
Forward-filling assumes that the most recently reported fundamentals remain valid until the next official filing.  
This is a common industry practice because:
- Companies only update fundamentals at quarterly/annual intervals.
- Investors typically use the last available report until new data is released.
- Without forward-fill, most trading days would have `NaN` values for fundamentals, making ratios unusable.

**Trade-off:** Forward-fill introduces a lag (fundamentals may have changed but are not yet reported), but it is more realistic than leaving gaps.



## Fundamental Data Strategy

- **Primary source** → `ticker.quarterly_balance_sheet` (quarterly data).  
- **Fallback 1** → `ticker.balance_sheet` (annual data).  
- **Fallback 2** → `ticker.info` dictionary (basic ratios and EV).  
- **If still missing** → Forward-fill last known values or set to `NaN`.  

### Signal Detection
- Golden Cross and Death Cross are detected using **vectorized pandas** operations.
- Edge cases handled:
  - Insufficient price history (<200 days).
  - NaN values in SMA calculations.

### Market Ticker Handling
- US tickers: no suffix (e.g., `AAPL`, `NVDA`).
- Indian tickers: `.NS` suffix added automatically if missing (e.g., `RELIANCE.NS`).
- Heuristic ensures compatibility across markets.

### Error Handling
- All errors logged using Python’s `logging`.
- API failures handled gracefully → pipeline continues with partial data.
- Data quality assessment included in JSON output (`complete`, `partial`, `missing`).

---

## 📊 Data Quality Assessment
- `"complete"` → All key fields present (SMA50, SMA200, BVPS, P/B, EV, 52w high).
- `"partial"` → Some fields missing.
- `"missing"` → No usable fundamentals.

---

## ✅ Testing Instructions

### Requirements
- `pytest`

### Tests Implemented
- **Processor tests:** Verify SMA and fundamental ratio calculations.
- **Signal tests:** Confirm Golden/Death Cross detection logic.
- **Validation tests:** Ensure Pydantic schemas reject invalid rows.
- **Integration tests:** Run full pipeline on multiple tickers.

### Test Matrix
- **Old US stocks:** `AAPL`, `NVDA`, `MSFT`
- **Old Indian stocks:** `RELIANCE.NS`, `TCS.NS`
- **Recent IPOs (<10 months):** `SWIGGY.NS`, `HYUNDAI.NS`, `URBANCOMP.NS`

Run:
```bash
pytest
```

---

## 📝 Example Output (NVDA)
```json
{
  "ticker": "NVDA",
  "golden_crosses": ["2023-03-20"],
  "death_crosses": ["2022-09-15"],
  "latest": {
    "date": "2025-09-26",
    "close": 455.2,
    "SMA50": 440.5,
    "SMA200": 410.2,
    "52w_high": 480.0,
    "pct_from_52w_high": -5.16,
    "bvps": 8.32,
    "pb_ratio": 54.7,
    "enterprise_value": 1183920000000
  },
  "data_quality": "complete"
}
```

---

