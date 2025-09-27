from typing import Dict, Any
import pandas as pd
import numpy as np
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def process_data(raw: Dict[str, Any], min_sma_days: int = 200) -> pd.DataFrame:
    prices: pd.DataFrame = raw.get('prices').copy()
    prices = prices.sort_values('date').set_index('date')

    # --- Technical indicators ---
    prices['SMA50'] = prices['close'].rolling(window=50, min_periods=1).mean()
    prices['SMA200'] = prices['close'].rolling(window=200, min_periods=1).mean()
    prices['52w_high'] = prices['close'].rolling(window=252, min_periods=1).max()
    prices['pct_from_52w_high'] = (prices['close'] - prices['52w_high']) / prices['52w_high'] * 100

    # --- Fundamentals ---
    info = raw.get('info', {}) or {}

    # Book Value Per Share (BVPS)
    bvps = None
    try:
        # In yfinance, bookValue is already per share for many tickers
        if info.get('bookValue'):
            bvps = info['bookValue']
        else:
            total_equity = info.get('totalAssets') or None
            shares = info.get('sharesOutstanding') or None
            if total_equity and shares and shares > 0:
                bvps = total_equity / shares
    except Exception:
        bvps = None

    # Price-to-Book (P/B) Ratio
    if bvps and bvps > 0:
        prices['bvps'] = bvps
        prices['pb_ratio'] = prices['close'] / bvps
    else:
        prices['bvps'] = np.nan
        prices['pb_ratio'] = np.nan

    # Enterprise Value (simplified)
    ev = info.get('enterpriseValue')
    prices['enterprise_value'] = ev if ev else np.nan

    prices.reset_index(inplace=True)
    return prices

def process_data(raw: Dict[str, Any], min_sma_days: int = 200) -> pd.DataFrame:
    """
    Takes raw fetch output and returns a DataFrame with computed metrics:
    - Technical indicators (SMA50, SMA200, 52w high, pct from high)
    - Forward-filled fundamentals (e.g. Book Value, Revenue)
    - Fundamental ratios (BVPS, P/B, EV)
    """
    # --- Prices ---
    prices: pd.DataFrame = raw.get("prices").copy()
    prices = prices.sort_values("date").set_index("date")

    # --- Technical indicators ---
    prices["SMA50"] = prices["close"].rolling(window=50, min_periods=1).mean()
    prices["SMA200"] = prices["close"].rolling(window=200, min_periods=1).mean()
    prices["52w_high"] = prices["close"].rolling(window=252, min_periods=1).max()
    prices["pct_from_52w_high"] = (
        (prices["close"] - prices["52w_high"]) / prices["52w_high"] * 100
    )

    # --- Fundamentals ---
    fundamentals = raw.get("fundamentals")
    if fundamentals is not None and hasattr(fundamentals, "T") and not fundamentals.empty:
        try:
            # Transpose: rows become report dates
            fdf = fundamentals.T
            fdf.index = pd.to_datetime(fdf.index).date

            # Keep only useful columns if available
            keep_cols = [c for c in ["TotalAssets", "TotalLiab", "OrdinarySharesNumber"] if c in fdf.columns]
            if keep_cols:
                fdf = fdf[keep_cols]

            # Merge with prices
            merged = prices.merge(fdf, left_index=True, right_index=True, how="left")

            # Forward-fill fundamentals so each day between reports carries last known values
            merged = merged.ffill()

            prices = merged
        except Exception as e:
            logger.warning(f"Could not merge fundamentals: {e}")

    # --- Ratios from fundamentals/info ---
    info = raw.get("info", {}) or {}

    # Book Value per Share (BVPS)
    bvps = None
    try:
        if "bookValue" in info and info["bookValue"]:
            bvps = info["bookValue"]  # Already per share in most yfinance tickers
        elif (
            "TotalAssets" in prices.columns
            and "OrdinarySharesNumber" in prices.columns
            and prices["OrdinarySharesNumber"].notnull().any()
        ):
            # Derive BVPS = TotalAssets / Shares Outstanding
            last_assets = prices["TotalAssets"].ffill().iloc[-1]
            last_shares = prices["OrdinarySharesNumber"].ffill().iloc[-1]
            if last_shares and last_shares > 0:
                bvps = last_assets / last_shares
    except Exception:
        bvps = None

    if bvps and bvps > 0:
        prices["bvps"] = bvps
        prices["pb_ratio"] = prices["close"] / bvps
    else:
        prices["bvps"] = np.nan
        prices["pb_ratio"] = np.nan

    # Enterprise Value (from info as fallback)
    ev = info.get("enterpriseValue")
    prices["enterprise_value"] = ev if ev else np.nan

    prices.reset_index(inplace=True)
    return prices