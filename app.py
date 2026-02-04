from flask import Flask, render_template
import yfinance as yf

app = Flask(__name__)

def get_etf_data():
    tickers = ['JEPI', 'QYLD', 'DIVO', 'SPHD']
    data = []
    for ticker_symbol in tickers:
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info

            # Extract relevant information
            name = info.get('shortName', info.get('longName', ticker_symbol))
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))

            # Yield handling
            div_yield_raw = info.get('dividendYield', 0)
            if div_yield_raw:
                if div_yield_raw < 1: # Likely decimal
                     div_yield = f"{div_yield_raw * 100:.2f}%"
                else: # Likely percentage
                     div_yield = f"{div_yield_raw:.2f}%"
            else:
                div_yield = "N/A"

            # Last dividend from history if info is missing
            last_div = info.get('lastDividendValue', 0)
            if not last_div:
                try:
                    history = ticker.dividends
                    if not history.empty:
                        last_div = history.iloc[-1]
                except:
                    pass

            # Format last_div
            if last_div:
                last_div_str = f"${last_div:.4f}"
            else:
                last_div_str = "N/A"

            data.append({
                'ticker': ticker_symbol,
                'name': name,
                'price': price,
                'yield': div_yield,
                'last_dividend': last_div_str
            })
        except Exception as e:
            print(f"Error fetching data for {ticker_symbol}: {e}")
            data.append({
                'ticker': ticker_symbol,
                'name': "Error",
                'price': 0,
                'yield': "N/A",
                'last_dividend': "N/A"
            })
    return data

@app.route('/')
def index():
    etfs = get_etf_data()
    return render_template('index.html', etfs=etfs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
