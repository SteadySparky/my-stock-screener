import yfinance as yf
import pandas as pd
import pandas_ta as ta

# Mix of US and UK Tickers
tickers = ["AAPL", "TSLA", "INTC", "PARA", "VOD.L", "BARC.L", "LLOY.L", "BT-A.L"]

def screen():
    print(f"Scanning {len(tickers)} stocks...")
    results = []
    for t in tickers:
        try:
            df = yf.download(t, period="1mo", interval="1d", progress=False)
            if len(df) < 10: continue

            # RSI Calculation
            df['RSI'] = ta.rsi(df['Close'], length=14)
            current_rsi = df['RSI'].iloc[-1]

            # 3-Day Drop Logic
            # Checks if Today < Yesterday AND Yesterday < Day Before
            three_day_drop = (df['Close'].iloc[-1] < df['Close'].iloc[-2]) and \
                             (df['Close'].iloc[-2] < df['Close'].iloc[-3])

            if three_day_drop and current_rsi < 45:
                results.append({"Ticker": t, "RSI": round(current_rsi, 2), "Price": round(df['Close'].iloc[-1], 2)})
        except:
            continue
            
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        print("\n--- MATCHES FOUND ---")
        print(df_results.to_string(index=False))
        df_results.to_csv("hits.csv", index=False)
    else:
        print("\nNo stocks matched the criteria today.")

if __name__ == "__main__":
    screen()
