from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

# --- THE ALGORITHM ---
def calculate_technical_signals(ticker):
    # 1. Fetch Data (1 Year of history to ensure valid Moving Averages)
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty:
            return None
        
        # Flatten MultiIndex columns if necessary (yfinance update fix)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 2. Calculate Bollinger Bands
        # Middle Band = 20 Day Simple Moving Average (SMA)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        # Standard Deviation
        df['STD_20'] = df['Close'].rolling(window=20).std()
        # Upper/Lower Bands (2 Standard Deviations)
        df['Upper_Band'] = df['SMA_20'] + (df['STD_20'] * 2)
        df['Lower_Band'] = df['SMA_20'] - (df['STD_20'] * 2)

        # 3. Calculate RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 4. Generate Signal (The "Brain")
        latest = df.iloc[-1]
        signal = "NEUTRAL"
        confidence = 0

        # BUY LOGIC: Price < Lower Band AND RSI < 30 (Oversold)
        if latest['Close'] < latest['Lower_Band'] and latest['RSI'] < 30:
            signal = "STRONG BUY"
            confidence = 90
        elif latest['Close'] < latest['Lower_Band']:
            signal = "BUY"
            confidence = 60
        elif latest['RSI'] > 70:
            signal = "SELL"
            confidence = 80
            
        return {
            "current_price": round(float(latest['Close']), 2),
            "signal": signal,
            "rsi": round(float(latest['RSI']), 2),
            "lower_band": round(float(latest['Lower_Band']), 2),
            "dates": df.index.strftime('%Y-%m-%d').tolist()[-50:], # Send last 50 days for charting
            "prices": df['Close'].tail(50).tolist(),
            "lower_band_data": df['Lower_Band'].tail(50).tolist()
        }

    except Exception as e:
        print(f"Error: {e}")
        return None

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    ticker = data.get('ticker', 'SPY').upper()
    result = calculate_technical_signals(ticker)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Ticker not found or data error"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)