import yfinance as yf
import pandas as pd
import os

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_settings():
    # Default values in case the file is missing
    settings = {"rsi_limit": 50, "down_days": 3}
    if os.path.exists('settings.txt'):
        with open('settings.txt', 'r') as f:
            for line in f:
                if ':' in line:
                    key, val = line.split(':')
                    settings[key.strip()] = int(val.strip())
    return settings

def run_scan(filename, output_name, rsi_limit, down_days):
    if not os.path.exists(filename):
        pd.DataFrame(columns=["Ticker", "RSI", "Price"]).to_csv(output_name, index=False)
        return
        
    with open(filename, 'r') as f:
        tickers = [line.strip() for line in f if line.strip()]

    results = []
    for t in tickers:
        try:
            df = yf.download(t, period="1mo", interval="1d", progress=False)
            if df is None or len(df) < 15: continue

            df['RSI'] = calculate_rsi(df['Close'])
            c = df['Close']
            
            # Check for consecutive drops based on settings
            drops = 0
            for i in range(1, down_days + 1):
                if c.iloc[-i] < c.iloc[-(i+1)]:
                    drops += 1
                else:
                    break
            
            current_rsi = df['RSI'].iloc[-1]

            if drops >= down_days and current_rsi < rsi_limit:
                results.append({"Ticker": t, "RSI": round(current_rsi, 2), "Price": round(c.iloc[-1].item(), 2)})
        except:
            continue
            
    df_hits = pd.DataFrame(results if results else [], columns=["Ticker", "RSI", "Price"])
    df_hits.to_csv(output_name, index=False)
    print(f"Finished {filename}: Found {len(results)} matches using RSI < {rsi_limit} and {down_days} down days.")

if __name__ == "__main__":
    s = get_settings()
    run_scan('usa_tickers.txt', 'usa_hits.csv', s['rsi_limit'], s['down_days'])
    run_scan('uk_tickers.txt', 'uk_hits.csv', s['rsi_limit'], s['down_days'])
