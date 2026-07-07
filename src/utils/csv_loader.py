import pandas as pd
from typing import Optional
from pathlib import Path

class CSVLoader:
    REQUIRED_COLUMNS = [
        'transaction_id', 'merchant_id', 'amount', 
        'currency', 'status', 'created_at'
    ]
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.file_loaded = False
        self.validation_errors = []
    
    def load(self, file_path: str) -> bool:
        """Load and validate CSV file"""
        try:
            path = Path(file_path)
            if path.suffix.lower() == '.csv':
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            
            if not self._validate_columns():
                return False
            
            self._clean_data()
            self.file_loaded = True
            return True
            
        except Exception as e:
            self.validation_errors.append(f"Load error: {str(e)}")
            return False
    
    def _validate_columns(self) -> bool:
        """Check required columns exist"""
        missing = set(self.REQUIRED_COLUMNS) - set(self.df.columns)
        if missing:
            self.validation_errors.append(f"Missing columns: {missing}")
            return False
        return True
    
    def _clean_data(self):
        """Clean and normalize data"""
        # Convert dates
        date_columns = ['created_at', 'completed_at']
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
        # Convert amounts to float
        amount_columns = ['amount', 'fee', 'net_amount']
        for col in amount_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Normalize status values
        if 'status' in self.df.columns:
            self.df['status'] = self.df['status'].str.lower().str.strip()
    
    def get_info(self) -> dict:
        """Get dataset summary"""
        if self.df is None:
            return {}
        
        return {
            'total_rows': len(self.df),
            'columns': self.df.columns.tolist(),
            'date_range': {
                'start': str(self.df['created_at'].min()),
                'end': str(self.df['created_at'].max())
            },
            'status_distribution': self.df['status'].value_counts().to_dict(),
            'total_amount': float(self.df['amount'].sum()),
            'currencies': self.df['currency'].unique().tolist()
        }
