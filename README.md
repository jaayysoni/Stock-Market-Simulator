# Crypto Trading Simulator

## Overview

The Crypto Trading Simulator is a high-performance, real-time trading platform built with Python and FastAPI. It demonstrates backend engineering expertise in handling real-time data, scalable API design, and performance optimization.

Key highlights include:
- **Real-time updates:** Tracks live cryptocurrency prices and portfolio values using ~90 WebSocket connections and APIs.  
- **Interactive experience:** Instant updates on prices, balances, and transactions.  
- **Backend-focused design:** Showcases async handling, caching, and scalable system architecture.  
- **Risk-free environment:** Users can practice trading strategies without financial exposure.  
- **Ideal for:** Developers exploring backend systems, real-time applications, and cloud deployments.

## Application Screenshots

<p align="center">
  <img src="https://github.com/user-attachments/assets/596fc5f9-b8ed-4da8-aa21-09726e47cf98" width="800">
  <br>
  <strong>Dashboard View</strong>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/fa4f08b3-1df4-4244-b55a-3c04e86d8208" width="800">
  <br>
  <strong>Transactions</strong>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/721c8edf-4bc0-42b7-852c-bfd6f9072e9c" width="800">
  <br>
  <strong>Portfolio</strong>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/8a035427-f95f-4332-982e-52133ebd5c15" width="800">
  <br>
  <strong>Trading Terminal View</strong>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/9d0790c9-d7b3-4cb3-bb9d-dbc4221f7f06" width="800">
  <br>
  <strong>Trading Terminal — Successful Order Execution</strong>
</p>


## Problem Statement

Cryptocurrency markets are highly volatile and largely unregulated, making trading risky for beginners. Studies show over 80% of new traders lose capital within their first year, while only a small fraction achieve consistent profitability.

Most educational tools lack real-time data or fail to expose users to actual market risks. The Crypto Trading Simulator provides a risk-free, real-time environment where users can experience price volatility and trading challenges without using real money.

## Objective

The primary objectives of the Crypto Trading Simulator are to:

- Provide a **real-time, risk-free environment** to practice cryptocurrency trading.  
- Expose users to **live market volatility** and real-time data using WebSockets and APIs.  
- Demonstrate **backend expertise**: scalable APIs, async handling, caching, and performance optimization.  
- Offer an **interactive platform** for exploring trading strategies without financial risk.

## Methodology

The Crypto Trading Simulator was developed using an **Agile, iterative approach** with a focus on backend performance and real-time data handling. Key aspects include:

- **Backend-first design:** Built with Python 3.13.2 and FastAPI for scalable, low-latency operations.  
- **Real-time processing:** ~90 WebSocket connections and APIs provide live price updates and portfolio tracking.  
- **Performance optimization:** Caching and asynchronous handling ensure efficient, responsive updates.  
- **Testing & validation:** Ensured data consistency, prevented race conditions, and handled high-frequency updates.  
- **Deployment & CI/CD:** Cloud-ready deployment with CI/CD pipelines for seamless updates and integration.

## Features

### User-Facing Features

- **Live Dashboard:** Real-time prices and 24-hour changes for the top 90 cryptocurrencies.  
- **Portfolio Tracking:** Shows current prices, total value, and profit/loss (P/L).  
- **Transaction History:** Complete log of all buy/sell operations.  
- **Virtual Money Management:** Add or deduct unlimited virtual funds to test strategies.  
- **Trading Terminal:** Interactive charts for analyzing price trends and executing virtual trades.

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
