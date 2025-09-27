from pydantic import BaseModel, validator
from datetime import date
from decimal import Decimal
from typing import Optional


class PriceRow(BaseModel):
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

    @validator("high")
    def high_ge_low(cls, v, values):
        low = values.get("low")
        if low is not None and v < low:
            raise ValueError("high must be >= low")
        return v


class FundamentalRow(BaseModel):
    date: date
    book_value: Optional[Decimal] = None
    total_debt: Optional[Decimal] = None
    cash: Optional[Decimal] = None
    shares_outstanding: Optional[Decimal] = None


class SignalEvent(BaseModel):
    date: date
    ticker: str
    type: str  # GoldenCross or DeathCross
