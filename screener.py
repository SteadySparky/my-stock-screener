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
    settings = {"rsi_limit": 50, "down_days": 3}
    if os.path.exists('settings.txt'):
        try:
            with open('settings.txt', 'r') as f:
                for line in f:
                    if ':' in line:
                        key, val = line.split(':')
                        settings[key.strip().lower()] = int(val.strip())
        except: pass
    return settings

def run_scan(ticker_file, output_csv, rsi_limit, down_days):
    if not os.path.exists(ticker_file):
        pd.DataFrame(columns=["Ticker", "RSI", "Price"]).to_csv(output_csv, index=False)
        return

    with open(ticker_file, 'r') as f:
        tickers = [line.strip() for line in f if line.strip()]

    print(f"--- Scanning {ticker_file} ---")
    results = []
    
    for t in tickers:
        try:
            # FIX: auto_adjust=True and actions=False makes the data cleaner
            df = yf.download(t, period="1mo", interval="1d", progress=False, auto_adjust=True)
            
            if df.empty or len(df) < 15:
                continue

            # FIX: Ensure we are looking at the 'Close' column regardless of multi-index
            if 'Close' in df.columns:
                price_col = df['Close']
            else:
                # If yfinance used the ticker as a header, grab the first column
                price_col = df.iloc[:, 0] 

            # Calculate RSI on the clean price column
            rsi_series = calculate_rsi(price_col)
            
            # Count consecutive drops
            drops = 0
            # We use .values to avoid index issues
            prices = price_col.values.flatten()
            
            for i in range(1, down_days + 1):
                if prices[-i] < prices[-(i+1)]:
                    drops += 1
                else:
                    break
            
            current_rsi = float(rsi_series.iloc[-1])
            current_price = float(prices[-1])

            print(f"{t}: RSI {round(current_rsi,1)}, Drops {drops}")

            if drops >= down_days and current_rsi < rsi_limit:
                results.append({
                    "Ticker": t, 
                    "RSI": round(current_rsi, 2), 
                    "Price": round(current_price, 2)
                })
        except Exception as e:
            print(f"Error scanning {t}: {e}")
            continue

    df_hits = pd.DataFrame(results if results else [], columns=["Ticker", "RSI", "Price"])
    df_hits.to_csv(output_csv, index=False)
    print(f"DONE: Found {len(results)} matches.")

if __name__ == "__main__":
    s = get_settings()
    print(f"Target: RSI < {s['rsi_limit']} and {s['down_days']}+ drops")
    run_scan('usa_tickers.txt', 'usa_hits.csv', s['rsi_limit'], s['down_days'])
    run_scan('uk_tickers.txt', 'uk_hits.csv', s['rsi_limit'], s['down_days'])
