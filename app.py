from flask import Flask, render_template
import yfinance as yf
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def get_etf_data_detailed():
    tickers = ['JEPI', 'QYLD', 'DIVO', 'SPHD']
    data_list = []

    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Basic Info
            name = info.get('shortName', info.get('longName', symbol))
            market_cap = info.get('marketCap', 0)

            listing_date_ts = info.get('firstTradeDateEpochUtc')
            listing_date = "N/A"
            if listing_date_ts:
                listing_date = datetime.fromtimestamp(listing_date_ts).strftime('%Y-%m-%d')

            underlying_index = info.get('category', "N/A")
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))

            # Returns Calculation
            hist = ticker.history(period="1y")
            returns = {'1d': 0.0, '1w': 0.0, '1m': 0.0, '3m': 0.0, '6m': 0.0, '1y': 0.0}

            if not hist.empty:
                last_price = hist['Close'].iloc[-1]
                def calc_ret(days_back):
                    if len(hist) > days_back:
                         past_price = hist['Close'].iloc[-(days_back+1)]
                         return (last_price - past_price) / past_price
                    return 0.0
                returns['1d'] = calc_ret(1)
                returns['1w'] = calc_ret(5)
                returns['1m'] = calc_ret(21)
                returns['3m'] = calc_ret(63)
                returns['6m'] = calc_ret(126)
                if len(hist) > 0:
                    start_price = hist['Close'].iloc[0]
                    returns['1y'] = (last_price - start_price) / start_price

            # Monthly Distributions
            divs = ticker.dividends
            monthly_dist = {m: {'amount': 0, 'yield': 0} for m in range(1, 13)}

            if not divs.empty:
                current_year = datetime.now().year
                for date, amount in divs.items():
                    if date.year == current_year:
                        month_idx = date.month
                        m_yield = (amount / current_price) if current_price else 0
                        monthly_dist[month_idx]['amount'] = amount
                        monthly_dist[month_idx]['yield'] = m_yield

            est_dist = sum(d['amount'] for d in monthly_dist.values())

            # Format Data for Template
            row = {
                'ticker': symbol,
                'name': name,
                'market_cap': f"{market_cap:,}",
                'listing_date': listing_date,
                'index': underlying_index,
                'est_dist': f"${est_dist:.4f}",
                'price': f"${current_price:.2f}",
                'price_return': "N/A",
                'total_return': "N/A",

                'ret_1d': f"{returns['1d']*100:.2f}%",
                'ret_1w': f"{returns['1w']*100:.2f}%",
                'ret_1m': f"{returns['1m']*100:.2f}%",
                'ret_3m': f"{returns['3m']*100:.2f}%",
                'ret_6m': f"{returns['6m']*100:.2f}%",
                'ret_1y': f"{returns['1y']*100:.2f}%",
            }

            # Flatten Monthly Data for Template Access
            for m in range(1, 13):
                row[f'dist_{m}'] = f"${monthly_dist[m]['amount']:.4f}"
                row[f'yield_{m}'] = f"{monthly_dist[m]['yield']*100:.2f}%"

            data_list.append(row)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    return data_list

@app.route('/')
def index():
    etfs = get_etf_data_detailed()
    return render_template('index.html', etfs=etfs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
