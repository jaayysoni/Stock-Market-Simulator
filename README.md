# Crypto Trading Simulator
[![Live Demo](https://img.shields.io/badge/Live-Demo-green)](https://crypto.jaayysoni.com)

[![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/-SQLite-003B57?style=flat&logo=sqlite)](https://www.sqlite.org/)
[![Redis](https://img.shields.io/badge/-Redis-DC382D?style=flat&logo=redis)](https://redis.io/)
[![HTML5](https://img.shields.io/badge/-HTML5-E34F26?style=flat&logo=html5)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/-CSS3-1572B6?style=flat&logo=css3)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=000000)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![API](https://img.shields.io/badge/-API-4FC08D?style=flat&logo=api)]()
[![WebSockets](https://img.shields.io/badge/-WebSockets-000000?style=flat&logo=websockets)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![AWS](https://img.shields.io/badge/-AWS-FF9900?style=flat&logo=amazonaws&logoColor=FFFFFF)](https://aws.amazon.com/)
[![GitHub Actions](https://img.shields.io/badge/-CI/CD-2088FF?style=flat&logo=githubactions)](https://github.com/features/actions)
[![GitHub Actions](https://img.shields.io/badge/-GitHub%20Actions-2088FF?style=flat&logo=githubactions)](https://github.com/features/actions)
[![Git](https://img.shields.io/badge/-Git-F05032?style=flat&logo=git)](https://git-scm.com/)

## Overview

The **Crypto Trading Simulator** is a real-time trading platform built with **Python and FastAPI**, designed to demonstrate strong **backend engineering fundamentals** such as real-time data processing, scalable API design, and performance optimization.

This project focuses on **how real-world trading systems work behind the scenes**, including live price streaming, portfolio updates, and transaction handling — all in a **risk-free simulated environment**.

## Live Demo / Deployment

The Crypto Trading Simulator is deployed and running on **AWS EC2** with **Nginx** as a reverse proxy and **Let's Encrypt SSL** for HTTPS:

- **URL:** [https://crypto.jaayysoni.com](https://crypto.jaayysoni.com)
- **Hosting Provider:** AWS EC2 (Amazon Linux 2023)
- **Web Server:** Nginx
- **SSL Certificate:** Let’s Encrypt (HTTPS enabled)
- **Cloud Skills Demonstrated:** EC2 setup, security groups, firewall configuration, domain mapping, HTTPS configuration

**Key highlights:**
- **Real-time system:** Streams live cryptocurrency prices and portfolio updates using ~90 concurrent WebSocket connections.
- **High-performance backend:** Built with async FastAPI, efficient request handling, and caching for low-latency updates.
- **Interactive trading flow:** Instant updates to balances, portfolios, and transaction history.
- **Backend-first architecture:** Clear separation of business logic, services, and infrastructure components.
- **Learning-focused and production-ready:** Ideal for showcasing backend, real-time systems, and cloud deployment skills.

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

Learning how trading systems work is challenging because most educational platforms either lack **real-time market data** or do not reflect the **performance and complexity of real trading environments**.

As a result, developers and beginners rarely get hands-on exposure to:
- Live price volatility
- Real-time portfolio updates
- High-frequency data flows

The **Crypto Trading Simulator** addresses this gap by providing a **real-time, risk-free trading environment** that mirrors key backend challenges found in production trading systems, without involving real money.

## Objective

The primary objective of the **Crypto Trading Simulator** is to design and implement a **real-time backend system** that mirrors the core technical challenges of modern trading platforms.

Specifically, this project aims to:
- Build a **real-time, risk-free trading environment** for simulating cryptocurrency trades.
- Process **live market data** using WebSockets and external APIs.
- Demonstrate strong **backend engineering skills**, including async request handling, caching, and scalable API design.
- Deliver an **interactive system** where portfolio data, balances, and transactions update instantly.

## Methodology

The Crypto Trading Simulator was developed with a strong focus on **backend performance, reliability, and real-time data handling**, following an iterative development process.

Key implementation details include:
- **Backend-first architecture:** Implemented using Python 3.13.2 and FastAPI to support asynchronous, low-latency APIs.
- **Real-time data flow:** Utilized ~90 concurrent WebSocket connections and external APIs to stream live cryptocurrency prices and portfolio updates.
- **Performance optimization:** Applied caching and async processing to minimize redundant API calls and ensure responsive updates.
- **Data consistency and safety:** Handled high-frequency updates while preventing race conditions and ensuring accurate portfolio and transaction states.
- **Deployment and automation:** Deployed to the cloud with automated CI/CD using GitHub Actions for reliable and repeatable releases.

## Features

### User-Facing Features

- **Live Market Dashboard:** Displays real-time prices and 24-hour changes for the top 90 cryptocurrencies.
- **Portfolio Tracking:** Automatically updates current holdings, total portfolio value, and profit/loss (P/L).
- **Transaction History:** Maintains a complete, timestamped record of all buy and sell operations.
- **Virtual Funds Management:** Allows users to add or adjust virtual balances to simulate different trading strategies.
- **Trading Terminal:** Provides interactive charts and controls for analyzing price movements and executing simulated trades.

### Technical Features

- Built using **Python 3.13.2** and **FastAPI**, leveraging async capabilities for high-performance backend operations.
- Manages **~90 concurrent WebSocket connections** to stream live cryptocurrency prices in real time.
- Integrates multiple **external real-time APIs** to fetch and synchronize accurate market data.
- Implements an **asynchronous, non-blocking architecture** to ensure low-latency updates under frequent data changes.
- Uses **Redis-based caching** to reduce redundant API calls and improve overall system efficiency.
- **Deployed to the cloud** on AWS EC2 (Mumbai region) with an automated **CI/CD pipeline using GitHub Actions**.

## Cloud Deployment & Architecture

This project demonstrates production-level cloud deployment:

- **Server:** AWS EC2 instance running Amazon Linux 2023
- **Web Server / Reverse Proxy:** Nginx configured for SSL termination
- **Domain Management:** Custom domain (crypto.jaayysoni.com) configured to point to EC2 public IP
- **SSL Certificate:** Let's Encrypt used for HTTPS
- **CI/CD:** Automated deployment pipeline using GitHub Actions
- **Performance:** Optimized for real-time WebSocket connections (~90 users) with Redis caching

  
## Tech Stack

| Layer / Purpose        | Technology / Tool                                   |
|------------------------|-----------------------------------------------------|
| Backend                | Python 3.13.2, FastAPI                              |
| Real-Time Communication| WebSockets (~90 concurrent connections), APIs       |
| Database               | SQLite                                              |
| Caching                | Redis                                               |
| Frontend               | HTML, CSS, JavaScript                               |
| Charts & Visualization | Client-side interactive trading charts              |
| Hosting & Deployment   | AWS EC2 (Amazon Linux 2023) with Nginx & HTTPS      |
| CI/CD                  | GitHub Actions                                      |
| Version Control        | Git                                                  |


## Software Requirements

To run the Crypto Trading Simulator locally or deploy it, the following are required:

- **Python 3.13.2** – Core backend runtime for FastAPI and async processing.
- **Redis** – Used for caching and improving real-time WebSocket performance.
- **SQLite** – Lightweight database for storing portfolio and transaction data.
- **Git** – For source control and project management.
- **Modern Web Browser** – To access the dashboard, trading terminal, and portfolio views.
- **AWS Account (optional)** – Required only if you want to deploy the application to the cloud

  
## Hardware Requirements

To run the Crypto Trading Simulator smoothly, the following minimum hardware is recommended:

- **Processor:** Intel i3 / AMD Ryzen 3 or higher  
- **RAM:** 4 GB minimum (8 GB recommended for optimal performance)  
- **Storage:** 2 GB free space (to accommodate Python, Redis, and SQLite)  
- **Internet Connection:** Stable connection for real-time price updates and WebSocket streaming  
- **Browser:** Latest version of Safari, Chrome, Firefox, or Edge

  
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
│   ├── __init__.py
│   ├── config.py                # Configuration settings
│   ├── constants/               # Constant values like coin data
│   │   └── coin.py
│   ├── database/                # Database setup and session management
│   │   ├── db.py
│   │   ├── init_db.py
│   │   └── session.py
│   ├── main.py                  # FastAPI entry point
│   ├── models/                  # Pydantic/SQLAlchemy models
│   │   ├── __init__.py
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
│   │   ├── __init__.py
│   │   └── scheduler.py
│   └── utils/                   # Helper utilities
│       ├── cache.py
│       └── redis_client.py
│
├── app.db                        # SQLite database file
├── deploy/                       # Deployment scripts/configs
│   ├── fastapi_nginx.conf
│   └── setup_nginx.sh
├── docker-compose.yml
├── Dockerfile
├── docs/                         # Documentation
│   ├── api_docs.md
│   └── setup_guide.md
├── insert_crypto.py               # Script to seed crypto data
├── LICENSE
├── README.md
├── requirements.txt
├── static/                        # Frontend assets
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
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


