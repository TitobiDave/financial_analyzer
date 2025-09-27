import pytest
import pandas as pd
from datetime import date, timedelta


@pytest.fixture
def sample_prices():
    # generate 300 days of synthetic prices
    start = date.today() - timedelta(days=400)
    dates = [start + timedelta(days=i) for i in range(300)]
    prices = [100 + i * 0.1 for i in range(300)]
    df = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "high": [p + 1 for p in prices],
            "low": [p - 1 for p in prices],
            "close": prices,
            "volume": [1000] * 300,
        }
    )
    return df
