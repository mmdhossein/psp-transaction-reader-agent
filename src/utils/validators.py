"""Validation utilities for transaction data integrity."""
from datetime import datetime
from typing import Any, Optional

from src.models.enums import Currency, PaymentMethod, TransactionStatus


class ValidationError(Exception):
    """Raised when a transaction record fails validation."""
    pass


def validate_transaction_id(value: Any) -> str:
    if not value or not isinstance(value, str) or not value.strip():
        raise ValidationError("transaction_id must be a non-empty string.")
    return value.strip()


def validate_merchant_id(value: Any) -> str:
    if not value or not isinstance(value, str) or not value.strip():
        raise ValidationError("merchant_id must be a non-empty string.")
    return value.strip()


def validate_amount(value: Any) -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"amount '{value}' is not a valid number.")
    if amount < 0:
        raise ValidationError(f"amount cannot be negative: {amount}")
    if amount > 1_000_000_000:
        raise ValidationError(f"amount '{amount}' exceeds sane upper bound; possible data error.")
    return round(amount, 2)


def validate_currency(value: Any) -> Currency:
    if isinstance(value, Currency):
        return value
    try:
        return Currency(str(value).strip().upper())
    except ValueError:
        raise ValidationError(f"Unsupported currency code: '{value}'")


def validate_status(value: Any) -> TransactionStatus:
    if isinstance(value, TransactionStatus):
        return value
    try:
        return TransactionStatus(str(value).strip().lower())
    except ValueError:
        raise ValidationError(f"Unsupported transaction status: '{value}'")


def validate_payment_method(value: Any) -> Optional[PaymentMethod]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, PaymentMethod):
        return value
    try:
        return PaymentMethod(str(value).strip().lower())
    except ValueError:
        raise ValidationError(f"Unsupported payment method: '{value}'")


def validate_created_at(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%m/%d/%Y %H:%M:%S"):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
    # Fallback to pandas-style parsing if strict formats fail
    import pandas as pd
    try:
        parsed = pd.to_datetime(value)
        return parsed.to_pydatetime()
    except Exception:
        raise ValidationError(f"Unable to parse created_at value: '{value}'")


def validate_row(row: dict) -> dict:
    """Validate a full CSV row dict, returning cleaned/typed values or raising ValidationError."""
    return {
        "transaction_id": validate_transaction_id(row.get("transaction_id")),
        "merchant_id": validate_merchant_id(row.get("merchant_id")),
        "amount": validate_amount(row.get("amount")),
        "currency": validate_currency(row.get("currency")),
        "status": validate_status(row.get("status")),
        "created_at": validate_created_at(row.get("created_at")),
        "payment_method": validate_payment_method(row.get("payment_method")),
    }
