# 📈 Stock Technical Analyzer & Portfolio Optimizer

A Flask-based web application that performs technical analysis on real-time stock data. It utilizes statistical indicators (RSI, Bollinger Bands) to generate trading signals, identify trending assets, and optimize portfolio allocation based on a user's budget.

## 🚀 Features

* **Single Stock Analysis:**
* Retrieves real-time data using `yfinance`.
* Calculates **RSI (Relative Strength Index)** and **Bollinger Bands**.
* Generates **Buy, Sell, or Hold** signals with a confidence score.
* Projects potential profit percentages and target prices based on volatility.


## **Market Scanner (Trending):**
* Automatically scans a pre-defined list of popular stocks and ETFs (e.g., AAPL, SPY, NVDA).
* Filters and returns only assets currently showing "BUY" signals.


## **Portfolio Comparison & Optimization:**
* Compares a custom list of user-selected stocks.
* Calculates a proprietary "Attractiveness Score" (0-100) for each asset.
* **Smart Allocation:** Distributes a user's specific budget (e.g., $1,000) across the selected stocks based on their technical strength.



## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Data Source:** Yahoo Finance (`yfinance`)
* **Data Processing:** Pandas, NumPy

<img width="1877" height="982" alt="image" src="https://github.com/user-attachments/assets/23a57f8d-457e-4712-8cc0-ff3e30b9e937" />

## 📦 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/stock-analyzer.git
cd stock-analyzer

```


2. **Create a virtual environment (Optional but recommended):**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

```


3. **Install dependencies:**
Create a `requirements.txt` file with the following content (or install manually):
```text
flask
yfinance
pandas
numpy

```


Then run:
```bash
pip install -r requirements.txt

```



## 🏃‍♂️ Usage

1. **Start the server:**
```bash
python app.py

```


The application will start on `http://127.0.0.1:5000`.
2. **API Endpoints:**
| Method | Endpoint | Description | JSON Body Example |
| --- | --- | --- | --- |
| `POST` | `/predict` | Analyze a specific ticker. | `{"ticker": "NVDA"}` |
| `GET` | `/trending` | Get a list of popular stocks with "BUY" signals. | *None* |
| `POST` | `/compare` | Optimize a portfolio plan. | `{"tickers": ["AAPL", "TSLA"], "budget": 2000}` |



## 📊 Logic Explanation

The application uses a custom algorithm to generate signals:

* **Buy Signal:** Triggered if the Price is below the **Lower Bollinger Band** AND **RSI < 45** (indicating the asset is oversold/undervalued).
* **Sell Signal:** Triggered if **RSI > 70** (indicating the asset is overbought).
* **Profit Projection:** Calculated as the percentage difference between the *Current Price* and the *Upper Bollinger Band*.

## ⚠️ Disclaimer

This application is for **educational and informational purposes only**. The "Buy/Sell" signals are generated based on mathematical formulas (technical analysis) and do not account for fundamental news, economic events, or market sentiment. **Do not use this tool as the sole basis for real financial investment decisions.** Always do your own research.
