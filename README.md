# Crypto Trading Simulator

## Overview

The **Crypto Trading Simulator** is a high-performance, real-time trading platform built with Python and FastAPI. Key highlights include:

- **Real-time updates:** Tracks live cryptocurrency prices and portfolio values using ~90 WebSocket connections and real-time APIs.  
- **Interactive trading experience:** Instant updates on prices, balances, and transactions.  
- **Backend expertise showcase:** Demonstrates skills in real-time data handling, performance optimization, and scalable API design.  
- **Risk-free learning environment:** Users can simulate trading strategies without real financial exposure.

## Problem Statement

Cryptocurrency markets are **highly volatile and largely unregulated**, meaning prices can swing dramatically without warning and there’s no government protection or oversight for traders. This instability makes crypto trading **inherently risky**, especially for beginners who may not fully understand market dynamics or risk management.

- A large majority of retail crypto traders lose money: studies show that **over 80% of new traders lose capital within their first year**, with many losing nearly all of their investment.
- Only a small fraction of traders — roughly **10–20% — achieve consistent profitability** over time, while the rest face losses due to volatility, leverage, and emotional decision‑making.
- On average, beginner traders can experience **significant losses**, especially in highly leveraged futures or day trading, where many lose **70–90% of capital** in their first year.

Most educational platforms and tools either lack **real-time data** or fail to expose users to the **true risk environment** of live markets. The **Crypto Trading Simulator** fills this gap by providing a **real-time, hands‑on environment** where users can experience price volatility and trading risks *without using real money*, giving them a practical sense of how unpredictable and unstable crypto markets can be.

## Objective

The primary objectives of the **Crypto Trading Simulator** are:

- Provide a **real-time, risk-free environment** for users to practice cryptocurrency trading.  
- Expose users to **live market volatility and price fluctuations** using ~90 WebSocket connections and real-time APIs.  
- Help users **understand the risks** involved in trading unregulated and unstable markets.  
- Demonstrate **backend development expertise**, including performance optimization, scalable API design, and real-time data handling.  
- Create an **interactive, engaging platform** for both beginners and enthusiasts to explore trading strategies without financial loss.

## Methodology

The **Crypto Trading Simulator** was developed using an **Agile, iterative approach**, focusing on incremental development and testing. Key aspects of the methodology include:

- **Backend-first architecture:** Built using **Python 3.13.2** and FastAPI to handle real-time trading data and WebSocket connections efficiently.  
- **Real-time data handling:** Integrated ~90 WebSocket connections and APIs to provide live price updates and portfolio tracking.  
- **Performance optimization:** Implemented caching strategies and asynchronous handling to ensure low-latency, scalable updates.  
- **Testing and validation:** Conducted rigorous testing to ensure data consistency, prevent race conditions, and handle high-frequency updates.  
- **Deployment and CI/CD:** Hosted on Render (Singapore region) with a CI/CD pipeline using GitHub Actions for seamless updates and continuous integration.

## Features

### User-Facing Features
- **Live Dashboard:** Displays real-time prices and 24-hour price changes for the **top 90 most traded cryptocurrencies**.  
- **Portfolio Tracking:** Shows current prices, total value, and **profit/loss (P/L)** for individual holdings or the overall portfolio.  
- **Transaction History:** Records all buy and sell operations across all time, providing a **complete trade log**.  
- **Virtual Money Management:** Users can **add or deduct unlimited virtual money** freely to practice different trading strategies.  
- **Trading Terminal:** Interactive live chart for any selected cryptocurrency, allowing users to **analyze price trends and trade virtually**.

### Technical Features
- Built with **Python 3.13.2** and **FastAPI** for high-performance backend operations.  
- Handles **~90 WebSocket connections** for real-time price streaming of top cryptocurrencies.  
- Integrates multiple **real-time APIs** for accurate market data.  
- **Asynchronous and optimized** backend for low-latency updates.  
- Caching implemented to **reduce redundant API calls** and improve system efficiency.  
- Deployed on **Render (Singapore region)** with CI/CD pipeline using GitHub Actions.

## Tech Stack

| Layer / Purpose       | Technology / Tool                  |
|-----------------------|------------------------------------|
| Backend               | Python 3.13.2, FastAPI             |
| Real-Time Data        | WebSockets (~90 connections), APIs |
| Database              | SQLite                             |
| Caching               | Redis                              |
| Frontend              | HTML, CSS, JavaScript              |
| Charts / Visualization| Trading Terminal Live Charts       |
| Hosting / Deployment  | Render (Singapore region)          |
| CI/CD                 | GitHub Actions                     |
| Version Control       | Git                                |


## Software Requirements

- **Python 3.13.2** – Backend development and real-time API handling.  
- **Redis** – Caching for real-time data and WebSocket performance.  
- **SQLite** – Local database for storing portfolio and transaction data.  
- **Git** – Version control and repository management.  
- **Web Browser** – For accessing the frontend dashboard, trading terminal, and portfolio.  
- **Render Account (optional)** – For deployment of live simulator (Singapore region).

## Hardware Requirements

- **Processor:** Intel i3 / AMD Ryzen 3 or higher  
- **RAM:** 4 GB minimum (8 GB recommended for smooth performance)  
- **Storage:** 2 GB free space (for Python, Redis, and SQLite)  
- **Internet Connection:** Stable connection for real-time price updates and WebSocket streaming  
- **Browser:** Safari, Chrome, Firefox, Edge (latest versions recommended)

## Installation & Running Instructions

Follow these steps to set up and run the Crypto Trading Simulator locally:

1. **Clone the repository**
```bash
git clone https://github.com/jaayysoni/Crypto-Trading-Simulator.git
cd Crypto-Trading-Simulator
```
2.	**Create a virtual environment**
```
python -m venv venv
```
3.	**Activate the virtual environment**

Windows
```
venv\Scripts\activate
```
Mac/Linux
```
source venv/bin/activate
```
4.	Install dependencies
```
pip install -r requirements.txt
```
5.	Start the backend server
```
uvicorn app.main:app --reload
```
6.	Access the frontend
	•	Open your browser (Safari, Chrome, Firefox, Edge)
	•	Go to: http://localhost:8000


## Project Structure

```
Crypto-Trading-Simulator/
│
├── app/                         # Backend application
│   ├── init.py
│   ├── config.py                # Configuration settings
│   ├── constants/               # Constant values like coin data
│   │   └── coin.py
│   ├── database/                # Database setup and session management
│   │   ├── db.py
│   │   ├── init_db.py
│   │   └── session.py
│   ├── main.py                  # FastAPI entry point
│   ├── models/                  # Pydantic/SQLAlchemy models
│   │   ├── balance.py
│   │   ├── crypto.py
│   │   └── transaction.py
│   ├── schemas/                 # Pydantic schemas
│   │   ├── portfolio_schemas.py
│   │   └── transaction_schema.py
│   ├── services/                # Business logic layer
│   │   ├── balance_transaction.py
│   │   ├── crypto_ws.py
│   │   ├── price_service.py
│   │   └── transaction_services.py
│   ├── tasks/                   # Background tasks and scheduler
│   │   ├── init.py
│   │   └── scheduler.py
│   └── utils/                   # Helper utilities
│       ├── cache.py
│       └── redis_client.py
│
├── docs/                         # Documentation
│   ├── api_docs.md
│   └── setup_guide.md
│
├── static/                       # Frontend assets
│   ├── css/
│   │   ├── dashboard.css
│   │   ├── portfolio.css
│   │   ├── tradingterminal.css
│   │   └── transaction.css
│   ├── js/
│   │   ├── dashboard.js
│   │   ├── portfolio.js
│   │   ├── tradingterminal.js
│   │   └── transaction.js
│   ├── dashboard.html
│   ├── portfolio.html
│   ├── tradingterminal.html
│   └── transaction.html
│
├── insert_crypto.py              # Script to seed crypto data
├── requirements.txt              # Python dependencies
├── app.db                        # SQLite database file
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── README.md                     # Project README
```










