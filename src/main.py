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
    """Run the full stock analysis pipeline.

    This command:
      * Normalizes the ticker symbol.
      * Loads configuration settings.
      * Fetches historical stock data.
      * Processes technical and fundamental metrics.
      * Detects golden/death cross signals.
      * Saves results into the database.
      * Outputs a JSON summary of the latest metrics and signals.

    Args:
        ticker (str): Stock ticker symbol (e.g., `AAPL`, `RELIANCE.NS`).
        output (str, optional): Path to save JSON output file. Defaults to `"output.json"`.
        config (str, optional): Path to YAML configuration file. Defaults to None.

    Returns:
        None
    """
    ticker = normalize_ticker(ticker)
    cfg = load_config(config)
    setup_logging(cfg.get("logging", {}).get("level", "INFO"))
    period = cfg.get("data_settings", {}).get("historical_period", "5y")
    dbpath = cfg.get("database", {}).get("path", "financial_data.db")

    raw = fetch_stock_data(ticker, period=period)
    if raw is None:
        typer.echo(f"No price data for {ticker}, exiting.")
        return
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
    """Assess the quality of processed stock data.

    Evaluates whether the required core metrics are available
    in the latest row of the DataFrame.

    Args:
        df (pd.DataFrame): Processed DataFrame containing technical and fundamental metrics.

    Returns:
        str: One of:
            * `"complete"`: All core fields are present.
            * `"partial"`: Some but not all fields are present.
            * `"missing"`: No required fields are present or DataFrame is empty.
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


def normalize_ticker(ticker: str) -> str:
    """
    Normalize ticker symbols for market-specific formats.

    - Add `.NS` if it's likely an Indian stock (heuristic).
    - Leave US tickers unchanged.
    """
    ticker = ticker.strip().upper()

    # If ticker already has suffix, return as is
    if "." in ticker:
        return ticker

    # Simple heuristic:
    # US tickers are usually 1–4 letters (AAPL, NVDA, MSFT).
    # Indian tickers are often longer (RELIANCE, TCS, HDFCBANK).
    if len(ticker) > 4:
        return ticker + ".NS"

    return ticker


if __name__ == "__main__":
    app()
