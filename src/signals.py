from typing import List
import pandas as pd


def detect_golden_crossover(df: pd.DataFrame) -> List[str]:
    """
    Detects golden cross events in stock data.

    A golden cross occurs when the 50-day simple moving average (SMA50)
    crosses above the 200-day simple moving average (SMA200).

    Args:
        df (pd.DataFrame): DataFrame containing stock data with columns:
            - "date": datetime or string of the date
            - "SMA50": 50-day simple moving average
            - "SMA200": 200-day simple moving average

    Returns:
        List[str]: List of dates (as strings) where golden cross events occurred.
    """
    df = df.sort_values("date").reset_index(drop=True)
    if "SMA50" not in df or "SMA200" not in df:
        return []

    sma50 = df["SMA50"]
    sma200 = df["SMA200"]
    cond = (sma50 > sma200) & (sma50.shift(1) <= sma200.shift(1))
    dates = df.loc[cond, "date"].astype(str).tolist()
    return dates


def detect_death_cross(df: pd.DataFrame) -> List[str]:
    """
    Detects death cross events in stock data.

    A death cross occurs when the 50-day simple moving average (SMA50)
    crosses below the 200-day simple moving average (SMA200).

    Args:
        df (pd.DataFrame): DataFrame containing stock data with columns:
            - "date": datetime or string of the date
            - "SMA50": 50-day simple moving average
            - "SMA200": 200-day simple moving average

    Returns:
        List[str]: List of dates (as strings) where death cross events occurred.
    """
    df = df.sort_values("date").reset_index(drop=True)
    if "SMA50" not in df or "SMA200" not in df:
        return []

    sma50 = df["SMA50"]
    sma200 = df["SMA200"]
    cond = (sma50 < sma200) & (sma50.shift(1) >= sma200.shift(1))
    dates = df.loc[cond, "date"].astype(str).tolist()
    return dates
