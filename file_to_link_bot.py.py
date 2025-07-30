import pandas as pd
import requests
import time
import os
from datetime import datetime

# Nifty 50 stocks (example subset)
nifty_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK', 'LT', 'SBIN']

# Excel writer setup
output_file = 'Nifty_Options_Analysis.xlsx'

# Ensure the file exists
if not os.path.exists(output_file):
    # Create an empty DataFrame and save it to the file
    df = pd.DataFrame(columns=['Time', 'Symbol', 'Strike Price', 'Option Type', 'LTP', 'Change (%)', 'OI', 'OI Change', 'Divergence Type'])
    df.to_excel(output_file, index=False, sheet_name='Live Data')

def fetch_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"Failed for {symbol}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def analyze_data(data, symbol):
    records = []
    time_now = datetime.now().strftime("%H:%M:%S")
    if not data:
        return []

    try:
        ce_data = data['records']['data']
        for entry in ce_data:
            strike_price = entry.get('strikePrice')
            for option_type in ['CE', 'PE']:
                option_data = entry.get(option_type)
                if option_data:
                    ltp = option_data.get('lastPrice', 0)
                    change = option_data.get('change', 0)
                    oi = option_data.get('openInterest', 0)
                    change_oi = option_data.get('changeinOpenInterest', 0)

                    # Divergence logic
                    divergence = ''
                    if change > 0 and change_oi < 0:
                        divergence = 'Bearish'
                    elif change < 0 and change_oi > 0:
                        divergence = 'Bullish'

                    if abs(change_oi) > 10000:  # sudden OI spike threshold
                        records.append([
                            time_now, symbol, strike_price, option_type, ltp,
                            change, oi, change_oi, divergence
                        ])
        return records
    except:
        return []

# Main loop
while True:
    all_data = []
    for symbol in nifty_stocks:
        option_data = fetch_option_chain(symbol)
        parsed = analyze_data(option_data, symbol)
        all_data.extend(parsed)

    df = pd.DataFrame(all_data, columns=[
        'Time', 'Symbol', 'Strike Price', 'Option Type',
        'LTP', 'Change (%)', 'OI', 'OI Change', 'Divergence Type'
    ])

    # Save to Excel without overwriting the entire sheet
    with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, index=False, sheet_name='Live Data')

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Data updated.")

    time.sleep(1)  # Update every second

