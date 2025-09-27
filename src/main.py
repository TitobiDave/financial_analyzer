import typer
import json
import pandas as pd
from .data_fetcher import fetch_stock_data
from .processor import process_data
from .signals import detect_golden_crossover, detect_death_cross
from .database import init_db, save_daily_metrics, save_signals
from .config import load_config
from .utils import setup_logging

app = typer.Typer()


@app.command()
def run(
    ticker: str = typer.Option(..., "--ticker", "-t", help="Stock ticker symbol"),
    output: str = "output.json",
    config: str = None,
):
    """Run full pipeline for a ticker and save JSON output."""
    cfg = load_config(config)
    setup_logging(cfg.get("logging", {}).get("level", "INFO"))
    period = cfg.get("data_settings", {}).get("historical_period", "5y")
    dbpath = cfg.get("database", {}).get("path", "financial_data.db")

    raw = fetch_stock_data(ticker, period=period)
    df = process_data(
        raw,
        min_sma_days=cfg.get("data_settings", {}).get("min_trading_days_for_sma", 200),
    )
    golden = detect_golden_crossover(df)
    death = detect_death_cross(df)

    engine = init_db(dbpath)
    save_daily_metrics(engine, ticker, df)
    save_signals(engine, ticker, golden, "GoldenCross")
    save_signals(engine, ticker, death, "DeathCross")

    keep_cols = [
        "date",
        "close",
        "SMA50",
        "SMA200",
        "52w_high",
        "pct_from_52w_high",
        "bvps",
        "pb_ratio",
        "enterprise_value",
    ]
    latest_row = df.sort_values("date").iloc[-1]
    latest_row = {k: latest_row[k] for k in keep_cols if k in latest_row}
    result = {
        "ticker": ticker,
        "golden_crosses": golden,
        "death_crosses": death,
        "latest": latest_row,
        "data_quality": assess_data_quality(df) if not df.empty else "missing",
    }
    with open(output, "w") as f:
        json.dump(result, f, default=str, indent=2)

    typer.echo(f"Saved analysis to {output}")


def assess_data_quality(df: pd.DataFrame) -> str:
    """
    Assess data quality for required fields.
    Returns: "complete", "partial", or "missing"
    """
    if df.empty:
        return "missing"

    latest = df.iloc[-1]

    core_fields = [
        "SMA50",
        "SMA200",
        "52w_high",
        "pct_from_52w_high",
        "bvps",
        "pb_ratio",
        "enterprise_value",
    ]

    available = sum(1 for f in core_fields if f in latest and not pd.isna(latest[f]))

    if available == len(core_fields):
        return "complete"
    elif available > 0:
        return "partial"
    else:
        return "missing"


if __name__ == "__main__":
    app()
