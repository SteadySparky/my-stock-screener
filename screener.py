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
            
            # Logic: 3-day drop + RSI < 50
            is_dropping = (c.iloc[-1] < c.iloc[-2]) and (c.iloc[-2] < c.iloc[-3])
            current_rsi = df['RSI'].iloc[-1]

            if is_dropping and current_rsi < 50:
                results.append({"Ticker": t, "RSI": round(current_rsi, 2), "Price": round(c.iloc[-1].item(), 2)})
        except:
            continue
            
    # Always save, even if empty, to prevent GitHub Action errors
    df_hits = pd.DataFrame(results if results else [], columns=["Ticker", "RSI", "Price"])
    df_hits.to_csv(output_name, index=False)
    print(f"Finished {filename}: Found {len(results)} matches.")

if __name__ == "__main__":
    run_scan('usa_tickers.txt', 'usa_hits.csv')
    run_scan('uk_tickers.txt', 'uk_hits.csv')
