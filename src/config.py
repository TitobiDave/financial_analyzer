from pathlib import Path
import yaml
from typing import Any, Dict, Optional

DEFAULT_CONFIG: Dict[str, Any] = {
    "database": {"path": "financial_data.db"},
    "logging": {"level": "INFO"},
    "data_settings": {"historical_period": "5y", "min_trading_days_for_sma": 200},
}


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from a YAML file or use defaults.

    If a path is provided and the YAML file exists, the function
    loads settings from it. Otherwise, it falls back to the
    default configuration.

    Args:
        path (Optional[str]): Path to a YAML configuration file. Defaults to None.

    Returns:
        Dict[str, Any]: Configuration dictionary containing:
            * `database`: Database connection settings.
            * `logging`: Logging level configuration.
            * `data_settings`: Data fetch and processing parameters.
    """
    if path:
        p = Path(path)
        if p.exists():
            with open(p, "r") as f:
                return yaml.safe_load(f)
    return DEFAULT_CONFIG
