import yfinance as yf
import pandas as pd

# List of stocks to check
tickers = ["AAPL", "TSLA", "INTC", "PARA", "VOD.L", "BARC.L", "LLOY.L"]

def calculate_rsi(series, period=14):
    """Manually calculate RSI without extra libraries"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def screen():
    print("Starting Market Scan...")
    results = []
    
    for t in tickers:
        try:
            # Download data
            df = yf.download(t, period="1mo", interval="1d", progress=False)
            if len(df) < 15: continue

            # Calculate RSI
            df['RSI'] = calculate_rsi(df['Close'])
            current_rsi = df['RSI'].iloc[-1]

            # 3-Day Drop Logic
            # Close[today] < Close[yesterday] AND Close[yesterday] < Close[day_before]
            c = df['Close']
            is_dropping = (c.iloc[-1] < c.iloc[-2]) and (c.iloc[-2] < c.iloc[-3])

            print(f"Checked {t}: RSI is {round(current_rsi, 2)}")

            # Criteria: RSI under 45 and 3-day price drop
            if is_dropping and current_rsi < 45:
                results.append({"Ticker": t, "RSI": round(current_rsi, 2), "Price": round(c.iloc[-1], 2)})

        except Exception as e:
            print(f"Error scanning {t}: {e}")
            
    if results:
        print("\n✅ MATCHES FOUND:")
        print(pd.DataFrame(results).to_string(index=False))
    else:
        print("\nNo stocks matched the criteria today.")

if __name__ == "__main__":
    screen()
