from sqlalchemy import (
    create_engine,
    Column,
    String,
    Date,
    Float,
    Integer,
    Table,
    MetaData,
    Engine,
    text,
)
import pandas as pd
import logging
from typing import List

logger = logging.getLogger(__name__)

metadata = MetaData()


def get_engine(path: str) -> Engine:
    """Create a SQLAlchemy engine for a SQLite database.

    Args:
        path (str): Path to the SQLite database file.

    Returns:
        Engine: SQLAlchemy engine object for database interaction.
    """
    return create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})


def init_db(path: str) -> Engine:
    """Initialize the SQLite database schema.

    Creates tables for:
      * `tickers`
      * `daily_metrics`
      * `signal_events`

    Args:
        path (str): Path to the SQLite database file.

    Returns:
        Engine: SQLAlchemy engine bound to the created tables.
    """
    engine = get_engine(path)
    metadata.bind = engine

    Table(
        "tickers",
        metadata,
        Column("ticker", String, primary_key=True),
        Column("name", String),
    )

    Table(
        "daily_metrics",
        metadata,
        Column("ticker", String, primary_key=True),
        Column("date", Date, primary_key=True),
        Column("close", Float),
        Column("SMA50", Float),
        Column("SMA200", Float),
    )

    Table(
        "signal_events",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("ticker", String),
        Column("date", Date),
        Column("type", String),
    )

    metadata.create_all(engine)
    return engine


def save_daily_metrics(engine: Engine, ticker: str, df: pd.DataFrame) -> None:
    """Save or update daily metrics into the database.

    Performs an idempotent insert (`INSERT OR REPLACE`) to avoid duplicates.

    Args:
        engine (Engine): Active SQLAlchemy engine.
        ticker (str): Stock ticker symbol.
        df (pd.DataFrame): DataFrame containing columns:
            - `date`
            - `close`
            - `SMA50`
            - `SMA200`

    Returns:
        None
    """
    df2 = df[["date", "close", "SMA50", "SMA200"]].copy()
    df2["ticker"] = ticker

    stmt = text(
        """
        INSERT OR REPLACE INTO daily_metrics
        (ticker, date, close, SMA50, SMA200)
        VALUES (:ticker, :date, :close, :SMA50, :SMA200)
        """
    )

    with engine.begin() as conn:
        for _, row in df2.iterrows():
            conn.execute(
                stmt,
                {
                    "ticker": row["ticker"],
                    "date": row["date"],
                    "close": float(row["close"]) if row["close"] is not None else None,
                    "SMA50": float(row["SMA50"]) if row["SMA50"] is not None else None,
                    "SMA200": float(row["SMA200"])
                    if row["SMA200"] is not None
                    else None,
                },
            )

    logger.info(f"Saved {len(df2)} daily metrics for {ticker} (upserted)")


def save_signals(engine: Engine, ticker: str, signals: List[str], type_: str) -> None:
    """Save trading signals (golden/death crosses) into the database.

    Performs an idempotent insert (`INSERT OR REPLACE`) to avoid duplicates.

    Args:
        engine (Engine): Active SQLAlchemy engine.
        ticker (str): Stock ticker symbol.
        signals (List[str]): List of signal dates (ISO format).
        type_ (str): Type of signal, e.g., `"GoldenCross"` or `"DeathCross"`.

    Returns:
        None
    """
    stmt = text(
        """
        INSERT OR REPLACE INTO signal_events (ticker, date, type)
        VALUES (:ticker, :date, :type)
        """
    )

    with engine.begin() as conn:
        for d in signals:
            conn.execute(stmt, {"ticker": ticker, "date": d, "type": type_})
