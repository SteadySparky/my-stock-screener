import yfinance as yf
import pandas as pd
import os

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_scan(filename, output_name):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found!")
        return []
        
    with open(filename, 'r') as f:
        tickers = [line.strip() for line in f if line.strip()]

    print(f"--- Scanning {len(tickers)} stocks from {filename} ---")
    results = []
    
    for t in tickers:
        try:
            df = yf.download(t, period="1mo", interval="1d", progress=False)
            if len(df) < 15: continue

            df['RSI'] = calculate_rsi(df['Close'])
            c = df['Close']
            
            # Logic: Price dropped 3 days in a row + RSI under 50
            is_dropping = (c.iloc[-1] < c.iloc[-2]) and (c.iloc[-2] < c.iloc[-3])
            current_rsi = df['RSI'].iloc[-1]

            if is_dropping and current_rsi < 50:
                results.append({"Ticker": t, "RSI": round(current_rsi, 2), "Price": round(c.iloc[-1], 2)})
        except:
            continue
            
    if results:
        df_hits = pd.DataFrame(results)
        df_hits.to_csv(output_name, index=False)
        print(f"Found {len(results)} matches. Saved to {output_name}")
    else:
        # Create an empty file so GitHub doesn't error out
        pd.DataFrame(columns=["Ticker", "RSI", "Price"]).to_csv(output_name, index=False)
        print(f"No matches found for {filename}.")

if __name__ == "__main__":
    run_scan('usa_tickers.txt', 'usa_hits.csv')
    run_scan('uk_tickers.txt', 'uk_hits.csv')
