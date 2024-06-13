import yfinance as yf
from smp_tickers import smp500_tickers, india_stocks  # Ensure these modules are available and correct
from utils.data_fetching import fetch_stock_data_yahoo, fetch_stock_info_yahoo
from nifty50_tickers import nifty50_tickers
import concurrent.futures
import time
import pandas as pd
import datetime as dt
from datetime import datetime

def check_screen(stock_data):
    try:
        today = stock_data.iloc[-1]
        yesterday = stock_data.iloc[-2]
        # Check various SMA cross conditions
        if today['SMA_30'] > today['SMA_50'] and yesterday['SMA_30'] < yesterday['SMA_50']:
            return True, '30 cross 50 above'
        if today['SMA_30'] < today['SMA_50'] and yesterday['SMA_30'] > yesterday['SMA_50']:
            return True, '30 cross 50 below'
        if today['SMA_30'] < today['SMA_200'] and yesterday['SMA_30'] > yesterday['SMA_200']:
            return True, '30 cross 200 below'
        if today['SMA_30'] > today['SMA_200'] and yesterday['SMA_30'] < yesterday['SMA_200']:
            return True, '30 cross 200 above'
        if today['close'] < today['SMA_200'] and yesterday['close'] > yesterday['SMA_200']:
            return True, 'Last below 200'
        if today['close'] > today['SMA_200'] and yesterday['close'] < yesterday['SMA_200']:
            return True, 'Last above 200'
    except Exception as e:
        print("Error in check_screen:", e)
    return False, ''

def calculate_sma(data, timeperiod):
    return data.rolling(window=timeperiod).mean()

def fetch_stock_data(ticker):
    stock_data, info = fetch_stock_data_yahoo(ticker, '1y', '1d')
    if stock_data.empty:
        return None
    stock_data['SMA_30'] = calculate_sma(stock_data['close'], 30)
    stock_data['SMA_50'] = calculate_sma(stock_data['close'], 50)
    stock_data['SMA_200'] = calculate_sma(stock_data['close'], 200)
    is_true, signal = check_screen(stock_data)
    if is_true:
        last_data = stock_data.iloc[-1]
        data_dict = {
            'Signal Time': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Signal Name': signal,
            'Stock Ticker': ticker,
            'Stock Name': info.get('longName', ''),
            'Current Price': last_data['close'],
            '% Change': ((last_data['close'] / info.get('previousClose') - 1) * 100).round(2),
        }
        return data_dict
    return None

def get_screen_df():
    start = time.time()
    screened = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(fetch_stock_data, smp500_tickers[:50])
        for result in results:
            if result:
                screened.append(result)
                print(f"Stock {result['Stock Ticker']} passed the screen.")
    print(f"Total stocks passed the screen: {len(screened)}")
    end = time.time()
    print(f"Time taken to process: {end - start:.2f} seconds.")
    df = pd.DataFrame(screened)
    return df

def get_stock_info(ticker):
    stock_info = fetch_stock_info_yahoo(ticker)
    data_dict = {
        'Previous close': stock_info.get('previousClose'),
        'Open': stock_info.get('open'),
        'Bid': f"{stock_info.get('bid', 0)} x {stock_info.get('bidSize', 0)}",
        'Ask': f"{stock_info.get('ask', 0)} x {stock_info.get('askSize', 0)}",
        'Market cap': f"{stock_info.get('marketCap')}, {stock_info.get('currency')}",
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

if __name__ == '__main__':
    print(get_screen_df())
