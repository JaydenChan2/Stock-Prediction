# Stock-Predictive-Model
This predictive algorithm is a full-stack financial analysis tool built with Python (Flask) and JavaScript. It implements a Mean Reversion strategy using RSI and Bollinger Bands to identify oversold "Buy Zones" for stocks and crypto. The app features a real-time REST API, vectorised pandas calculations, and an interactive Chart.js frontend.

## 🚀 Features
- **Real-Time Data:** Fetches live market data for Stocks, ETFs, and Crypto using `yfinance`.
- **Algorithmic Analysis:** Calculates **RSI** and **Bollinger Bands** to detect statistically "oversold" conditions.
- **Interactive UI:** Visualizes price action and "Buy Zones" dynamically with **Chart.js**.
- **REST API:** Built with **Flask** to serve JSON signals to the frontend.

## 🛠️ Tech Stack
- **Backend:** Python, Flask, Pandas, NumPy, Yfinance
- **Frontend:** HTML5, CSS3, JavaScript (Chart.js)

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install flask yfinance pandas numpy
