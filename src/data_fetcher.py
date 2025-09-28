from typing import Dict, Any
import yfinance as yf
import logging
import pandas as pd

from src.models import DailyPrice

logger = logging.getLogger(__name__)


def fetch_stock_data(ticker: str, period: str = "5y") -> Dict[str, Any]:
    """Fetch historical prices and fundamental data for a given ticker.

    Uses the Yahoo Finance API via `yfinance` to retrieve:
      * Daily OHLCV (open, high, low, close, volume) price history.
      * Quarterly balance sheet (if available).
      * General company info as a fallback.

    Args:
        ticker (str): Stock ticker symbol (e.g., `"AAPL"`, `"RELIANCE.NS"`).
        period (str, optional): Historical period to fetch (e.g., `"1y"`, `"5y"`). Defaults to `"5y"`.

    Returns:
        Dict[str, Any]: Dictionary with keys:
            * `"prices"` (pd.DataFrame): Daily historical prices with normalized columns:
                - `date`, `open`, `high`, `low`, `close`, `volume`.
            * `"fundamentals"` (pd.DataFrame or dict): Quarterly balance sheet, if available.
            * `"info"` (dict): Fallback company info from Yahoo Finance.

    Raises:
        Exception: If the Yahoo Finance request fails.
    """
    try:
        tk = yf.Ticker(ticker)

        hist = tk.history(period=period, auto_adjust=False)
        if hist.empty:
            logger.warning(f"No price history for {ticker}")

        hist = hist.reset_index()
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
        hist["date"] = pd.to_datetime(hist["date"]).dt.date
        validated_rows = []
        for _, row in hist.iterrows():
            try:
                validated = DailyPrice(**row.to_dict())
                validated_rows.append(validated.dict())
            except Exception as e:
                logger.warning(f"Validation failed for row {row}: {e}")

        hist = pd.DataFrame(validated_rows)

        fundamentals: Any = {}
        try:
            qbs = tk.quarterly_balance_sheet
            if hasattr(qbs, "columns") and not qbs.empty:
                fundamentals = qbs.to_dict()
        except Exception:
            pass
        info: Dict[str, Any] = {}
        try:
            info = tk.info
        except Exception:
            info = {}

        if hist.empty:
            logger.warning(f"No usable price history for {ticker}, skipping.")
            return None

        return {"prices": hist, "fundamentals": fundamentals, "info": info}

    except Exception as e:
        logger.exception(f"Failed to fetch data for {ticker}: {e}")
        raise
