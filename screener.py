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
        except:
            pass
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
            df = yf.download(t, period="1mo", interval="1d", progress=False)
            if df is None or len(df) < 15:
                continue

            df['RSI'] = calculate_rsi(df['Close'])
            close_prices = df['Close'].values.flatten()
            
            # Count consecutive drops
            drops = 0
            for i in range(1, down_days + 1):
                if close_prices[-i] < close_prices[-(i+1)]:
                    drops += 1
                else:
                    break
            
            current_rsi = float(df['RSI'].iloc[-1])
            current_price = float(df['Close'].iloc[-1])

            if drops >= down_days and current_rsi < rsi_limit:
                results.append({
                    "Ticker": t, 
                    "RSI": round(current_rsi, 2), 
                    "Price": round(current_price, 2)
                })
        except:
            continue

    df_hits = pd.DataFrame(results if results else [], columns=["Ticker", "RSI", "Price"])
    df_hits.to_csv(output_csv, index=False)
    print(f"Saved {len(results)} matches to {output_csv}")

if __name__ == "__main__":
    s = get_settings()
    run_scan('usa_tickers.txt', 'usa_hits.csv', s['rsi_limit'], s['down_days'])
    run_scan('uk_tickers.txt', 'uk_hits.csv', s['rsi_limit'], s['down_days'])
