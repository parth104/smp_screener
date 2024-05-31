import yfinance as yf
from smp_tickers import smp500_tickers, india_stocks
from utils.data_fetching import fetch_stock_data_yahoo, fetch_stock_info_yahoo
from nifty50_tickers import nifty50_tickers
import talib
import concurrent.futures
import time
import pandas as pd
import datetime as dt
from datetime import datetime

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
        if today['close'] < today['SMA_200'] and yesterday['close'] > yesterday['SMA_200']:
            return True, 'Last below 200'
        # Check if the close cross up 200-day SMA since previous day
        if today['close'] > today['SMA_200'] and yesterday['close'] < yesterday['SMA_200']:
            return True, 'Last above 200'
    except Exception as e:
        print("Error in check_screen:", e)
    return False, ''


def fetch_stock_data(ticker):

    stock_data, info = fetch_stock_data_yahoo(ticker, '1y', '1d')
    # stock_data = data.history(period='1y', interval='1d')
    stock_data['SMA_30'] = talib.SMA(stock_data['close'], timeperiod=30)
    stock_data['SMA_50'] = talib.SMA(stock_data['close'], timeperiod=50)
    stock_data['SMA_200'] = talib.SMA(stock_data['close'], timeperiod=200)
    if stock_data.empty:
        return None
    is_true, signal = check_screen(stock_data)
    if is_true:
        # print(data.info)
        last_data = stock_data.iloc[-1]
        data_dict = {
            'Signal Time': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Signal Name': signal,
            'Stock Ticker': ticker,
            'Stock Name': info.get('longName', ''),
            'Current Price': info.get('currentPrice', ''),
            '% Change': ((last_data['close'] / info.get('previousClose') - 1) * 100).round(2),
            # 'Sector': data.info.get('sector', ''),
            # 'Industry': data.info.get('industry', ''),
            # 'Market Cap': data.info.get('marketCap', ''),
            # 'Previous Close': data.info.get('previousClose', ''),
            # '50-day Average Volume': data.info.get('averageVolume', ''),
            # 'EPS': data.info.get('trailingEps', ''),
            # 'PE Ratio': data.info.get('trailingPE', ''),
            # 'Forward PE Ratio': data.info.get('forwardPE', ''),
            # 'PEG Ratio': data.info.get('pegRatio', ''),
            # 'Price to Sales Ratio': data.info.get('priceToSalesTrailing12Months', ''),
            # 'Price to Book Ratio': data.info.get('priceToBook', ''),
            # 'Price to Cashflow Ratio': data.info.get('priceToCashflow', ''),
            # 'Enterprise Value': data.info.get('enterpriseValue', ''),
            # 'Enterprise to Revenue Ratio': data.info.get('enterpriseToRevenue', ''),
            # 'Enterprise to EBITDA Ratio': data.info.get('enterpriseToEbitda', ''),
            # 'Beta': data.info.get('beta', ''),
            # '52-week High': data.info.get('fiftyTwoWeekHigh', ''),
            # '52-week Low': data.info.get('fiftyTwoWeekLow', ''),
            # 'Dividend Rate': data.info.get('dividendRate', ''),
            # 'Dividend Yield': data.info.get('dividendYield', ''),
            # 'Ex-Dividend Date': data.info.get('exDividendDate', ''),
            # '1y Target Estimate': data.info.get('targetMeanPrice', ''),
            # 'Screened': True
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
                print(f"Stock {result} passed the screen.")
    # print(screened)
    print(f"Total stocks passed the screen: {len(screened)}")
    end = time.time()
    print(f"Time taken to process  {end-start:.2f} seconds.")
    df = pd.DataFrame(screened)
    
    return df

def get_stock_info(ticker):
    data = yf.Ticker(ticker)
    stock_info = fetch_stock_info_yahoo(ticker)
    # data_dict = {
    #     'Stock Ticker': ticker,
    #     'Stock Name': data.info.get('longName', ''),
    #     'Current Price': data.info.get('currentPrice', ''),
    #     'Sector': data.info.get('sector', ''),
    #     'Industry': data.info.get('industry', ''),
    #     'Market Cap': data.info.get('marketCap', ''),
    #     'Previous Close': data.info.get('previousClose', ''),
    #     '50-day Average Volume': data.info.get('averageVolume', ''),
    #     'EPS': data.info.get('trailingEps', ''),
    #     'PE Ratio': data.info.get('trailingPE', ''),
    #     'Forward PE Ratio': data.info.get('forwardPE', ''),
    #     'PEG Ratio': data.info.get('pegRatio', ''),
    #     'Price to Sales Ratio': data.info.get('priceToSalesTrailing12Months', ''),
    #     'Price to Book Ratio': data.info.get('priceToBook', ''),
    #     'Price to Cashflow Ratio': data.info.get('priceToCashflow', ''),
    #     'Enterprise Value': data.info.get('enterpriseValue', ''),
    #     'Enterprise to Revenue Ratio': data.info.get('enterpriseToRevenue', ''),
    #     'Enterprise to EBITDA Ratio': data.info.get('enterpriseToEbitda', ''),
    #     'Beta': data.info.get('beta', ''),
    #     '52-week High': data.info.get('fiftyTwoWeekHigh', ''),
    #     '52-week Low': data.info.get('fiftyTwoWeekLow', ''),
    # }
    data_dict = {
        'Previous close': stock_info.get('previousClose'),
        'Open': stock_info.get('open'),
        'Bid': f"{stock_info.get('bid', 0)} x {stock_info.get('bidSize', 0)}",
        'Ask': f"{stock_info.get('ask', 0)} x {stock_info.get('askSize', 0)}",
        # 'Day\'s range': f"{stock_info.get('dayLow')} - {stock_info.get('dayHigh')}",
        # '52-week range': f"{stock_info.get('fiftyTwoWeekLow')} - {stock_info.get('fiftyTwoWeekHigh')}",
        # 'Volume': stock_info.get('volume'),
        # 'Avg. volume': stock_info.get('averageVolume'),
        'Market cap': f"{stock_info.get('marketCap')}, {stock_info.get('currency')}",
        'Beta (5Y monthly)': stock_info.get('beta'),
        # 'PE ratio (TTM)': stock_info.get('trailingPE'),
        # 'EPS (TTM)': stock_info.get('trailingEps'),
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
