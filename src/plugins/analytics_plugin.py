import pandas as pd
import json
from semantic_kernel.functions import kernel_function
from utils.csv_loader import CSVLoader

class AnalyticsPlugin:
    def __init__(self, loader: CSVLoader):
        self.loader = loader
    
    @property
    def df(self):
        return self.loader.df
    
    @kernel_function(
        name="get_daily_trends",
        description="Get daily transaction trends for time series analysis"
    )
    def get_daily_trends(self) -> str:
        """Calculate daily metrics"""
        if self.df is None:
            return "No data loaded"
        
        self.df['date'] = pd.to_datetime(self.df['created_at']).dt.date
        
        daily = self.df.groupby('date').agg({
            'transaction_id': 'count',
            'amount': 'sum',
            'status': lambda x: (x == 'completed').sum()
        }).reset_index()
        
        daily.columns = ['date', 'count', 'volume', 'successful']
        daily['success_rate'] = (daily['successful'] / daily['count'] * 100).round(2)
        daily['date'] = daily['date'].astype(str)
        
        return json.dumps(daily.to_dict('records'), ensure_ascii=False)
    
    @kernel_function(
        name="get_currency_breakdown",
        description="Analyze transactions by currency"
    )
    def get_currency_breakdown(self) -> str:
        """Group by currency"""
        if self.df is None:
            return "No data loaded"
        
        currency_stats = self.df.groupby('currency').agg({
            'transaction_id': 'count',
            'amount': 'sum'
        }).reset_index()
        
        currency_stats.columns = ['currency', 'count', 'volume']
        currency_stats['percentage'] = (
            currency_stats['count'] / currency_stats['count'].sum() * 100
        ).round(2)
        
        return json.dumps(currency_stats.to_dict('records'), ensure_ascii=False)
    
    @kernel_function(
        name="get_geographic_distribution",
        description="Analyze transactions by country"
    )
    def get_geographic_distribution(self) -> str:
        """Geographic breakdown"""
        if self.df is None or 'country' not in self.df.columns:
            return "Country data not available"
        
        geo = self.df.groupby('country').agg({
            'transaction_id': 'count',
            'amount': 'sum',
            'status': lambda x: (x == 'completed').sum()
        }).reset_index()
        
        geo.columns = ['country', 'count', 'volume', 'successful']
        geo['success_rate'] = (geo['successful'] / geo['count'] * 100).round(2)
        geo = geo.sort_values('volume', ascending=False)
        
        return json.dumps(geo.head(30).to_dict('records'), ensure_ascii=False)
    
    @kernel_function(
        name="get_hourly_pattern",
        description="Analyze transaction patterns by hour of day"
    )
    def get_hourly_pattern(self) -> str:
        """Hour of day analysis"""
        if self.df is None:
            return "No data loaded"
        
        self.df['hour'] = pd.to_datetime(self.df['created_at']).dt.hour
        
        hourly = self.df.groupby('hour').agg({
            'transaction_id': 'count',
            'amount': 'sum'
        }).reset_index()
        
        hourly.columns = ['hour', 'count', 'volume']
        hourly['avg_transaction'] = (hourly['volume'] / hourly['count']).round(2)
        
        return json.dumps(hourly.to_dict('records'), ensure_ascii=False)
    
    @kernel_function(
        name="get_cohort_analysis",
        description="Analyze customer cohorts by first transaction date"
    )
    def get_cohort_analysis(self) -> str:
        """Customer cohort metrics"""
        if self.df is None or 'customer_id' not in self.df.columns:
            return "Customer data not available"
        
        # Get first transaction per customer
        first_txn = self.df.groupby('customer_id')['created_at'].min().reset_index()
        first_txn['cohort'] = pd.to_datetime(first_txn['created_at']).dt.to_period('M')
        
        # Merge back
        df_with_cohort = self.df.merge(first_txn[['customer_id', 'cohort']], on='customer_id')
        
        cohort_stats = df_with_cohort.groupby('cohort').agg({
            'customer_id': 'nunique',
            'transaction_id': 'count',
            'amount': 'sum'
        }).reset_index()
        
        cohort_stats.columns = ['cohort', 'customers', 'transactions', 'volume']
        cohort_stats['cohort'] = cohort_stats['cohort'].astype(str)
        cohort_stats['avg_per_customer'] = (cohort_stats['volume'] / cohort_stats['customers']).round(2)
        
        return json.dumps(cohort_stats.to_dict('records'), ensure_ascii=False)
