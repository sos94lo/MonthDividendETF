import json
import os
from flask import Flask, render_template

app = Flask(__name__)

def load_data():
    # Try loading real data first, then mock
    files = ['etf_data.json', 'etf_data_mock.json']
    for file in files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check if it's a valid data dict or list
                    if isinstance(data, dict):
                        if data.get('status') == 'error':
                            continue
                        return data.get('data', [])
                    elif isinstance(data, list):
                        return data
            except:
                continue
    return []

@app.route('/')
def index():
    raw_data = load_data()
    # Process data to match table structure if needed
    # For now, pass raw_data and let jinja handle access,
    # but we might need to calculate yields.

    formatted_data = []
    for item in raw_data:
        # handle missing keys safely
        price = item.get('price', 0)
        dists = item.get('distributions', {})

        row = {
            'code': item.get('stock_code', ''),
            'name': item.get('stock_name', ''),
            'market_cap': item.get('net_asset', 0),
            'listing_date': item.get('listing_date', '-'),
            'index': item.get('underlying_index', '-'),
            'expected_dist': item.get('total_dist', 0), # Mock: use total as expected
            'price': price,
            'price_return': '-', # Placeholder
            'total_return': '-', # Placeholder
            'returns': item.get('returns', {}),
            'months': []
        }

        # Calculate monthly amount and yield
        for m in range(1, 13):
            amt = dists.get(str(m), 0)
            rate = round((amt / price * 100), 2) if price > 0 else 0
            row['months'].append({'amt': amt, 'rate': rate})

        formatted_data.append(row)

    return render_template('index.html', etf_list=formatted_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
