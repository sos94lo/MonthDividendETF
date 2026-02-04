import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_etf_data_detailed():
    # Popular Monthly Dividend ETFs
    tickers = ['JEPI', 'QYLD', 'DIVO', 'SPHD']

    data_list = []

    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # 1. Basic Info
            name = info.get('shortName', info.get('longName', symbol))
            market_cap = info.get('marketCap', 0)

            # Listing Date
            # yfinance often returns 'firstTradeDateEpochUtc'
            listing_date_ts = info.get('firstTradeDateEpochUtc')
            listing_date = "N/A"
            if listing_date_ts:
                listing_date = datetime.fromtimestamp(listing_date_ts).strftime('%Y-%m-%d')

            # Underlying Index (Not always available in basic info, using placeholder or category)
            underlying_index = info.get('category', "N/A")

            # Current Price
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))

            # 2. Returns Calculation (Price Return)
            # Fetch 1 year of history to calculate various periods
            hist = ticker.history(period="1y")

            returns = {
                '1d': 0.0, '1w': 0.0, '1m': 0.0, '3m': 0.0, '6m': 0.0, '1y': 0.0
            }

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

            # 3. Monthly Distributions (Jan-Dec)
            # Get dividend history
            divs = ticker.dividends

            # Initialize monthly buckets for the current year (or last 12 months)
            # For simplicity, we'll try to fill the months of the current calendar year or last 12 reported months.
            # Let's map 1=Jan, 2=Feb...
            monthly_dist = {m: {'amount': 0, 'yield': 0} for m in range(1, 13)}

            if not divs.empty:
                # Filter for this year or last 12 months. Let's look at the last 12 months of data.
                # Actually, the user column says "1월", "2월"... implying a calendar view.
                # Let's verify if we have data for 2024 (or current year).
                current_year = datetime.now().year

                # Filter divs for current year
                this_year_divs = divs[divs.index.year == current_year]

                # If very early in year, might want last year?
                # Let's stick to "Latest available for that month" strategy.
                # If we have a dividend in May 2024, use it. If not, maybe leave empty?
                # Usually "Monthly Dividend ETF" implies we check the latest year's payment for that month.

                for date, amount in divs.items():
                    if date.year == current_year:
                        month_idx = date.month
                        # Simple yield approx: amount / current_price
                        # Note: Real yield is usually annualized, but here "Monthly Yield" might just be (Div / Price)
                        m_yield = (amount / current_price) if current_price else 0
                        monthly_dist[month_idx]['amount'] = amount
                        monthly_dist[month_idx]['yield'] = m_yield

            # Est. Distribution (Sum of last 12 months or similar?)
            # Let's sum the monthly amounts we found (or from info)
            est_dist = sum(d['amount'] for d in monthly_dist.values())

            # Construct Data Row
            row = {
                'ticker': symbol,
                'name': name,
                'market_cap': market_cap,
                'listing_date': listing_date,
                'index': underlying_index,
                'est_dist': est_dist,
                'price': current_price,
                'price_return': "N/A", # Complex calculation, skip for now or use 1Y
                'total_return': "N/A", # Requires reinvestment calc

                # Returns
                'ret_1d': returns['1d'],
                'ret_1w': returns['1w'],
                'ret_1m': returns['1m'],
                'ret_3m': returns['3m'],
                'ret_6m': returns['6m'],
                'ret_1y': returns['1y'],
            }

            # Add Monthly Data
            for m in range(1, 13):
                row[f'dist_{m}'] = monthly_dist[m]['amount']
                row[f'yield_{m}'] = monthly_dist[m]['yield']

            data_list.append(row)

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    return data_list

if __name__ == "__main__":
    # Test
    print(get_etf_data_detailed())
