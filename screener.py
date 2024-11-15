import yfinance as yf
from smp_tickers import ALL_TICKERS, russell500_tickers
from alpha_vantage.timeseries import TimeSeries
from utils.data_fetching import fetch_stock_info_yahoo
from nifty50_tickers import nifty50_tickers
import talib
import concurrent.futures
import time
import pandas as pd
import datetime as dt
from datetime import datetime

ts = TimeSeries(key='API_KEY', output_format='pandas')

def check_screen(stock_data):
    try:
        today = stock_data.iloc[-1]
        yesterday = stock_data.iloc[-2]
        # Check if the 30-day SMA cross up 50-day SMA since previous day
        if today['SMA_30'] > today['SMA_50'] and yesterday['SMA_30'] < yesterday['SMA_50']:
            return True, '30 cross 50 above'
        # Check if the 30-day SMA cross down 50-day SMA since previous day
        if today['SMA_30'] < today['SMA_50'] and yesterday['SMA_30'] > yesterday['SMA_50']:
            return True, '30 cross 50 below'
        # Check if the 30-day SMA cross down 200-day SMA since previous day
        if today['SMA_30'] < today['SMA_200'] and yesterday['SMA_30'] > yesterday['SMA_200']:
            return True, '30 cross 200 below'
        # Check if the 30-day SMA cross up 200-day SMA since previous day
        if today['SMA_30'] > today['SMA_200'] and yesterday['SMA_30'] < yesterday['SMA_200']:
            return True, '30 cross 200 above'
        # Check if the Close price cross down 200-day SMA since previous day
        if today['4. close'] < today['SMA_200'] and yesterday['4. close'] > yesterday['SMA_200']:
            return True, 'Last below 200'
        # Check if the close cross up 200-day SMA since previous day
        if today['4. close'] > today['SMA_200'] and yesterday['4. close'] < yesterday['SMA_200']:
            return True, 'Last above 200'
    except Exception as e:
        print("Error in check_screen:", e)
    return False, ''


def fetch_stock_data(ticker):

    try:
        stock_data, metadata = ts.get_daily(ticker, outputsize='full')
        stock_data['SMA_30'] = talib.SMA(stock_data['4. close'], timeperiod=30)
        stock_data['SMA_50'] = talib.SMA(stock_data['4. close'], timeperiod=50)
        stock_data['SMA_200'] = talib.SMA(stock_data['4. close'], timeperiod=200)
        if stock_data.empty:
            return None
        is_true, signal = check_screen(stock_data)
        print(is_true, signal)
        if is_true:
            last_data = stock_data.iloc[-1]
            prev_data = stock_data.iloc[-2]
            data_dict = {
                'Signal Time': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Signal Name': signal,
                'Stock Ticker': ticker,
                '% Change': ((last_data['4. close'] / prev_data['4. close'] - 1) * 100).round(2)
            }
            return data_dict
    except Exception as e:
        print(ticker, e)

        return None
    return None


def get_screen_df():
    start = time.time()
    screened = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Make request in chunk of 50 and take 5 sec sleep
        for i in range(0, 20, 50):
        # for i in range(0, len(ALL_TICKERS), 50):
            results = executor.map(fetch_stock_data, ALL_TICKERS[i:i+50])
            for result in results:
                if result:
                    screened.append(result)
                    print(f"Stock {result} passed the screen.")
            time.sleep(5)
    print(f"Total stocks passed the screen: {len(screened)}")
    end = time.time()
    print(f"Time taken to process  {end-start:.2f} seconds.")
    df = pd.DataFrame(screened)
    
    return df

def get_stock_info(ticker):
    stock_info = fetch_stock_info_yahoo(ticker)
    data_dict = {
        'Previous close': stock_info.get('previousClose'),
        'Open': stock_info.get('open'),
        'Market cap': f"{convert_to_billions_or_trillions(stock_info.get('marketCap'))}, {stock_info.get('currency')}",
        'Beta (5Y monthly)': stock_info.get('beta'),
        'Earnings date': stock_info.get('next_earning_date', ''),
        'Forward dividend & yield': f"{stock_info.get('dividendRate')} ({round(stock_info.get('dividendYield', 0) * 100, 2)} %)",
        'Ex-dividend date': convert_epoch_to_date_string(stock_info.get('exDividendDate', '')),
        '1y target est': stock_info.get('targetMeanPrice'),
    }

    return data_dict
    

def convert_epoch_to_date_string(epoch_time):
    if isinstance(epoch_time, list) and epoch_time:  # handle list of timestamps
        return ', '.join([datetime.utcfromtimestamp(time).strftime('%b %d, %Y') for time in epoch_time])
    elif isinstance(epoch_time, (int, float)):
        return datetime.fromtimestamp(epoch_time).strftime('%b %d, %Y')
    return 'N/A'

def convert_to_billions_or_trillions(amount):
    amount = float(amount)
    if amount >= 1_000_000_000_000:
        return f"{amount / 1_000_000_000_000:.2f} Trillion"
    elif amount >= 1_000_000_000:
        return f"{amount / 1_000_000_000:.2f} Billion"
    elif amount >= 1_000_000:
        return f"{amount / 1_000_000:.2f} Million"
    else:
        return f"{amount}"

if __name__ == '__main__':
    print(get_screen_df())
