import pandas as pd
import json
from semantic_kernel.functions import kernel_function
from utils.csv_loader import CSVLoader

class TransactionPlugin:
    def __init__(self, loader: CSVLoader):
        self.loader = loader
    
    @property
    def df(self):
        return self.loader.df
    
    @kernel_function(
        name="get_transaction_summary",
        description="Get overall transaction summary including total volume, count, success rate"
    )
    def get_transaction_summary(self) -> str:
        """Calculate key transaction metrics"""
        if self.df is None:
            return "No data loaded"
        
        total_count = len(self.df)
        successful = len(self.df[self.df['status'] == 'completed'])
        total_volume = self.df[self.df['status'] == 'completed']['amount'].sum()
        total_fees = self.df['fee'].sum() if 'fee' in self.df.columns else 0
        
        summary = {
            'total_transactions': int(total_count),
            'successful_transactions': int(successful),
            'success_rate': round(successful / total_count * 100, 2),
            'total_volume': round(float(total_volume), 2),
            'total_fees': round(float(total_fees), 2),
            'net_revenue': round(float(total_volume - total_fees), 2)
        }
        
        return json.dumps(summary, ensure_ascii=False)
    
    @kernel_function(
        name="get_status_breakdown",
        description="Get transaction count and volume by status"
    )
    def get_status_breakdown(self) -> str:
        """Break down transactions by status"""
        if self.df is None:
            return "No data loaded"
        
        breakdown = {}
        for status in self.df['status'].unique():
            status_df = self.df[self.df['status'] == status]
            breakdown[status] = {
                'count': int(len(status_df)),
                'volume': round(float(status_df['amount'].sum()), 2),
                'percentage': round(len(status_df) / len(self.df) * 100, 2)
            }
        
        return json.dumps(breakdown, ensure_ascii=False)
    
    @kernel_function(
        name="get_merchant_performance",
        description="Get transaction metrics grouped by merchant"
    )
    def get_merchant_performance(self) -> str:
        """Analyze performance by merchant"""
        if self.df is None:
            return "No data loaded"
        
        merchant_stats = self.df.groupby('merchant_id').agg({
            'transaction_id': 'count',
            'amount': 'sum',
            'fee': 'sum',
            'status': lambda x: (x == 'completed').sum()
        }).reset_index()
        
        merchant_stats.columns = ['merchant_id', 'total_txns', 'volume', 'fees', 'successful']
        merchant_stats['success_rate'] = (
            merchant_stats['successful'] / merchant_stats['total_txns'] * 100
        ).round(2)
        merchant_stats['net_revenue'] = merchant_stats['volume'] - merchant_stats['fees']
        
        result = merchant_stats.sort_values('volume', ascending=False).head(20).to_dict('records')
        return json.dumps(result, ensure_ascii=False)
    
    @kernel_function(
        name="get_payment_method_stats",
        description="Get transaction distribution by payment method"
    )
    def get_payment_method_stats(self) -> str:
        """Analyze by payment method"""
        if self.df is None or 'payment_method' not in self.df.columns:
            return "Payment method data not available"
        
        stats = self.df.groupby('payment_method').agg({
            'transaction_id': 'count',
            'amount': 'sum',
            'status': lambda x: (x == 'completed').sum()
        }).reset_index()
        
        stats.columns = ['payment_method', 'count', 'volume', 'successful']
        stats['success_rate'] = (stats['successful'] / stats['count'] * 100).round(2)
        stats['avg_transaction'] = (stats['volume'] / stats['count']).round(2)
        
        return json.dumps(stats.to_dict('records'), ensure_ascii=False)
    
    @kernel_function(
        name="search_transaction",
        description="Search for specific transaction by ID or customer ID"
    )
    def search_transaction(self, search_term: str) -> str:
        """Find transaction by ID or customer"""
        if self.df is None:
            return "No data loaded"
        
        # Search in transaction_id
        result = self.df[self.df['transaction_id'].astype(str).str.contains(search_term, case=False, na=False)]
        
        # Also search in customer_id if exists
        if 'customer_id' in self.df.columns:
            customer_match = self.df[self.df['customer_id'].astype(str).str.contains(search_term, case=False, na=False)]
            result = pd.concat([result, customer_match]).drop_duplicates()
        
        if len(result) == 0:
            return json.dumps({'message': 'No transactions found'}, ensure_ascii=False)
        
        return json.dumps(result.head(10).to_dict('records'), ensure_ascii=False)
    
    @kernel_function(
        name="get_failed_transactions",
        description="Get all failed transactions with details"
    )
    def get_failed_transactions(self) -> str:
        """Retrieve failed transactions for investigation"""
        if self.df is None:
            return "No data loaded"
        
        failed = self.df[self.df['status'].isin(['failed', 'cancelled'])]
        
        summary = {
            'total_failed': int(len(failed)),
            'failed_volume': round(float(failed['amount'].sum()), 2),
            'transactions': failed.head(50).to_dict('records')
        }
        
        return json.dumps(summary, ensure_ascii=False)
    
    @kernel_function(
        name="get_refund_analysis",
        description="Analyze refunded transactions"
    )
    def get_refund_analysis(self) -> str:
        """Get refund metrics"""
        if self.df is None:
            return "No data loaded"
        
        refunded = self.df[self.df['status'] == 'refunded']
        
        analysis = {
            'total_refunds': int(len(refunded)),
            'refund_rate': round(len(refunded) / len(self.df) * 100, 2),
            'refunded_amount': round(float(refunded['amount'].sum()), 2),
            'top_merchants': refunded['merchant_id'].value_counts().head(10).to_dict()
        }
        
        return json.dumps(analysis, ensure_ascii=False)
