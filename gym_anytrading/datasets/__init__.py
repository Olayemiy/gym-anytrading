from .utils import load_dataset as _load_dataset


# Load FOREX datasets
FOREX_EURUSD_1H_ASK = _load_dataset('FOREX_EURUSD_1H_ASK', None) #'Time'

BACKTEST_DATASET = _load_dataset('BACKTEST_DATASET', None) #'Open' - yemi

# Load Stocks datasets
STOCKS_GOOGL = _load_dataset('STOCKS_GOOGL', 'Date')
