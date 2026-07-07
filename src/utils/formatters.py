"""Formatting utilities for currency, dates, and report output."""
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Union

from src.models.enums import Currency


CURRENCY_SYMBOLS = {
    Currency.USD: "$",
    Currency.EUR: "€",
    Currency.GBP: "£",
    Currency.IRR: "﷼",
    Currency.AED: "د.إ",
}


def format_amount(amount: Union[float, Decimal], currency: Currency = Currency.USD) -> str:
    """Format a numeric amount with currency symbol and thousands separators."""
    dec_amount = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    symbol = CURRENCY_SYMBOLS.get(currency, "")
    return f"{symbol}{dec_amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a ratio (0.0 - 1.0) as a percentage string."""
    return f"{value * 100:.{decimals}f}%"


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object consistently across reports."""
    return dt.strftime(fmt)


def format_large_number(value: Union[int, float]) -> str:
    """Convert large numbers to human-readable form (e.g. 1.2K, 3.4M)."""
    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def truncate_id(identifier: str, length: int = 8) -> str:
    """Truncate long IDs for display (e.g. in chat responses/tables)."""
    if len(identifier) <= length:
        return identifier
    return f"{identifier[:length]}…"


def dataframe_to_markdown_table(df, max_rows: int = 20) -> str:
    """Convert a pandas DataFrame to a markdown table string, truncated for chat display."""
    if df.empty:
        return "_No data available._"
    truncated = df.head(max_rows)
    md = truncated.to_markdown(index=False)
    if len(df) > max_rows:
        md += f"\n\n*Showing {max_rows} of {len(df)} rows.*"
    return md
