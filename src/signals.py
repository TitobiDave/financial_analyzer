from typing import List
import pandas as pd

def detect_golden_crossover(df: pd.DataFrame) -> List[str]:
    df = df.sort_values('date').reset_index(drop=True)
    # need SMA50 and SMA200
    if 'SMA50' not in df or 'SMA200' not in df:
        return []
    sma50 = df['SMA50']
    sma200 = df['SMA200']
    # Golden cross: yesterday SMA50 <= SMA200 and today SMA50 > SMA200
    cond = (sma50 > sma200) & (sma50.shift(1) <= sma200.shift(1))
    dates = df.loc[cond, 'date'].astype(str).tolist()
    return dates

def detect_death_cross(df: pd.DataFrame) -> List[str]:
    df = df.sort_values('date').reset_index(drop=True)
    if 'SMA50' not in df or 'SMA200' not in df:
        return []
    sma50 = df['SMA50']
    sma200 = df['SMA200']
    cond = (sma50 < sma200) & (sma50.shift(1) >= sma200.shift(1))
    dates = df.loc[cond, 'date'].astype(str).tolist()
    return dates
