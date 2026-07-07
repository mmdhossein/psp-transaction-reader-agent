from enum import Enum

class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CHARGEBACK = "chargeback"
    CANCELLED = "cancelled"

class PaymentMethod(Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    CRYPTO = "crypto"

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    IRR = "IRR"

class TransactionType(Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    PAYOUT = "payout"
    FEE = "fee"
