import yfinance as yf
import pandas as pd
import os

def calculate_rsi(series, period=14):
    """Standard RSI calculation"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_settings():
    """Reads settings.txt or uses defaults"""
    settings = {"rsi_limit": 50, "down_days": 3}
    if os.path.exists('settings.txt'):
        try:
            with open('settings.txt', 'r') as f:
                for line in f:
                    if ':' in line:
                        key, val = line.split(':')
                        settings[key.strip().lower()] = int(val.strip())
        except Exception as e:
            print(f"Settings error: {e}. Using defaults.")
    return settings

def run_scan(ticker_file, output_csv, rsi_limit, down_days):
    """Scans a specific list of tickers and saves results"""
    if not os.path.exists(ticker_file):
        print(f"Skipping {ticker_file}: File not found.")
        pd.DataFrame(columns=["Ticker", "RSI", "Price"]).to_csv(output_csv, index=False)
        return

    with open(ticker_file, 'r') as f:
        tickers = [line.strip() for line in f if line.strip()]

    print(f"\n--- Scanning {len(tickers)} stocks from {ticker_file} ---")
    results = []
    
    for t in tickers:
        try:
            # Get 1 month of daily data
            df = yf.download(t, period="1mo", interval="1d", progress=False)
            if df is None or len(df) < 15:
                continue

            # Calculate RSI
            df['RSI'] = calculate_rsi(df['Close'])
            
            # Logic: Check for consecutive lower closes
            # We use .iloc[-1].item() to get a clean number from the table
            close_prices = df['Close'].values.flatten()
            
            drops = 0
            for i in range(1, down_days + 1):
                if close_prices[-i] < close_prices[-(i+1)]:
                    drops += 1
                else:
                    break
            
            current_rsi = float(df['RSI'].iloc[-
