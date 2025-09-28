from typing import Dict, Any
import pandas as pd
import numpy as np
import logging

from src.models import FundamentalMetrics

logger = logging.getLogger(__name__)


def process_data(raw: Dict[str, Any], min_sma_days: int = 200) -> pd.DataFrame:
    """Process raw stock data into a DataFrame with technical and fundamental metrics.

    This function takes the raw output from `fetch_stock_data` and computes:
      * Technical indicators:
          - 50-day simple moving average (SMA50)
          - 200-day simple moving average (SMA200)
          - 52-week high
          - % difference from 52-week high
      * Fundamentals:
          - Merges quarterly balance sheet values with daily prices
          - Forward-fills values across days between reports
      * Fundamental ratios:
          - Book Value per Share (BVPS)
          - Price-to-Book (P/B) ratio
          - Enterprise Value (EV)

    Args:
        raw (Dict[str, Any]): Dictionary containing:
            * `"prices"` (pd.DataFrame): Daily OHLCV price history.
            * `"fundamentals"` (pd.DataFrame or dict): Quarterly balance sheet.
            * `"info"` (dict): General company metadata.
        min_sma_days (int, optional): Minimum trading days for SMA computation.
            Defaults to 200.

    Returns:
        pd.DataFrame: Processed DataFrame with columns:
            - `date`, `close`, `SMA50`, `SMA200`, `52w_high`,
              `pct_from_52w_high`, `bvps`, `pb_ratio`, `enterprise_value`
            - Plus any merged fundamental fields (e.g., `TotalAssets`, `OrdinarySharesNumber`).
    """

    prices: pd.DataFrame = raw.get("prices").copy()
    prices = prices.sort_values("date").set_index("date")

    prices["SMA50"] = prices["close"].rolling(window=50, min_periods=1).mean()
    prices["SMA200"] = prices["close"].rolling(window=200, min_periods=1).mean()
    prices["52w_high"] = prices["close"].rolling(window=252, min_periods=1).max()
    prices["pct_from_52w_high"] = (
        (prices["close"] - prices["52w_high"]) / prices["52w_high"] * 100
    )

    fundamentals = raw.get("fundamentals")
    if (
        fundamentals is not None
        and hasattr(fundamentals, "T")
        and not fundamentals.empty
    ):
        try:
            fdf = fundamentals.T
            fdf.index = pd.to_datetime(fdf.index, format="%Y-%m-%d", errors="coerce")
            fdf = fdf[~fdf.index.isna()]
            keep_cols = [
                c
                for c in ["TotalAssets", "TotalLiab", "OrdinarySharesNumber"]
                if c in fdf.columns
            ]
            if keep_cols:
                fdf = fdf[keep_cols]

            merged = prices.merge(fdf, left_index=True, right_index=True, how="left")
            merged = merged.ffill().infer_objects(copy=False)
            prices = merged
        except Exception as e:
            logger.warning(f"Could not merge fundamentals: {e}")

    info = raw.get("info", {}) or {}

    bvps = None
    try:
        if "bookValue" in info and info["bookValue"]:
            bvps = info["bookValue"]
        elif (
            "TotalAssets" in prices.columns
            and "OrdinarySharesNumber" in prices.columns
            and prices["OrdinarySharesNumber"].notnull().any()
        ):
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

    ev = info.get("enterpriseValue")
    prices["enterprise_value"] = ev if ev else np.nan
    latest = prices.iloc[-1]
    try:
        validated = FundamentalMetrics(
            bvps=latest["bvps"],
            pb_ratio=latest["pb_ratio"],
            enterprise_value=latest["enterprise_value"],
        )
        logger.info(
            f"Latest fundamentals - BVPS: {validated.bvps}, P/B: {validated.pb_ratio}, EV: {validated.enterprise_value}"
        )
    except Exception as e:
        logger.warning(f"Fundamental validation failed: {e}")

    prices.reset_index(inplace=True)
    return prices
