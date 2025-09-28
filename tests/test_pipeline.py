import pytest
import pandas as pd
from src.data_fetcher import fetch_stock_data
from src.processor import process_data
from src.signals import detect_golden_crossover, detect_death_cross


@pytest.mark.parametrize("ticker", ["AAPL", "RELIANCE.NS"])
def test_pipeline_runs_for_ticker(ticker):
    """Ensure the pipeline works for US and Indian tickers."""
    raw = fetch_stock_data(ticker, period="1y")
    df = process_data(raw)

    # DataFrame should not be empty
    assert not df.empty

    # Core columns must exist
    for col in [
        "SMA50",
        "SMA200",
        "52w_high",
        "pct_from_52w_high",
        "bvps",
        "pb_ratio",
        "enterprise_value",
    ]:
        assert col in df.columns

    # Golden/death cross detection should return a list
    golden = detect_golden_crossover(df)
    death = detect_death_cross(df)
    assert isinstance(golden, list)
    assert isinstance(death, list)


def test_pipeline_handles_recent_ipo(monkeypatch):
    """Ensure pipeline works with short history (recent IPO)."""
    # Create minimal fake raw data
    raw = {
        "prices": pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5, freq="D").date,
                "close": [10, 11, 12, 11, 13],
                "open": [9, 10, 11, 10, 12],
                "high": [10, 11, 12, 12, 13],
                "low": [8, 9, 10, 9, 11],
                "volume": [100, 200, 300, 250, 400],
            }
        ),
        "fundamentals": None,
        "info": {},
    }

    df = process_data(raw)

    # Should still compute SMAs, even with <200 days
    assert "SMA50" in df.columns
    assert not df["SMA50"].isna().all()
