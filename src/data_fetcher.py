from typing import Dict, Any
import yfinance as yf
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def fetch_stock_data(ticker: str, period: str = "5y") -> Dict[str, Any]:
    """Fetch price history and basic fundamentals from yfinance.
    Returns dict with 'prices' (DataFrame) and 'fundamentals' (DataFrame or dict)."""
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period=period, auto_adjust=False)
        if hist.empty:
            logger.warning(f"No price history for {ticker}")
        hist = hist.reset_index()
        # normalize columns
        hist = hist.rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )
        # Ensure types
        hist["date"] = pd.to_datetime(hist["date"]).dt.date
        # fundamentals: try quarterly balance sheet / financials
        fundamentals = {}
        try:
            qbs = tk.quarterly_balance_sheet
            if hasattr(qbs, "columns") and not qbs.empty:
                fundamentals = qbs
        except Exception:
            pass
        # fallback to info
        info = {}
        try:
            info = tk.info
        except Exception:
            info = {}

        return {"prices": hist, "fundamentals": fundamentals, "info": info}
    except Exception as e:
        logger.exception(f"Failed to fetch data for {ticker}: {e}")
        raise
