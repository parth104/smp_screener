import requests

def fetch_smp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    print(response.status_code)
    if response.status_code == 200:
        tickers = []
        data = response.text
        start = data.find('<table class="wikitable sortable" id="constituents">')
        print(start)
        end = data.find('</table>', start)
        # print(end)
        table = data[start:end]
        rows = table.split('<tr>')[1:]
        print(type(rows))
        print(rows[0])
        
        for row in rows:
            cols = row.split('<td>')
            print(cols)
            ticker = cols[1].split('">')[1].split('</a')[0]
            print(ticker)
            tickers.append(ticker)
        return tickers
    else:
        print("Failed to fetch S&P 500 tickers.")

def save_tickers_to_file(tickers, filename='smp_tickers.py'):
    with open(filename, 'w') as f:
        f.write("smp500_tickers = [\n")
        for ticker in tickers:
            f.write(f"    '{ticker}',\n")
        f.write("]")

def fetch_nifty50_tickers():
    url = 'https://en.wikipedia.org/wiki/NIFTY_50'
    response = requests.get(url)
    data = response.text
    tickers = []
    start = data.find('<table class="wikitable sortable" id="constituents">')
    end = data.find('</table>', start)
    
    table = data[start:end]
    rows = table.split('<tr>')[1:]
    print(type(rows))
    print(rows[1])
    
    for row in rows[1:]:
        cols = row.split('<td>')
        ticker = cols[1].split('\n')[0]
        tickers.append(ticker)

    print(len(tickers))
    return tickers

if __name__ == "__main__":
    # smp500_tickers = fetch_smp500_tickers()
    # if smp500_tickers:
    #     save_tickers_to_file(smp500_tickers)
    #     print("S&P 500 tickers saved to smp_tickers.py file.")
    # else:
    #     print("Failed to fetch S&P 500 tickers.")


    nifty50_tickers = fetch_nifty50_tickers()
    if nifty50_tickers:
        save_tickers_to_file(nifty50_tickers, 'nifty50_tickers.py')
        print("S&P 500 tickers saved to smp_tickers.py file.")
    else:
        print("Failed to fetch S&P 500 tickers.")
