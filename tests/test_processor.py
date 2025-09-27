from src.processor import process_data

def test_process_basic(sample_prices):
    raw = {'prices': sample_prices, 'info': {}}
    df = process_data(raw)
    assert 'SMA50' in df.columns
    assert 'SMA200' in df.columns
    assert len(df) == len(sample_prices)
