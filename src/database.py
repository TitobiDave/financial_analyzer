from sqlalchemy import create_engine, Column, String, Date, Float, Integer, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import pandas as pd
import logging

logger = logging.getLogger(__name__)

metadata = MetaData()

def get_engine(path: str):
    return create_engine(f'sqlite:///{path}', connect_args={'check_same_thread': False})

def init_db(path: str):
    engine = get_engine(path)
    metadata.bind = engine
    # tables
    from sqlalchemy import Column, String, Date, Float, Integer
    tickers = Table(
        'tickers', metadata,
        Column('ticker', String, primary_key=True),
        Column('name', String)
    )
    daily_metrics = Table(
        'daily_metrics', metadata,
        Column('ticker', String, primary_key=True),
        Column('date', Date, primary_key=True),
        Column('close', Float),
        Column('SMA50', Float),
        Column('SMA200', Float)
    )
    signal_events = Table(
        'signal_events', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('ticker', String),
        Column('date', Date),
        Column('type', String)
    )
    metadata.create_all(engine)
    return engine

def save_daily_metrics(engine, ticker: str, df: pd.DataFrame):
    df2 = df[['date', 'close', 'SMA50', 'SMA200']].copy()
    df2['ticker'] = ticker

    stmt = text("""
        INSERT OR REPLACE INTO daily_metrics
        (ticker, date, close, SMA50, SMA200)
        VALUES (:ticker, :date, :close, :SMA50, :SMA200)
    """)

    with engine.begin() as conn:
        for _, row in df2.iterrows():
            conn.execute(stmt, {
                "ticker": row['ticker'],
                "date": row['date'],
                "close": float(row['close']) if row['close'] is not None else None,
                "SMA50": float(row['SMA50']) if row['SMA50'] is not None else None,
                "SMA200": float(row['SMA200']) if row['SMA200'] is not None else None,
            })

    logger.info(f"Saved {len(df2)} daily metrics for {ticker} (upserted)")


def save_signals(engine, ticker: str, signals: list, type_: str):
    stmt = text("""
        INSERT OR REPLACE INTO signal_events (ticker, date, type)
        VALUES (:ticker, :date, :type)
    """)
    with engine.begin() as conn:
        for d in signals:
            conn.execute(stmt, {"ticker": ticker, "date": d, "type": type_})