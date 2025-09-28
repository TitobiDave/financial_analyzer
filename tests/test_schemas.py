import pytest
from datetime import date
from pydantic import ValidationError

from src.models import DailyPrice, FundamentalMetrics


def test_daily_price_valid():
    """Test that DailyPrice accepts valid inputs.

    Verifies:
        * All required fields are accepted.
        * Values are stored correctly.
    """
    dp = DailyPrice(
        date=date(2024, 1, 1),
        open=100.5,
        high=105.0,
        low=99.5,
        close=102.3,
        volume=1_000_000,
    )
    assert dp.date == date(2024, 1, 1)
    assert dp.close == 102.3
    assert dp.volume == 1_000_000


def test_daily_price_invalid_missing_field():
    """Test that DailyPrice raises error when a required field is missing.

    Expectation:
        ValidationError is raised when the `close` field is omitted.
    """
    with pytest.raises(ValidationError):
        DailyPrice(
            date=date(2024, 1, 1),
            open=100.5,
            high=105.0,
            low=99.5,
            # close is missing
            volume=5000,
        )


def test_daily_price_invalid_type():
    """Test that DailyPrice rejects incorrect field types.

    Expectation:
        ValidationError is raised when:
        * `date` is not a datetime.date object.
        * `open` or `volume` are provided as strings instead of numbers.
    """
    with pytest.raises(ValidationError):
        DailyPrice(
            date="2024-01-01",  # not a date object
            open="one hundred",  # wrong type
            high=105.0,
            low=99.5,
            close=102.3,
            volume="lots",  # wrong type
        )


def test_fundamental_metrics_valid():
    """Test that FundamentalMetrics accepts valid numeric inputs.

    Verifies:
        * `bvps`, `pb_ratio`, and `enterprise_value` are stored correctly.
    """
    fm = FundamentalMetrics(
        bvps=50.0,
        pb_ratio=2.1,
        enterprise_value=1_000_000_000.0,
    )
    assert fm.bvps == 50.0
    assert fm.pb_ratio == 2.1
    assert fm.enterprise_value == 1_000_000_000.0


def test_fundamental_metrics_optional_fields():
    """Test that FundamentalMetrics allows all fields to be optional.

    Verifies:
        * Schema can be instantiated without providing any values.
        * Defaults remain `None`.
    """
    fm = FundamentalMetrics()
    assert fm.bvps is None
    assert fm.pb_ratio is None
    assert fm.enterprise_value is None


def test_fundamental_metrics_invalid_type():
    """Test that FundamentalMetrics rejects incorrect types.

    Expectation:
        ValidationError is raised when string values are passed instead of floats.
    """
    with pytest.raises(ValidationError):
        FundamentalMetrics(
            bvps="fifty",  # not a float
            pb_ratio="two",
            enterprise_value="big",
        )
