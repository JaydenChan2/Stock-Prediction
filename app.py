from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import numpy as np

POPULAR_TICKERS = [
    {"symbol": 'AAPL', "name": "Apple Inc.", "type": "Stock"},
    {"symbol": 'MSFT', "name": "Microsoft Corp.", "type": "Stock"},
    {"symbol": 'GOOGL', "name": "Alphabet Inc.", "type": "Stock"},
    {"symbol": 'AMZN', "name": "Amazon.com Inc.", "type": "Stock"},
    {"symbol": 'TSLA', "name": "Tesla Inc.", "type": "Stock"},
    {"symbol": 'NVDA', "name": "NVIDIA Corp.", "type": "Stock"},
    {"symbol": 'SPY', "name": "SPDR S&P 500 ETF Trust", "type": "ETF"},
    {"symbol": 'QQQ', "name": "Invesco QQQ Trust", "type": "ETF"},
    {"symbol": 'IWM', "name": "iShares Russell 2000 ETF", "type": "ETF"},
    {"symbol": 'AMD', "name": "Advanced Micro Devices", "type": "Stock"},
    {"symbol": 'META', "name": "Meta Platforms Inc.", "type": "Stock"},
    {"symbol": 'NFLX', "name": "Netflix Inc.", "type": "Stock"},
    {"symbol": 'INTC', "name": "Intel Corp.", "type": "Stock"},
    {"symbol": 'BA', "name": "Boeing Co.", "type": "Stock"},
    {"symbol": 'JPM', "name": "JPMorgan Chase & Co.", "type": "Stock"},
    {"symbol": 'V', "name": "Visa Inc.", "type": "Stock"},
    {"symbol": 'PG', "name": "Procter & Gamble Co.", "type": "Stock"},
    {"symbol": 'UNH', "name": "UnitedHealth Group Inc.", "type": "Stock"},
    {"symbol": 'HD', "name": "Home Depot Inc.", "type": "Stock"},
    {"symbol": 'MA', "name": "Mastercard Inc.", "type": "Stock"},
    {"symbol": 'XOM', "name": "Exxon Mobil Corp.", "type": "Stock"},
    {"symbol": 'JNJ', "name": "Johnson & Johnson", "type": "Stock"},
    {"symbol": 'VBO', "name": "Vanguard Bond ETF", "type": "ETF"},
    {"symbol": 'GLD', "name": "SPDR Gold Shares", "type": "ETF"},
    {"symbol": 'SLV', "name": "iShares Silver Trust", "type": "ETF"}
]

app = Flask(__name__)

def calculate_technical_signals(ticker):
    # Gathering relevant data for the past year
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty:
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Calculate Bollinger Bands
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        # Standard Deviation
        df['STD_20'] = df['Close'].rolling(window=20).std()
        # Upper/Lower Bands (2 Standard Deviations)
        df['Upper_Band'] = df['SMA_20'] + (df['STD_20'] * 2)
        df['Lower_Band'] = df['SMA_20'] - (df['STD_20'] * 2)

        # Calculate RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Generate Signal Based on Latest Data
        latest = df.iloc[-1]
        signal = "NEUTRAL"
        confidence = 0

        # Logic: Price < Lower Band AND RSI < 30 (Oversold)
        if latest['Close'] < latest['Lower_Band'] and latest['RSI'] < 30:
            signal = "STRONG BUY"
            confidence = 90
        elif latest['Close'] < latest['Lower_Band']:
            signal = "BUY"
            confidence = 60
        elif latest['RSI'] < 45:
            signal = "BUY"
            confidence = 50
        elif latest['RSI'] > 70:
            signal = "SELL"
            confidence = 80
            
        return {
            "current_price": round(float(latest['Close']), 2),
            "signal": signal,
            "rsi": round(float(latest['RSI']), 2),
            "lower_band": round(float(latest['Lower_Band']), 2),
            "sma20": round(float(latest['SMA_20']), 2), # Needed for scoring
            "dates": df.index.strftime('%Y-%m-%d').tolist()[-50:], # Send last 50 days for charting
            "prices": df['Close'].tail(50).tolist(),
            "lower_band_data": df['Lower_Band'].tail(50).tolist(),
            # Projections
            "lower_band_data": df['Lower_Band'].tail(50).tolist(),
            # Projections
            "target_price": round(float(latest['Upper_Band']), 2),
            "potential_profit": round(((latest['Upper_Band'] - latest['Close']) / latest['Close']) * 100, 2),
            "holding_period": "2-4 Weeks" if signal == "BUY" or signal == "STRONG BUY" else "Wait for Signal",
            # Company Info
            "company_name": yf.Ticker(ticker).info.get('longName', ticker)
        }

    except Exception as e:
        print(f"Error: {e}")
        return None

def calculate_score(data):
    # Base score
    score = 50
    
    # Technical Boosts
    if data['current_price'] < data['lower_band']:
        score += 20
    elif data['current_price'] < data['sma20']:
        score += 10
        
    if data['rsi'] < 30:
        score += 20
    elif data['rsi'] < 40:
        score += 10
    
    # Technical Penalties
    if data['rsi'] > 70:
        score = 0 # Do not buy
    elif data['rsi'] > 60:
        score -= 10
        
    return max(0, min(100, score))

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

@app.route('/trending')
def trending():
    trending_stocks = []
    
    for item in POPULAR_TICKERS:
        ticker = item['symbol']
        try:
            result = calculate_technical_signals(ticker)
            if result and "BUY" in result['signal']:
                trending_stocks.append({
                    "ticker": ticker,
                    "name": item['name'],
                    "type": item['type'],
                    "price": result['current_price'],
                    "signal": result['signal'],
                    "rsi": result['rsi']
                })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
            
    return jsonify(trending_stocks)

@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()
    tickers = [t.strip().upper() for t in data.get('tickers', []) if t.strip()]
    budget = float(data.get('budget', 1000))
    
    if not tickers:
        return jsonify({"error": "No tickers provided"}), 400

    results = []
    total_score = 0
    
    # 1. Calculate Scores
    for ticker in tickers:
        try:
            tech_data = calculate_technical_signals(ticker)
            if tech_data:
                score = calculate_score(tech_data)
                results.append({
                    "ticker": ticker,
                    "price": tech_data['current_price'],
                    "signal": tech_data['signal'],
                    "rsi": tech_data['rsi'],
                    "score": score
                })
                total_score += score
        except Exception as e:
            print(f"Error comparing {ticker}: {e}")
            
    # 2. Allocate Budget
    portfolio = []
    for item in results:
        if total_score > 0 and item['score'] > 0:
            allocation_pct = item['score'] / total_score
            allocation_amt = allocation_pct * budget
        else:
            allocation_pct = 0
            allocation_amt = 0
            
        portfolio.append({
            "ticker": item['ticker'],
            "price": item['price'],
            "signal": item['signal'],
            "score": item['score'],
            "allocation_pct": round(allocation_pct * 100, 1),
            "allocation_amt": round(allocation_amt, 2)
        })
        
    # Sort by allocation amount (descending)
    portfolio.sort(key=lambda x: x['allocation_amt'], reverse=True)
    
    return jsonify(portfolio)

if __name__ == '__main__':
    app.run(debug=True, port=5000)