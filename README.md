'''
stock-simulator/
│
├── app/                                # Main FastAPI application code
│   ├── main.py                         # FastAPI entry point, includes app initialization and router registration
│
│   ├── models/                         # SQLAlchemy ORM models for database tables
│   │   ├── user.py                     # User model with fields like id, email, password, etc.
│   │   ├── stock.py                    # Stock model with symbol, name, latest price, sector, etc.
│   │   ├── transaction.py              # Model for buy/sell transactions with timestamps and details
│   │   └── portfolio.py                # Model to track user's stock holdings and portfolio metrics
│
│   ├── schemas/                        # Pydantic schemas for request validation and response formatting
│   │   ├── user_schema.py              # User input/output models (e.g., LoginRequest, UserOut)
│   │   ├── stock_schema.py             # Schema for stock-related operations
│   │   └── transaction_schema.py       # Schema for transaction requests/responses
│
│   ├── routers/                        # API route handlers grouped by functionality
│   │   ├── auth_router.py              # Handles registration, login, Gmail OAuth, guest sessions
│   │   ├── stock_router.py             # CRUD endpoints for stock data, search, watchlist, etc.
│   │   ├── transaction_router.py       # Buy/sell actions, filters, history endpoints
│   │   └── portfolio_router.py         # Endpoints for portfolio view, summary, profit/loss
│
│   ├── services/                       # Business logic and third-party API integrations
│   │   ├── stock_data.py               # Fetches stock data using yfinance or Alpha Vantage
│   │   ├── tax_calculator.py           # Computes tax simulations based on profits
│   │   ├── report_generator.py         # Generates PDF or CSV portfolio/transaction reports
│   │   └── notification.py             # Prepares daily summaries or optional email alerts
│
│   ├── database/                       # Database engine setup and session utilities
│   │   ├── db.py                       # Connects SQLAlchemy to SQLite and initializes engine
│   │   └── session.py                  # Creates session dependency for route access
│
│   ├── utils/                          # Utility modules for caching, rate limiting, email, etc.
│   │   ├── cache.py                    # Caching logic using in-memory or file-based store
│   │   ├── limiter.py                  # API rate limiting setup using slowapi
│   │   └── email_utils.py              # Sends emails via SMTP or other API (optional)
│
│   ├── auth/                           # Auth-related logic
│   │   ├── oauth.py                    # Gmail OAuth integration using Authlib or FastAPI-users
│   │   └── guest.py                    # Guest session handling with Starlette sessions
│
│   ├── tasks/                          # Background jobs and schedulers
│   │   ├── scheduler.py                # APScheduler config for running daily tasks
│   │   └── tasks.py                    # Background tasks like sending daily summary or cleanups
│
│   └── templates/                      # Jinja2 templates for reports or server-rendered HTML
│       └── report_template.html        # Template used for generating printable reports
│
├── static/                             # Static files served by FastAPI (HTML, CSS, JS, images)
│   ├── css/                            # CSS files including Tailwind build
│   ├── js/                             # JavaScript files (if any frontend logic)
│   ├── images/                         # App logos, stock icons, etc.
│   └── index.html                      # Main frontend file (if single-page app)
│
├── tests/                              # Test cases for core functionalities
│   ├── test_stocks.py                  # Unit and API tests for stock endpoints
│   ├── test_transactions.py            # Tests for buy/sell logic, validation
│   └── test_auth.py                    # Tests for login, guest session, Gmail OAuth
│
├── docs/                               # Optional documentation folder
│   ├── api_docs.md                     # API contract with endpoints and sample payloads
│   └── setup_guide.md                  # Project setup, run instructions, developer notes
│
├── .env                                # Environment variables file (API keys, secrets, DB URL)
├── .gitignore                          # Files/folders to ignore in version control
├── Dockerfile                          # Docker build configuration for backend container
├── docker-compose.yml                  # Optional: DB, app, and other service orchestration
├── requirements.txt                    # List of Python dependencies
├── README.md                           # Project overview, setup steps, and feature list
├── alembic.ini                         # Alembic migration configuration
└── alembic/                            # Alembic-generated DB migration scripts
'''