import pandas as pd
from src.signals import detect_golden_crossover, detect_death_cross
from datetime import date, timedelta


def test_golden_and_death_cross():
    dates = [date(2020, 1, 1) + timedelta(days=i) for i in range(10)]
    df = pd.DataFrame(
        {
            "date": dates,
            "SMA50": [1, 1, 1, 1, 2, 2, 2, 2, 3, 3],
            "SMA200": [1, 1, 1, 1, 1, 1.5, 1.7, 2.5, 2.9, 2],
        }
    )
    golden = detect_golden_crossover(df)
    death = detect_death_cross(df)
    assert isinstance(golden, list)
    assert isinstance(death, list)
