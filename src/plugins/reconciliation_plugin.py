"""Reconciliation plugin: settlement matching, discrepancy detection, gross/net reporting."""
import json
from typing import Annotated, Optional

import pandas as pd
from semantic_kernel.functions import kernel_function

from src.models.enums import TransactionStatus
from src.utils.formatters import format_amount, format_percentage


class ReconciliationPlugin:
    """Semantic Kernel plugin for reconciling PSP transaction data."""

    def __init__(self):
        self.transactions = []
        self.df = pd.DataFrame()

    def set_transactions(self, transactions: list, df: pd.DataFrame):
        self.transactions = transactions
        self.df = df

    def _check_data(self) -> Optional[str]:
        if self.df.empty:
            return json.dumps({"error": "No transaction data loaded. Please upload a CSV first."})
        return None

    @kernel_function(
        name="reconcile_totals",
        description="Reconcile gross volume vs net settled volume per merchant, accounting for fees/refunds if present.",
    )
    def reconcile_totals(
        self,
        merchant_id: Annotated[Optional[str], "Optional merchant ID to filter results"] = None,
    ) -> Annotated[str, "JSON reconciliation report per merchant"]:
        err = self._check_data()
        if err:
            return err

        df = self.df.copy()
        if merchant_id:
            df = df[df["merchant_id"] == merchant_id]
            if df.empty:
                return json.dumps({"error": f"No transactions found for merchant_id '{merchant_id}'"})

        results = []
        for mid, group in df.groupby("merchant_id"):
            gross = group["amount"].sum()
            settled = group[group["status"] == TransactionStatus.SUCCESS.value]["amount"].sum()
            refunded = group[group["status"] == TransactionStatus.REFUNDED.value]["amount"].sum() \
                if "refunded" in group["status"].values else 0.0
            failed = group[group["status"] == TransactionStatus.FAILED.value]["amount"].sum()
            net = settled - refunded

            results.append({
                "merchant_id": mid,
                "gross_volume": format_amount(gross),
                "settled_volume": format_amount(settled),
                "refunded_volume": format_amount(refunded),
                "failed_volume": format_amount(failed),
                "net_volume": format_amount(net),
                "transaction_count": int(len(group)),
            })

        return json.dumps({"reconciliation": results}, indent=2)

    @kernel_function(
        name="find_discrepancies",
        description="Detect transactions with inconsistent or suspicious status transitions relevant to settlement (e.g. duplicate transaction_ids, refunds exceeding original amount).",
    )
    def find_discrepancies(self) -> Annotated[str, "JSON list of discrepancies found"]:
        err = self._check_data()
        if err:
            return err

        df = self.df
        discrepancies = []

        # Duplicate transaction IDs — should be unique
        dup_ids = df[df.duplicated(subset=["transaction_id"], keep=False)]
        if not dup_ids.empty:
            for txn_id, group in dup_ids.groupby("transaction_id"):
                discrepancies.append({
                    "type": "duplicate_transaction_id",
                    "transaction_id": txn_id,
                    "occurrences": int(len(group)),
                    "statuses": group["status"].tolist(),
                })

        # Refunds larger than a sane merchant single-transaction ceiling (heuristic: > mean + 3*std)
        if "refunded" in df["status"].values:
            refunds = df[df["status"] == TransactionStatus.REFUNDED.value]
            if not refunds.empty:
                mean, std = refunds["amount"].mean(), refunds["amount"].std(ddof=0)
                threshold = mean + 3 * std if std and not pd.isna(std) else mean * 3
                outliers = refunds[refunds["amount"] > threshold]
                for _, row in outliers.iterrows():
                    discrepancies.append({
                        "type": "abnormal_refund_amount",
                        "transaction_id": row["transaction_id"],
                        "merchant_id": row["merchant_id"],
                        "amount": format_amount(row["amount"]),
                    })

        return json.dumps({
            "discrepancy_count": len(discrepancies),
            "discrepancies": discrepancies,
        }, indent=2)

    @kernel_function(
        name="settlement_summary",
        description="Provide an overall settlement summary across all merchants: totals, success rate, and pending exposure.",
    )
    def settlement_summary(self) -> Annotated[str, "JSON overall settlement summary"]:
        err = self._check_data()
        if err:
            return err

        df = self.df
        total = df["amount"].sum()
        success = df[df["status"] == TransactionStatus.SUCCESS.value]["amount"].sum()
        pending = df[df["status"] == TransactionStatus.PENDING.value]["amount"].sum() \
            if "pending" in df["status"].values else 0.0
        failed = df[df["status"] == TransactionStatus.FAILED.value]["amount"].sum()

        success_rate = len(df[df["status"] == TransactionStatus.SUCCESS.value]) / len(df) if len(df) else 0

        summary = {
            "total_volume": format_amount(total),
            "settled_volume": format_amount(success),
            "pending_exposure": format_amount(pending),
            "failed_volume": format_amount(failed),
            "success_rate": format_percentage(success_rate),
            "total_transactions": int(len(df)),
            "unique_merchants": int(df["merchant_id"].nunique()),
        }
        return json.dumps(summary, indent=2)
