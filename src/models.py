from pydantic import BaseModel, Field
from typing import Optional
from datetime import date as dt_date


class DailyPrice(BaseModel):
    """Schema for a single row of historical price data."""

    date: dt_date = Field(..., description="Trading date")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price of the day")
    low: float = Field(..., description="Lowest price of the day")
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")


class FundamentalMetrics(BaseModel):
    """Subset of fundamental metrics we care about."""

    bvps: Optional[float] = Field(None, description="Book value per share")
    pb_ratio: Optional[float] = Field(None, description="Price-to-book ratio")
    enterprise_value: Optional[float] = Field(
        None, description="Enterprise value of the company"
    )
