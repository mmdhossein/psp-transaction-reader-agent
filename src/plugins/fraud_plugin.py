import pandas as pd
import json
from semantic_kernel.functions import kernel_function
from utils.csv_loader import CSVLoader

class FraudPlugin:
    def __init__(self, loader: CSVLoader):
        self.loader = loader
    
    @property
    def df(self):
        return self.loader.df
    
    @kernel_function(
        name="detect_suspicious_patterns",
        description="Identify potentially fraudulent transaction patterns"
    )
    def detect_suspicious_patterns(self) -> str:
        """Flag suspicious activity"""
        if self.df is None:
            return "No data loaded"
        
        suspicious = []
        
        # High velocity: same customer multiple transactions in short time
        if 'customer_id' in self.df.columns:
            self.df['created_at_dt'] = pd.to_datetime(self.df['created_at'])
            customer_velocity = self.df.groupby('customer_id').apply(
                lambda x: len(x[x['created_at_dt'] > (x['created_at_dt'].max() - pd.Timedelta(hours=1))])
            )
            high_velocity = customer_velocity[customer_velocity > 5].index.tolist()
            
            if high_velocity:
                suspicious.append({
                    'type': 'high_velocity',
                    'description': 'Multiple transactions in 1 hour',
                    'customer_ids': high_velocity[:10]
                })
        
        # Large amounts
        if 'amount' in self.df.columns:
            threshold = self.df['amount'].quantile(0.99)
            large_txns = self.df[self.df['amount'] > threshold]
            
            if len(large_txns) > 0:
                suspicious.append({
                    'type': 'large_amount',
                    'description': f'Transactions above ${threshold:.2f}',
                    'count': int(len(large_txns)),
                    'total_volume': round(float(large_txns['amount'].sum()), 2)
                })
        
        # Failed then successful pattern
        if 'customer_id' in self.df.columns:
            customer_pattern = self.df.groupby('customer_id')['status'].apply(list)
            risky_pattern = customer_pattern.apply(
                lambda x: 'failed' in x[:3] and 'completed' in x[3:]
            )
            risky_customers = risky_pattern[risky_pattern].index.tolist()
            
            if risky_customers:
                suspicious.append({
                    'type': 'failed_then_success',
                    'description': 'Failed attempts followed by success',
                    'customer_ids': risky_customers[:10]
                })
        
        return json.dumps({
            'total_flags': len(suspicious),
            'patterns': suspicious
        }, ensure_ascii=False)
    
    @kernel_function(
        name="get_chargeback_analysis",
        description="Analyze chargeback transactions"
    )
    def get_chargeback_analysis(self) -> str:
        """Chargeback metrics"""
        if self.df is None:
            return "No data loaded"
        
        chargebacks = self.df[self.df['status'] == 'chargeback']
        
        if len(chargebacks) == 0:
            return json.dumps({'message': 'No chargebacks found'}, ensure_ascii=False)
        
        analysis = {
            'total_chargebacks': int(len(chargebacks)),
            'chargeback_rate': round(len(chargebacks) / len(self.df) * 100, 2),
            'chargeback_volume': round(float(chargebacks['amount'].sum()), 2),
            'top_merchants': chargebacks['merchant_id'].value_counts().head(10).to_dict()
        }
        
        if 'payment_method' in chargebacks.columns:
            analysis['by_payment_method'] = chargebacks['payment_method'].value_counts().to_dict()
        
        return json.dumps(analysis, ensure_ascii=False)
