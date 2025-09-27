from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "database": {"path": "financial_data.db"},
    "logging": {"level": "INFO"},
    "data_settings": {"historical_period": "5y", "min_trading_days_for_sma": 200},
}


def load_config(path: str = None):
    if path:
        p = Path(path)
        if p.exists():
            with open(p, "r") as f:
                return yaml.safe_load(f)
    return DEFAULT_CONFIG
