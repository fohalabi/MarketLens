# 📈 MarketLens

> **Real-time market intelligence, one lens at a time.**

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

---

## 🔭 Overview

**MarketLens** is a full-stack fintech application that provides real-time market data analysis across **Stocks**, **Crypto**, **Forex**, and **Commodities**. Built entirely in Python, it features a REST API, WebSocket price streaming, technical analysis engine, portfolio tracker, price alerts, and an interactive Streamlit dashboard — all containerized with Docker.

This project was built as a portfolio centerpiece to demonstrate production-grade Python and DevOps engineering for fintech development.

---

## ✨ Features

- 📊 **Real-time price tracking** — Stocks, Crypto, Forex, Commodities
- 📈 **Technical analysis engine** — RSI, MACD, Bollinger Bands, SMA, EMA, VWAP, ATR
- 🧠 **Buy/Sell/Hold signals** — Rule-based signal generation from indicators
- 💼 **Portfolio tracker** — Live P&L, return %, allocation charts
- 🔔 **Price alerts** — Create above/below alerts with auto-checking
- ⚡ **WebSocket streaming** — Real-time price updates via WebSocket
- 🗄️ **Historical data storage** — Persist OHLCV data in PostgreSQL
- 🐳 **Fully containerized** — Docker Compose spins up everything in one command
- 📖 **Auto-generated API docs** — Swagger UI at `/docs`
- ✅ **Tested** — pytest suite covering indicators, fetcher, and API endpoints

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.13 | Core application |
| Web Framework | FastAPI | REST API + WebSockets |
| Database | PostgreSQL 15 (Docker) | Persistent storage |
| Cache | Redis 7 (Docker) | Price caching & queues |
| ORM | SQLAlchemy 2.0 | Database models |
| Data Processing | Pandas + NumPy | Time-series analysis |
| Charts | Plotly | Interactive financial charts |
| Market Data | yfinance + ccxt + Alpha Vantage | Stocks, Crypto, Forex, Commodities |
| Dashboard | Streamlit | Visual UI |
| Containerization | Docker + Docker Compose | Service orchestration |
| CI/CD | GitHub Actions | Automated test & deploy |
| Auth | JWT (python-jose) | Secure API access |
| Scheduler | APScheduler | Alert checks |

---

## 🚀 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Python 3.13](https://python.org/downloads)
- [Git](https://git-scm.com)
- [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key) (free)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/market-lens.git
cd market-lens
```

**2. Create your environment file**
```bash
cp .env.example .env
```

**3. Fill in your `.env` file**
```bash
# Required
ALPHA_VANTAGE_API_KEY=your_key_here
SECRET_KEY=your-long-random-secret-key

# Pre-filled defaults (change in production)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=marketlensdb
```

**4. Start everything with Docker**
```bash
docker-compose up --build
```

**5. Open in your browser**

| Service | URL |
|---|---|
| 📖 API Docs (Swagger) | http://localhost:8000/docs |
| 📊 Dashboard | http://localhost:8501 |
| ❤️ Health Check | http://localhost:8000/health |

---

## 📡 API Reference

### Stocks
```
GET  /api/stocks/                        # List all stored stocks
GET  /api/stocks/{symbol}                # Get stock + full analysis
GET  /api/stocks/{symbol}/history        # Get OHLCV history (live)
GET  /api/stocks/{symbol}/history/stored # Get OHLCV history (from DB)
POST /api/stocks/{symbol}/history/save   # Save history to DB
POST /api/stocks/{symbol}/refresh        # Force refresh from Yahoo Finance
```

### Crypto
```
GET /api/crypto/{symbol}           # Get crypto price (e.g. BTC/USDT)
GET /api/crypto/{symbol}/history   # Get OHLCV history
GET /api/crypto/{symbol}/analysis  # Get full analysis + signal
```

### Forex
```
GET /api/forex/{from}/{to}         # Get exchange rate (e.g. EUR/USD)
```

### Commodities
```
GET /api/commodities/              # List supported commodities
GET /api/commodities/{symbol}      # Get commodity price (e.g. WTI, GOLD)
```

### Portfolio
```
GET    /api/portfolio/             # Get portfolio with live P&L
POST   /api/portfolio/             # Add holding
DELETE /api/portfolio/{id}         # Remove holding
```

### Alerts
```
GET    /api/alerts/                # List all alerts
POST   /api/alerts/                # Create price alert
DELETE /api/alerts/{id}            # Delete alert
GET    /api/alerts/check           # Manually trigger alert check
```

### WebSocket
```
WS /ws/prices                      # Real-time price stream
```

**WebSocket usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/prices');
ws.onopen = () => ws.send(JSON.stringify({ symbols: ['AAPL', 'TSLA'] }));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## 📊 Technical Indicators

| Indicator | Description | Signal |
|---|---|---|
| RSI (14) | Relative Strength Index | >70 overbought, <30 oversold |
| MACD | Moving Average Convergence Divergence | Histogram crossover |
| Bollinger Bands | Volatility bands around SMA | Price near bands = reversal |
| SMA 20/50 | Simple Moving Average | Trend direction |
| EMA 20 | Exponential Moving Average | Faster trend response |
| VWAP | Volume Weighted Average Price | Institutional benchmark |
| ATR | Average True Range | Volatility magnitude |

---

## 🐳 Docker Services

```yaml
services:
  app        → FastAPI application  (port 8000)
  db         → PostgreSQL database  (port 5432)
  redis      → Redis cache          (port 6380)
  dashboard  → Streamlit UI         (port 8501)
```

**Useful Docker commands:**
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f app

# Rebuild after code changes
docker-compose up --build
```

---

## 🧪 Running Tests

```bash
# Activate virtual environment
source venv/Scripts/activate   # Windows Git Bash
source venv/bin/activate       # Mac/Linux

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app
```

**Test coverage:**
- `tests/test_indicators.py` — RSI, SMA, MACD, Bollinger Bands calculations
- `tests/test_fetcher.py` — Stock data fetching and parsing
- `tests/test_api.py` — API endpoint responses

---

## 📁 Project Structure

```
market-lens/
├── app/
│   ├── api/routes/          # FastAPI route handlers
│   ├── core/                # Fetcher, indicators, analyzer
│   ├── models/              # SQLAlchemy DB models
│   ├── schemas/             # Pydantic validation schemas
│   ├── services/            # Business logic layer
│   ├── websockets/          # WebSocket price streaming
│   ├── dashboard/           # Streamlit UI
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # App settings
│   └── database.py          # DB connection
├── tests/                   # pytest test suite
├── .github/workflows/       # GitHub Actions CI/CD
├── Dockerfile               # Container definition
├── docker-compose.yml       # Multi-service orchestration
├── requirements.txt         # Python dependencies
└── .env.example             # Environment template
```

---

## 🔄 CI/CD Pipeline

Every push to `main` triggers the GitHub Actions pipeline:

```
Push to main
    │
    ├── 🧪 Run pytest
    ├── 🔍 Run flake8 lint
    ├── ⬛ Run black format check
    │
    └── ✅ All pass →  🐳 Build Docker image
                           │
                           └── 🚀 Deploy to Railway
```

---

## 🌍 Supported Markets

| Asset Class | Source | Examples |
|---|---|---|
| Stocks & Equities | Yahoo Finance (yfinance) | AAPL, TSLA, MSFT, GOOGL |
| Cryptocurrency | ccxt (Binance, Kraken) | BTC/USDT, ETH/USDT |
| Forex | Alpha Vantage | EUR/USD, GBP/USD, JPY/USD |
| Commodities | Alpha Vantage | WTI, BRENT, GOLD, NATURAL_GAS |

---

## 📝 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `SECRET_KEY` | ✅ | JWT signing secret |
| `ALPHA_VANTAGE_API_KEY` | ✅ | Free key from alphavantage.co |
| `BINANCE_API_KEY` | ❌ | Optional — for crypto data |
| `BINANCE_SECRET_KEY` | ❌ | Optional — for crypto data |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

Built with 🔥 by **Fohlabi** ~ evolving from frontend & backend to full-stack Python engineering.

---

<p align="center">
  <strong>MarketLens</strong> — Real-time market intelligence, one lens at a time.
</p>
