
from utils.yfinance_data import Yfinance

def calculate_z_scores(df):
    return (df - df.mean()) / df.std()

def fetch_stock_data_yahoo(ticker, period, interval):
    test = Yfinance([ticker])
    data = test.fetch_stock_data(ticker, period, interval)
    z_scores = data[['Open', 'High', 'Low', 'Close']].apply(calculate_z_scores)
    outliers = (z_scores.abs() > 6).any(axis=1)
    data = data.loc[~outliers]
    info = test.get_stock_info(ticker)
    info['next_earning_date'] = get_next_earning_date(ticker)
    data = data.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
    data = data[["open", "high", "low", "close", "volume"]]
    data = data.tz_localize(None)
    return data, info

def fetch_stock_info_yahoo(ticker):
    test = Yfinance([ticker])
    info = test.get_stock_info(ticker)
    info['next_earning_date'] = get_next_earning_date(ticker)
    return info

def get_next_earning_date(ticker):
    test = Yfinance([ticker])
    earnings = test.get_stock_calendar(ticker)
    if "Earnings Date" not in earnings:
        return '-'
    next_earning_date = earnings['Earnings Date']
    next_earning_date = ' - '.join(map(lambda x: x.strftime('%b %d, %Y'), next_earning_date))
    return next_earning_date
