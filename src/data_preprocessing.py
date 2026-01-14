"""
Data cleaning and preprocessing functions
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config.config import *

class DataPreprocessor:
    
    def __init__(self):
        print("🔧 DataPreprocessor initialized")
    
    def load_raw_data(self, data_type='enrolment'):
        """
        Load raw data from CSV files
        
        Args:
            data_type: 'enrolment', 'demographic', or 'biometric'
        """
        print(f"\n📂 Loading {data_type} data...")
        
        try:
            if data_type == 'enrolment':
                files = list(RAW_DATA_DIR.glob('**/*enrolment*.csv'))
            elif data_type == 'demographic':
                files = list(RAW_DATA_DIR.glob('**/*demographic*.csv'))
            elif data_type == 'biometric':
                files = list(RAW_DATA_DIR.glob('**/*biometric*.csv'))
            else:
                raise ValueError(f"Invalid data_type: {data_type}")
            
            if not files:
                print(f"❌ No {data_type} files found in {RAW_DATA_DIR}")
                return None
            
            # Load all CSV files and combine
            dfs = []
            for file in files:
                print(f"   Loading: {file.name}")
                df = pd.read_csv(file)
                dfs.append(df)
            
            combined_df = pd.concat(dfs, ignore_index=True)
            print(f"✅ Loaded {len(combined_df):,} rows, {len(combined_df.columns)} columns")
            
            return combined_df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def explore_data(self, df):
        """Quick data exploration"""
        print("\n📊 Data Exploration:")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        print(f"\n   Data types:\n{df.dtypes}")
        print(f"\n   Missing values:\n{df.isnull().sum()}")
        print(f"\n   First few rows:\n{df.head()}")
        return df.info()
    
    def clean_data(self, df):
        """
        Clean and validate data
        """
        print("\n🧹 Cleaning data...")
        original_rows = len(df)
        
        # Make a copy
        df_clean = df.copy()
        
        # 1. Handle dates (if date column exists)
        date_columns = [col for col in df_clean.columns if 'date' in col.lower()]
        for col in date_columns:
            print(f"   Converting {col} to datetime...")
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
        
        # 2. Clean pincode (if exists)
        if 'pincode' in df_clean.columns or 'Pincode' in df_clean.columns:
            pincode_col = 'pincode' if 'pincode' in df_clean.columns else 'Pincode'
            print(f"   Standardizing {pincode_col}...")
            df_clean[pincode_col] = df_clean[pincode_col].astype(str).str.zfill(6)
            # Remove invalid pincodes
            df_clean = df_clean[df_clean[pincode_col].str.len() == 6]
        
        # 3. Validate age (if exists)
        age_columns = [col for col in df_clean.columns if 'age' in col.lower()]
        for col in age_columns:
            if df_clean[col].dtype in ['int64', 'float64']:
                print(f"   Validating {col}...")
                df_clean = df_clean[(df_clean[col] >= AGE_MIN) & (df_clean[col] <= AGE_MAX)]
        
        # 4. Remove duplicates
        duplicates = df_clean.duplicated().sum()
        if duplicates > 0:
            print(f"   Removing {duplicates} duplicates...")
            df_clean = df_clean.drop_duplicates()
        
        # 5. Handle missing values in critical columns
        critical_cols = ['State', 'District', 'Pincode']
        existing_critical = [col for col in critical_cols if col in df_clean.columns]
        
        if existing_critical:
            before = len(df_clean)
            df_clean = df_clean.dropna(subset=existing_critical)
            dropped = before - len(df_clean)
            if dropped > 0:
                print(f"   Dropped {dropped} rows with missing critical values")
        
        # Summary
        final_rows = len(df_clean)
        retained_pct = (final_rows / original_rows) * 100
        
        print(f"\n✅ Cleaning complete:")
        print(f"   Original rows: {original_rows:,}")
        print(f"   Final rows: {final_rows:,}")
        print(f"   Retained: {retained_pct:.2f}%")
        
        return df_clean
    
    def feature_engineering(self, df):
        """Create additional features"""
        print("\n🔨 Feature engineering...")
        
        df_featured = df.copy()
        
        # Extract time features if date exists
        date_columns = [col for col in df_featured.columns if 'date' in col.lower()]
        for col in date_columns:
            if pd.api.types.is_datetime64_any_dtype(df_featured[col]):
                df_featured['year'] = df_featured[col].dt.year
                df_featured['month'] = df_featured[col].dt.month
                df_featured['quarter'] = df_featured[col].dt.quarter
                df_featured['day_of_week'] = df_featured[col].dt.dayofweek
                print(f"   Extracted time features from {col}")
        
        print(f"✅ Feature engineering complete")
        return df_featured
    
    def save_processed_data(self, df, filename):
        """Save processed data"""
        filepath = PROCESSED_DATA_DIR / filename
        df.to_csv(filepath, index=False)
        print(f"✅ Saved processed data to: {filepath}")
        return filepath

# Process all datasets
if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    
    # Define datasets to process
    datasets = [
        ('enrolment', 'cleaned_enrolment.csv'),
        ('demographic', 'cleaned_demographic.csv'),
        ('biometric', 'cleaned_biometric.csv')
    ]
    
    for data_type, output_file in datasets:
        print(f"\n{'='*60}")
        print(f"Processing {data_type.upper()} data")
        print(f"{'='*60}")
        
        df = preprocessor.load_raw_data(data_type)
        
        if df is not None:
            preprocessor.explore_data(df)
            df_clean = preprocessor.clean_data(df)
            df_final = preprocessor.feature_engineering(df_clean)
            preprocessor.save_processed_data(df_final, output_file)
        else:
            print(f"⚠️ Skipping {data_type} - no data found")
    
    print(f"\n{'='*60}")
    print("✅ All datasets processed!")
    print(f"{'='*60}")
