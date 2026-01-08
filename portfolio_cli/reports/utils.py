"""Utilities for portfolio reports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import yfinance as yf

PRICES_JSON_PATH = Path("data/prices.json")


@dataclass
class Holding:
    """A single portfolio holding."""

    symbol: str
    quantity: float
    cost_basis: float  # pricePerShare (avg cost)
    total_cost: float  # totalPrice
    current_price: float
    current_value: float
    allocation: float  # currentAllocation
    total_return_pct: float  # totalPercentChange


def load_holdings(path: Path = PRICES_JSON_PATH) -> List[Holding]:
    """Load holdings from prices.json."""
    with open(path) as f:
        data = json.load(f)

    holdings = []
    for h in data.get("holdings", []):
        # Skip non-stock holdings
        if h.get("holdingType") != "stock":
            continue

        # Parse current price (may be string)
        current_price = h.get("currentPricePerShare", 0)
        if isinstance(current_price, str):
            current_price = float(current_price)

        holdings.append(
            Holding(
                symbol=h["symbol"],
                quantity=h.get("quantity", 0),
                cost_basis=h.get("pricePerShare", 0),
                total_cost=h.get("totalPrice", 0),
                current_price=current_price,
                current_value=h.get("currentTotalPrice", 0),
                allocation=h.get("currentAllocation", 0),
                total_return_pct=h.get("totalPercentChange", 0),
            )
        )

    return holdings


def get_period_start_date(period: str, reference_date: Optional[date] = None) -> date:
    """
    Calculate the start date for a given period.

    Args:
        period: One of '3mo', 'ytd', '1y'
        reference_date: Reference date (defaults to today)

    Returns:
        Start date for the period
    """
    ref = reference_date or date.today()

    if period == "3mo":
        # ~3 months ago
        return ref - timedelta(days=90)
    elif period == "ytd":
        # First day of current year
        return date(ref.year, 1, 1)
    elif period == "1y":
        # ~1 year ago
        return ref - timedelta(days=365)
    else:
        raise ValueError(f"Unknown period: {period}. Use '3mo', 'ytd', or '1y'.")


def _normalize_symbol(symbol: str) -> str:
    """Normalize symbol for yfinance compatibility."""
    # BRK.B -> BRK-B (yfinance uses hyphens)
    return symbol.replace(".", "-")


def _denormalize_symbol(symbol: str) -> str:
    """Convert yfinance symbol back to portfolio format."""
    return symbol.replace("-", ".")


def fetch_historical_prices(
    symbols: List[str],
    start_date: date,
    end_date: Optional[date] = None,
) -> Dict[str, float]:
    """
    Fetch historical closing prices for symbols at a specific date.

    Returns a dict mapping symbol -> closing price at start_date.
    Uses the first available trading day on or after start_date.
    """
    # Fetch a small window to find the first available price
    # If the stock didn't exist at the start of the period, it will be skipped
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = (start_date + timedelta(days=10)).strftime("%Y-%m-%d")

    prices: Dict[str, float] = {}

    # Normalize symbols for yfinance
    symbol_map = {_normalize_symbol(s): s for s in symbols}
    yf_symbols = list(symbol_map.keys())

    # Batch download for efficiency
    tickers_str = " ".join(yf_symbols)
    try:
        data = yf.download(
            tickers_str,
            start=start_str,
            end=end_str,
            progress=False,
            auto_adjust=True,
        )

        if data.empty:
            return prices

        # Handle single vs multiple tickers
        if len(yf_symbols) == 1:
            # Single ticker: data is a simple DataFrame
            if not data.empty:
                first_close = data["Close"].iloc[0]
                orig_symbol = symbol_map[yf_symbols[0]]
                prices[orig_symbol] = float(first_close)
        else:
            # Multiple tickers: data has multi-level columns
            close_data = data["Close"]
            for yf_sym, orig_sym in symbol_map.items():
                if yf_sym in close_data.columns:
                    series = close_data[yf_sym].dropna()
                    if not series.empty:
                        prices[orig_sym] = float(series.iloc[0])

    except Exception as e:
        # Log but don't fail; individual symbols may still work
        print(f"Warning: Error fetching prices: {e}")

    return prices


def fetch_current_prices(symbols: List[str]) -> Dict[str, float]:
    """
    Fetch current prices for symbols.

    Returns a dict mapping symbol -> current price.
    """
    prices: Dict[str, float] = {}

    # Normalize symbols for yfinance
    symbol_map = {_normalize_symbol(s): s for s in symbols}
    yf_symbols = list(symbol_map.keys())

    tickers_str = " ".join(yf_symbols)
    try:
        data = yf.download(
            tickers_str,
            period="1d",
            progress=False,
            auto_adjust=True,
        )

        if data.empty:
            return prices

        if len(yf_symbols) == 1:
            if not data.empty:
                orig_symbol = symbol_map[yf_symbols[0]]
                prices[orig_symbol] = float(data["Close"].iloc[-1])
        else:
            close_data = data["Close"]
            for yf_sym, orig_sym in symbol_map.items():
                if yf_sym in close_data.columns:
                    series = close_data[yf_sym].dropna()
                    if not series.empty:
                        prices[orig_sym] = float(series.iloc[-1])

    except Exception as e:
        print(f"Warning: Error fetching current prices: {e}")

    return prices

