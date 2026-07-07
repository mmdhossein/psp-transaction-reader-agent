from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal

@dataclass
class Transaction:
    transaction_id: str
    merchant_id: str
    customer_id: Optional[str]
    amount: Decimal
    currency: str
    status: str
    payment_method: str
    transaction_type: str
    created_at: datetime
    completed_at: Optional[datetime]
    fee: Decimal
    net_amount: Decimal
    card_last4: Optional[str]
    country: Optional[str]
    description: Optional[str]
    metadata: Optional[dict]
    
    @property
    def is_successful(self) -> bool:
        return self.status == "completed"
    
    @property
    def is_refunded(self) -> bool:
        return self.status == "refunded"
