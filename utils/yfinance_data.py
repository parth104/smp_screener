import yfinance as yf

class Yfinance:
    def __init__(self, tickers):
        self.tickers = tickers
        self.data = yf.Tickers(tickers)
    
    def fetch_stock_data(self, ticker, period, interval):
        if ticker in self.tickers:
            return self.data.tickers[ticker].history(period=period, interval=interval, rounding=True)
        return None
    
    def get_stock_info(self, ticker):
        return self.data.tickers[ticker].info

    def get_stock_earning_dates(self, ticker):
        return self.data.tickers[ticker].get_earnings_dates(limit=100)
    
    def get_stock_calendar(self, ticker):
        return self.data.tickers[ticker].calendar
    

if __name__ == '__main__':
    test = Yfinance(['IIND.L'])
    data = test.fetch_stock_data('IIND.L', 'max', '1d')
    print(data.columns)
    data['Date'] = data.index.tz_localize(None)
    print(data.columns)
    data = data[['Date', 'Open', 'High', 'Low', 'Close']]
    print(data)
    data.to_csv('IIND_L.csv', index=False)
    # print(test.fetch_stock_data('BOOM.L', '5d', '1d'))
    # print(test.get_stock_info('BOOM.L'))
    # print(test.get_stock_earning_dates('BOOM.L'))

    # print(test.fetch_stock_data('RR.L', '10y', '1d'))
    # print(test.get_stock_info('TLT'))
    # print(test.get_stock_info('0P00017V11.L'))
    # print(test.data.tickers['RR.L'].get_news())
