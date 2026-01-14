"""
Power BI Data Export Script
===========================

This script prepares data in a format optimized for Power BI.

WHY SPECIAL FORMATTING FOR POWER BI?
------------------------------------
Power BI works best when:
1. Data is in a "flat" table format (no nested structures)
2. Date columns are proper dates (not strings)
3. Column names are clean (no special characters)
4. Related tables have clear keys for relationships
5. Data types are consistent

This script creates several tables that can be imported into Power BI
and linked together using the "Model" view.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.config import PROCESSED_DATA_DIR, OUTPUT_DATA_DIR

# Create Power BI export directory
POWERBI_DIR = OUTPUT_DATA_DIR / 'powerbi_exports'
POWERBI_DIR.mkdir(parents=True, exist_ok=True)

print("📊 Power BI Data Export Script")
print("=" * 50)

# =============================================================================
# TABLE 1: FACT TABLE - All Transactions
# =============================================================================

def create_fact_table():
    """
    Create a unified fact table combining all datasets.
    
    WHAT IS A FACT TABLE?
    ---------------------
    In data modeling, a "fact table" contains the measurable data
    (numbers you want to analyze). It connects to "dimension tables"
    that contain descriptive attributes.
    
    Our fact table will have:
    - Date (when)
    - State, District, Pincode (where)
    - Data Type (enrolment/demographic/biometric)
    - Count values (what we're measuring)
    """
    print("\n📋 Creating Fact Table...")
    
    all_data = []
    
    for data_type in ['enrolment', 'demographic', 'biometric']:
        filepath = PROCESSED_DATA_DIR / f'cleaned_{data_type}.csv'
        if not filepath.exists():
            print(f"   ⚠️ Skipping {data_type} - file not found")
            continue
            
        df = pd.read_csv(filepath, parse_dates=['date'])
        
        # Identify age columns and standardize
        if data_type == 'enrolment':
            # Enrolment has 3 age groups
            df['children_0_5'] = df['age_0_5']
            df['youth_5_17'] = df['age_5_17']
            df['adults_18_plus'] = df['age_18_greater']
        elif data_type == 'demographic':
            df['children_0_5'] = 0  # Not tracked in demographic
            df['youth_5_17'] = df['demo_age_5_17']
            df['adults_18_plus'] = df['demo_age_17_']
        else:  # biometric
            df['children_0_5'] = 0  # Not tracked in biometric
            df['youth_5_17'] = df['bio_age_5_17']
            df['adults_18_plus'] = df['bio_age_17_']
        
        # Calculate total
        df['total_count'] = df['children_0_5'] + df['youth_5_17'] + df['adults_18_plus']
        
        # Add data type column
        df['data_type'] = data_type.title()
        
        # Select and rename columns for Power BI
        fact_df = df[[
            'date', 'state', 'district', 'pincode',
            'data_type', 'children_0_5', 'youth_5_17', 
            'adults_18_plus', 'total_count',
            'year', 'month', 'quarter', 'day_of_week'
        ]].copy()
        
        all_data.append(fact_df)
        print(f"   ✅ Added {len(fact_df):,} rows from {data_type}")
    
    # Combine all data
    fact_table = pd.concat(all_data, ignore_index=True)
    
    # Ensure date is in proper format for Power BI
    fact_table['date'] = pd.to_datetime(fact_table['date']).dt.strftime('%Y-%m-%d')
    
    # Clean state names (fix inconsistencies found in anomaly detection)
    fact_table['state'] = fact_table['state'].str.strip().str.title()
    
    # Export
    output_path = POWERBI_DIR / 'fact_aadhaar_transactions.csv'
    fact_table.to_csv(output_path, index=False)
    print(f"\n💾 Saved: {output_path}")
    print(f"   Total rows: {len(fact_table):,}")
    
    return fact_table

# =============================================================================
# TABLE 2: DIMENSION TABLE - States
# =============================================================================

def create_state_dimension():
    """
    Create a dimension table for states.
    
    WHAT IS A DIMENSION TABLE?
    --------------------------
    Dimension tables contain descriptive attributes that you use
    to filter and group your data. For states, we include:
    - State name
    - Region (North/South/East/West)
    - Zone (for further categorization)
    
    This allows Power BI users to filter by region!
    """
    print("\n🗺️ Creating State Dimension Table...")
    
    # Define state regions (simplified)
    state_regions = {
        'Andhra Pradesh': 'South', 'Telangana': 'South', 'Karnataka': 'South',
        'Tamil Nadu': 'South', 'Kerala': 'South', 'Puducherry': 'South',
        'Uttar Pradesh': 'North', 'Delhi': 'North', 'Haryana': 'North',
        'Punjab': 'North', 'Rajasthan': 'North', 'Himachal Pradesh': 'North',
        'Uttarakhand': 'North', 'Jammu And Kashmir': 'North', 'Ladakh': 'North',
        'Chandigarh': 'North',
        'Maharashtra': 'West', 'Gujarat': 'West', 'Goa': 'West',
        'Madhya Pradesh': 'Central', 'Chhattisgarh': 'Central',
        'West Bengal': 'East', 'Bihar': 'East', 'Jharkhand': 'East',
        'Odisha': 'East', 'Assam': 'Northeast', 'Meghalaya': 'Northeast',
        'Tripura': 'Northeast', 'Manipur': 'Northeast', 'Mizoram': 'Northeast',
        'Nagaland': 'Northeast', 'Arunachal Pradesh': 'Northeast', 'Sikkim': 'Northeast'
    }
    
    # Get unique states from fact table
    fact_path = POWERBI_DIR / 'fact_aadhaar_transactions.csv'
    if fact_path.exists():
        df = pd.read_csv(fact_path)
        states = df['state'].unique()
    else:
        states = list(state_regions.keys())
    
    # Create dimension table
    dim_state = pd.DataFrame({
        'state': states,
        'region': [state_regions.get(s, 'Other') for s in states]
    })
    
    # Add state code (first 2 letters)
    dim_state['state_code'] = dim_state['state'].str[:2].str.upper()
    
    # Export
    output_path = POWERBI_DIR / 'dim_states.csv'
    dim_state.to_csv(output_path, index=False)
    print(f"💾 Saved: {output_path}")
    print(f"   States: {len(dim_state)}")
    
    return dim_state

# =============================================================================
# TABLE 3: DIMENSION TABLE - Date
# =============================================================================

def create_date_dimension():
    """
    Create a date dimension table (calendar table).
    
    WHY A DATE TABLE?
    -----------------
    Power BI's time intelligence features (YoY growth, MTD, etc.)
    require a proper date table. This creates one with:
    - Full date
    - Year, Quarter, Month, Week, Day
    - Month name, Day name
    - Is Weekend flag
    """
    print("\n📅 Creating Date Dimension Table...")
    
    # Create date range covering our data (2025)
    dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='D')
    
    dim_date = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'year': dates.year,
        'quarter': dates.quarter,
        'month': dates.month,
        'month_name': dates.strftime('%B'),
        'month_short': dates.strftime('%b'),
        'week': dates.isocalendar().week,
        'day': dates.day,
        'day_name': dates.strftime('%A'),
        'day_short': dates.strftime('%a'),
        'day_of_week': dates.dayofweek,
        'is_weekend': dates.dayofweek >= 5,
        'year_month': dates.strftime('%Y-%m')
    })
    
    # Export
    output_path = POWERBI_DIR / 'dim_date.csv'
    dim_date.to_csv(output_path, index=False)
    print(f"💾 Saved: {output_path}")
    print(f"   Days: {len(dim_date)}")
    
    return dim_date

# =============================================================================
# TABLE 4: SUMMARY TABLE - State Aggregates
# =============================================================================

def create_state_summary():
    """
    Create pre-aggregated state summary for faster Power BI performance.
    
    WHY PRE-AGGREGATE?
    ------------------
    Power BI can aggregate on the fly, but for large datasets,
    pre-aggregated tables load faster. This is useful for:
    - Quick initial dashboard load
    - Card visuals showing totals
    """
    print("\n📊 Creating State Summary Table...")
    
    summaries = []
    
    for data_type in ['enrolment', 'demographic', 'biometric']:
        filepath = OUTPUT_DATA_DIR / f'state_summary_{data_type}.csv'
        if filepath.exists():
            df = pd.read_csv(filepath)
            df['data_type'] = data_type.title()
            # Keep only relevant columns
            if 'total' in df.columns:
                df = df[['state', 'total', 'data_type']].copy() if 'state' in df.columns else df[['total', 'data_type']].copy()
                summaries.append(df)
    
    if summaries:
        summary_table = pd.concat(summaries, ignore_index=True)
        output_path = POWERBI_DIR / 'summary_by_state.csv'
        summary_table.to_csv(output_path, index=False)
        print(f"💾 Saved: {output_path}")
    
    return summary_table if summaries else None

# =============================================================================
# TABLE 5: ANOMALY TABLE
# =============================================================================

def create_anomaly_table():
    """
    Create a table of detected anomalies for Power BI.
    
    This allows creating visuals that highlight unusual data points.
    """
    print("\n🚨 Creating Anomaly Table...")
    
    anomalies = []
    
    for data_type in ['enrolment', 'demographic', 'biometric']:
        filepath = OUTPUT_DATA_DIR / f'zscore_outliers_{data_type}.csv'
        if filepath.exists():
            df = pd.read_csv(filepath)
            df['data_type'] = data_type.title()
            anomalies.append(df)
    
    if anomalies:
        anomaly_table = pd.concat(anomalies, ignore_index=True)
        output_path = POWERBI_DIR / 'anomalies.csv'
        anomaly_table.to_csv(output_path, index=False)
        print(f"💾 Saved: {output_path}")
        print(f"   Anomalies: {len(anomaly_table)}")
    
    return anomaly_table if anomalies else None

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("EXPORTING DATA FOR POWER BI")
    print("=" * 50)
    
    # Create all tables
    fact_table = create_fact_table()
    dim_state = create_state_dimension()
    dim_date = create_date_dimension()
    state_summary = create_state_summary()
    anomaly_table = create_anomaly_table()
    
    print("\n" + "=" * 50)
    print("✅ ALL EXPORTS COMPLETE!")
    print("=" * 50)
    print(f"\n📁 Files saved to: {POWERBI_DIR}")
    print("\nFiles created:")
    for f in POWERBI_DIR.glob('*.csv'):
        print(f"   - {f.name}")
    
    print("\n📋 Next: Open Power BI Desktop and import these CSV files!")
