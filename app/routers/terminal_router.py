# app/routers/terminal_router.py

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["Trading Terminal"])

@router.get("/tradingterminal", name="trading_terminal_page")
def trading_terminal_page(
    request: Request,
    symbol: str | None = None  # optional symbol
):
    """
    Render the trading terminal page.
    Live prices are fetched by frontend JS via Redis-cached API calls.
    """
    symbol = symbol.upper() if symbol else "BTC"
    return templates.TemplateResponse(
        "tradingterminal.html",
        {"request": request, "symbol": symbol}
    )