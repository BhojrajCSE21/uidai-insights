"""
Anomaly Detection & Machine Learning for UIDAI Aadhaar Data
============================================================

This script implements various ML techniques to detect anomalies
and patterns in the Aadhaar data.

WHAT IS ANOMALY DETECTION?
--------------------------
Anomaly detection finds "unusual" data points that don't follow
the normal pattern. In Aadhaar context, this could mean:
- A district suddenly having 10x more enrolments (suspicious?)
- A pincode with zero biometric updates (infrastructure issue?)
- Unusual spike on a specific date (data error or campaign?)

WHY IS THIS IMPORTANT FOR THE JOB?
----------------------------------
The job description mentions:
- "anomaly detection and performance analytics"
- "machine learning/statistical models for segmentation, classification, prediction"
This script demonstrates exactly those skills!
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import warnings
import joblib
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import PROCESSED_DATA_DIR, OUTPUT_DATA_DIR, MODEL_DIR

# Try importing sklearn (for ML models)
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    print("⚠️ scikit-learn not installed. Run: pip install scikit-learn")
    SKLEARN_AVAILABLE = False

# Set visualization style
plt.style.use('seaborn-v0_8-whitegrid')


class AnomalyDetector:
    """
    Anomaly Detection class for UIDAI data.
    
    This class implements multiple anomaly detection techniques:
    1. Statistical methods (Z-score, IQR) - Simple, interpretable
    2. Isolation Forest - ML-based, catches complex anomalies
    3. Time series analysis - For temporal anomalies
    """
    
    def __init__(self):
        """Initialize the detector."""
        self.figures_dir = OUTPUT_DATA_DIR / 'figures'
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        print("🔍 Anomaly Detector initialized")
    
    def load_data(self, data_type='enrolment'):
        """Load processed data."""
        file_map = {
            'enrolment': 'cleaned_enrolment.csv',
            'demographic': 'cleaned_demographic.csv',
            'biometric': 'cleaned_biometric.csv'
        }
        filepath = PROCESSED_DATA_DIR / file_map[data_type]
        df = pd.read_csv(filepath, parse_dates=['date'])
        print(f"✅ Loaded {len(df):,} rows of {data_type} data")
        return df
    
    # =========================================================================
    # METHOD 1: STATISTICAL OUTLIER DETECTION (Z-Score)
    # =========================================================================
    
    def detect_zscore_outliers(self, df, data_type='enrolment', threshold=3):
        """
        Detect outliers using Z-score method.
        
        WHAT IS Z-SCORE?
        ----------------
        Z-score tells you how many standard deviations a value is from the mean.
        
        Formula: Z = (X - mean) / standard_deviation
        
        Example:
        - If average daily enrolments = 1000, std = 200
        - A day with 1600 enrolments has Z = (1600-1000)/200 = 3
        - Z > 3 is usually considered an outlier (very unusual)
        
        WHY USE Z-SCORE?
        ----------------
        - Simple and fast
        - Easy to explain to stakeholders
        - Works well when data is roughly normally distributed
        - Industry standard for basic outlier detection
        
        THRESHOLD = 3:
        - Values with Z > 3 are in the top 0.3% (very rare)
        - Values with Z < -3 are in the bottom 0.3%
        """
        print(f"\n{'='*60}")
        print(f"Z-SCORE OUTLIER DETECTION - {data_type.upper()}")
        print(f"{'='*60}")
        
        # Get age columns based on data type
        if data_type == 'enrolment':
            age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
        elif data_type == 'demographic':
            age_cols = ['demo_age_5_17', 'demo_age_17_']
        else:
            age_cols = ['bio_age_5_17', 'bio_age_17_']
        
        # Create a copy and calculate total
        df_analysis = df.copy()
        df_analysis['total'] = df_analysis[age_cols].sum(axis=1)
        
        # Calculate Z-score for total column
        # Step 1: Calculate mean and standard deviation
        mean_val = df_analysis['total'].mean()
        std_val = df_analysis['total'].std()
        
        print(f"\n📊 Statistics:")
        print(f"   Mean: {mean_val:.2f}")
        print(f"   Std Dev: {std_val:.2f}")
        print(f"   Threshold: Z > {threshold} or Z < -{threshold}")
        
        # Step 2: Calculate Z-score for each row
        # (value - mean) / std
        df_analysis['zscore'] = (df_analysis['total'] - mean_val) / std_val
        
        # Step 3: Flag outliers (absolute Z-score > threshold)
        df_analysis['is_outlier'] = abs(df_analysis['zscore']) > threshold
        
        # Count and display outliers
        outliers = df_analysis[df_analysis['is_outlier']]
        outlier_count = len(outliers)
        outlier_pct = (outlier_count / len(df_analysis)) * 100
        
        print(f"\n🚨 Outliers Found: {outlier_count:,} ({outlier_pct:.2f}%)")
        
        if outlier_count > 0:
            # Show top outliers (highest Z-scores)
            top_outliers = outliers.nlargest(10, 'zscore')[
                ['date', 'state', 'district', 'total', 'zscore']
            ]
            print(f"\n📋 Top 10 Outliers (highest values):")
            print(top_outliers.to_string(index=False))
            
            # Analyze which states have most outliers
            outlier_by_state = outliers.groupby('state').size().sort_values(ascending=False)
            print(f"\n🗺️ States with most outliers:")
            print(outlier_by_state.head(10))
        
        # Save outliers report
        outliers_report = outliers[['date', 'state', 'district', 'pincode', 'total', 'zscore']]
        output_path = OUTPUT_DATA_DIR / f'zscore_outliers_{data_type}.csv'
        outliers_report.to_csv(output_path, index=False)
        print(f"\n💾 Saved outliers to: {output_path}")
        
        # Create visualization
        self._plot_zscore_distribution(df_analysis, data_type, threshold)
        
        return df_analysis
    
    def _plot_zscore_distribution(self, df, data_type, threshold):
        """
        Create a histogram showing Z-score distribution with outlier zones.
        
        WHY THIS VISUALIZATION?
        -----------------------
        - Shows the overall distribution of values
        - Red zones highlight where outliers are
        - Helps stakeholders understand "how unusual" outliers are
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Distribution of total values
        ax1 = axes[0]
        ax1.hist(df['total'], bins=50, edgecolor='black', alpha=0.7, color='#3498db')
        ax1.set_xlabel('Total Count')
        ax1.set_ylabel('Frequency')
        ax1.set_title(f'Distribution of {data_type.title()} Counts', fontweight='bold')
        
        # Plot 2: Z-score distribution with threshold lines
        ax2 = axes[1]
        ax2.hist(df['zscore'], bins=50, edgecolor='black', alpha=0.7, color='#2ecc71')
        ax2.axvline(x=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold (+{threshold})')
        ax2.axvline(x=-threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold (-{threshold})')
        ax2.set_xlabel('Z-Score')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Z-Score Distribution', fontweight='bold')
        ax2.legend()
        
        plt.tight_layout()
        
        fig_path = self.figures_dir / f'zscore_distribution_{data_type}.png'
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"📈 Saved chart: {fig_path}")
    
    # =========================================================================
    # METHOD 2: ISOLATION FOREST (ML-BASED)
    # =========================================================================
    
    def detect_isolation_forest(self, df, data_type='enrolment', contamination=0.01):
        """
        Detect anomalies using Isolation Forest algorithm.
        
        WHAT IS ISOLATION FOREST?
        -------------------------
        Isolation Forest is a machine learning algorithm that works on a 
        simple principle: anomalies are "few and different", so they are 
        easier to "isolate" from the rest of the data.
        
        HOW IT WORKS:
        1. Build random decision trees
        2. In each tree, randomly select a feature and split point
        3. Anomalies get isolated (reach a leaf) in fewer splits
        4. Normal points need more splits to be isolated
        
        ANALOGY:
        Imagine playing 20 questions to identify someone in a crowd:
        - A person wearing a clown costume (anomaly) can be identified 
          in 1-2 questions: "Are they wearing a costume?"
        - A normal person needs many questions to narrow down
        
        WHY USE ISOLATION FOREST?
        -------------------------
        - Works well with high-dimensional data
        - Doesn't require labeled data (unsupervised)
        - Fast and scalable
        - Catches anomalies that Z-score might miss
        
        CONTAMINATION = 0.01:
        - We expect about 1% of data to be anomalous
        - This is a hyperparameter you can tune
        """
        if not SKLEARN_AVAILABLE:
            print("⚠️ Skipping Isolation Forest - sklearn not installed")
            return None
        
        print(f"\n{'='*60}")
        print(f"ISOLATION FOREST ANOMALY DETECTION - {data_type.upper()}")
        print(f"{'='*60}")
        
        # Get age columns
        if data_type == 'enrolment':
            age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
        elif data_type == 'demographic':
            age_cols = ['demo_age_5_17', 'demo_age_17_']
        else:
            age_cols = ['bio_age_5_17', 'bio_age_17_']
        
        # Prepare features for the model
        # We use age columns + month + day_of_week as features
        df_analysis = df.copy()
        df_analysis['total'] = df_analysis[age_cols].sum(axis=1)
        
        # Select features for anomaly detection
        feature_cols = age_cols + ['month', 'day_of_week']
        
        # IMPORTANT: Handle NaN values before ML modeling!
        # sklearn doesn't accept NaN values, so we need to handle them
        # Option 1: Drop rows with NaN (we'll use this for simplicity)
        # Option 2: Impute with mean/median (more advanced)
        df_analysis = df_analysis.dropna(subset=feature_cols)
        print(f"   Rows after dropping NaN: {len(df_analysis):,}")
        
        X = df_analysis[feature_cols].values
        
        print(f"\n⚙️ Model Configuration:")
        print(f"   Features: {feature_cols}")
        print(f"   Contamination: {contamination} (expecting {contamination*100}% anomalies)")
        
        # Step 1: Standardize features (important for ML models!)
        # StandardScaler transforms data to have mean=0, std=1
        # This ensures all features have equal importance
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Step 2: Train Isolation Forest
        print(f"   Training Isolation Forest...")
        iso_forest = IsolationForest(
            contamination=contamination,  # Expected proportion of outliers
            random_state=42,              # For reproducibility
            n_estimators=100,             # Number of trees
            n_jobs=-1                     # Use all CPU cores
        )
        
        # fit_predict trains the model and returns predictions
        # -1 = anomaly, 1 = normal
        predictions = iso_forest.fit_predict(X_scaled)
        
        # Add predictions to dataframe
        df_analysis['anomaly_score'] = iso_forest.decision_function(X_scaled)
        df_analysis['is_anomaly'] = predictions == -1
        
        # Count anomalies
        anomaly_count = (predictions == -1).sum()
        anomaly_pct = (anomaly_count / len(df_analysis)) * 100
        
        print(f"\n🚨 Anomalies Detected: {anomaly_count:,} ({anomaly_pct:.2f}%)")
        
        # Analyze anomalies
        anomalies = df_analysis[df_analysis['is_anomaly']]
        
        if len(anomalies) > 0:
            # Show top anomalies (lowest anomaly scores = most anomalous)
            top_anomalies = anomalies.nsmallest(10, 'anomaly_score')[
                ['date', 'state', 'district', 'total', 'anomaly_score']
            ]
            print(f"\n📋 Top 10 Most Anomalous Records:")
            print(top_anomalies.to_string(index=False))
            
            # State-wise anomaly distribution
            print(f"\n🗺️ States with most anomalies:")
            anomaly_by_state = anomalies.groupby('state').size().sort_values(ascending=False)
            print(anomaly_by_state.head(10))
        
        # Save model for future use
        model_path = MODEL_DIR / f'isolation_forest_{data_type}.pkl'
        joblib.dump(iso_forest, model_path)
        print(f"\n💾 Saved model to: {model_path}")
        
        # Save scaler too (needed when using the model later)
        scaler_path = MODEL_DIR / f'scaler_{data_type}.pkl'
        joblib.dump(scaler, scaler_path)
        
        # Save anomaly report
        anomaly_report = anomalies[['date', 'state', 'district', 'pincode', 'total', 'anomaly_score']]
        output_path = OUTPUT_DATA_DIR / f'isolation_forest_anomalies_{data_type}.csv'
        anomaly_report.to_csv(output_path, index=False)
        print(f"💾 Saved anomalies to: {output_path}")
        
        # Create visualization
        self._plot_anomaly_scatter(df_analysis, data_type)
        
        return df_analysis
    
    def _plot_anomaly_scatter(self, df, data_type):
        """
        Create a scatter plot showing normal points vs anomalies.
        
        WHY SCATTER PLOT?
        -----------------
        - Visually separates normal vs anomalous points
        - Shows the relationship between features
        - Red points clearly highlight anomalies
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Separate normal and anomaly points
        normal = df[~df['is_anomaly']]
        anomalies = df[df['is_anomaly']]
        
        # Plot normal points in blue
        ax.scatter(normal['month'], normal['total'], 
                   c='#3498db', alpha=0.3, s=10, label='Normal')
        
        # Plot anomalies in red
        ax.scatter(anomalies['month'], anomalies['total'], 
                   c='red', alpha=0.8, s=50, label='Anomaly', marker='x')
        
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Count')
        ax.set_title(f'Anomaly Detection Results - {data_type.title()}', 
                     fontsize=14, fontweight='bold')
        ax.legend()
        
        plt.tight_layout()
        
        fig_path = self.figures_dir / f'anomaly_scatter_{data_type}.png'
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"📈 Saved chart: {fig_path}")
    
    # =========================================================================
    # METHOD 3: TIME SERIES ANOMALY DETECTION
    # =========================================================================
    
    def detect_temporal_anomalies(self, df, data_type='enrolment', window=7):
        """
        Detect anomalies in time series using rolling statistics.
        
        WHAT IS ROLLING WINDOW ANALYSIS?
        ---------------------------------
        Instead of comparing each day to the overall average,
        we compare it to the recent past (rolling window).
        
        Example with window=7:
        - For each day, calculate the average of the past 7 days
        - If today's value is way higher/lower than that average,
          it's anomalous relative to recent trends
        
        WHY USE ROLLING WINDOWS?
        ------------------------
        - Handles seasonal trends (enrolments might be higher in Q4)
        - Catches sudden spikes or drops
        - More sensitive to local patterns
        
        LOGIC:
        1. Group data by date to get daily totals
        2. Calculate rolling mean and std over the past N days
        3. If today's value is > mean + 2*std, flag as anomaly
        """
        print(f"\n{'='*60}")
        print(f"TIME SERIES ANOMALY DETECTION - {data_type.upper()}")
        print(f"{'='*60}")
        
        # Get age columns
        if data_type == 'enrolment':
            age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
        elif data_type == 'demographic':
            age_cols = ['demo_age_5_17', 'demo_age_17_']
        else:
            age_cols = ['bio_age_5_17', 'bio_age_17_']
        
        # Step 1: Aggregate daily totals
        df_temp = df.copy()
        df_temp['total'] = df_temp[age_cols].sum(axis=1)
        daily = df_temp.groupby('date')['total'].sum().reset_index()
        daily = daily.sort_values('date')
        
        print(f"\n📅 Analyzing {len(daily)} days of data")
        print(f"   Date range: {daily['date'].min().strftime('%Y-%m-%d')} to {daily['date'].max().strftime('%Y-%m-%d')}")
        print(f"   Rolling window: {window} days")
        
        # Step 2: Calculate rolling statistics
        # rolling(window) creates a "sliding window" of past N values
        # .mean() and .std() calculate mean and std for that window
        daily['rolling_mean'] = daily['total'].rolling(window=window, min_periods=1).mean()
        daily['rolling_std'] = daily['total'].rolling(window=window, min_periods=1).std()
        
        # Fill NaN std with 0 (first few points)
        daily['rolling_std'] = daily['rolling_std'].fillna(0)
        
        # Step 3: Calculate bounds for anomaly detection
        # Upper bound: mean + 2 standard deviations
        # Lower bound: mean - 2 standard deviations
        # Values outside these bounds are anomalies (95% confidence)
        daily['upper_bound'] = daily['rolling_mean'] + 2 * daily['rolling_std']
        daily['lower_bound'] = daily['rolling_mean'] - 2 * daily['rolling_std']
        
        # Step 4: Flag anomalies
        daily['is_spike'] = daily['total'] > daily['upper_bound']
        daily['is_drop'] = daily['total'] < daily['lower_bound']
        daily['is_anomaly'] = daily['is_spike'] | daily['is_drop']
        
        # Count anomalies
        spike_count = daily['is_spike'].sum()
        drop_count = daily['is_drop'].sum()
        total_anomalies = daily['is_anomaly'].sum()
        
        print(f"\n🚨 Temporal Anomalies Found:")
        print(f"   📈 Spikes (unusually high): {spike_count}")
        print(f"   📉 Drops (unusually low): {drop_count}")
        print(f"   Total: {total_anomalies}")
        
        # Show anomalous dates
        if total_anomalies > 0:
            anomalies = daily[daily['is_anomaly']][['date', 'total', 'rolling_mean', 'is_spike', 'is_drop']]
            print(f"\n📋 Anomalous Dates:")
            print(anomalies.to_string(index=False))
        
        # Save report
        output_path = OUTPUT_DATA_DIR / f'temporal_anomalies_{data_type}.csv'
        daily.to_csv(output_path, index=False)
        print(f"\n💾 Saved temporal analysis to: {output_path}")
        
        # Create visualization
        self._plot_temporal_anomalies(daily, data_type)
        
        return daily
    
    def _plot_temporal_anomalies(self, daily, data_type):
        """
        Create a time series plot with anomalies highlighted.
        
        WHY THIS VISUALIZATION?
        -----------------------
        - Shows trends over time
        - Rolling mean creates a "baseline" expectation
        - Anomalies clearly visible as points outside the shaded area
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Plot actual values
        ax.plot(daily['date'], daily['total'], 
                color='#3498db', linewidth=1, alpha=0.8, label='Actual')
        
        # Plot rolling mean
        ax.plot(daily['date'], daily['rolling_mean'], 
                color='#2ecc71', linewidth=2, label='Rolling Mean', linestyle='--')
        
        # Plot bounds as shaded area
        ax.fill_between(daily['date'], daily['lower_bound'], daily['upper_bound'], 
                        alpha=0.2, color='green', label='Expected Range')
        
        # Highlight anomalies
        spikes = daily[daily['is_spike']]
        drops = daily[daily['is_drop']]
        
        ax.scatter(spikes['date'], spikes['total'], 
                   color='red', s=100, zorder=5, label='Spike', marker='^')
        ax.scatter(drops['date'], drops['total'], 
                   color='orange', s=100, zorder=5, label='Drop', marker='v')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Total Count')
        ax.set_title(f'Time Series Anomaly Detection - {data_type.title()}', 
                     fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        plt.tight_layout()
        
        fig_path = self.figures_dir / f'temporal_anomalies_{data_type}.png'
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"📈 Saved chart: {fig_path}")
    
    # =========================================================================
    # METHOD 4: GEOGRAPHIC ANOMALY DETECTION
    # =========================================================================
    
    def detect_geographic_anomalies(self, df, data_type='enrolment'):
        """
        Detect states/districts with unusually high or low activity.
        
        LOGIC:
        ------
        1. Calculate total per state
        2. Compare each state's value to the overall median
        3. States with values >> median are over-performing
        4. States with values << median are under-performing
        
        WHY MEDIAN INSTEAD OF MEAN?
        ---------------------------
        Median is more robust to outliers. If one huge state (like UP)
        has 10x more enrolments, the mean gets pulled up, but median
        remains stable.
        """
        print(f"\n{'='*60}")
        print(f"GEOGRAPHIC ANOMALY DETECTION - {data_type.upper()}")
        print(f"{'='*60}")
        
        # Get age columns
        if data_type == 'enrolment':
            age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
        elif data_type == 'demographic':
            age_cols = ['demo_age_5_17', 'demo_age_17_']
        else:
            age_cols = ['bio_age_5_17', 'bio_age_17_']
        
        # Aggregate by state
        df_temp = df.copy()
        df_temp['total'] = df_temp[age_cols].sum(axis=1)
        state_totals = df_temp.groupby('state')['total'].sum().reset_index()
        
        # Calculate statistics
        median_val = state_totals['total'].median()
        mean_val = state_totals['total'].mean()
        std_val = state_totals['total'].std()
        
        print(f"\n📊 State-level Statistics:")
        print(f"   Number of states: {len(state_totals)}")
        print(f"   Median: {median_val:,.0f}")
        print(f"   Mean: {mean_val:,.0f}")
        print(f"   Std Dev: {std_val:,.0f}")
        
        # Calculate deviation from median
        state_totals['deviation'] = (state_totals['total'] - median_val) / median_val * 100
        state_totals['zscore'] = (state_totals['total'] - mean_val) / std_val
        
        # Flag anomalies (more than 2 std from mean)
        state_totals['is_anomaly'] = abs(state_totals['zscore']) > 2
        
        # Separate over-performers and under-performers
        over_performers = state_totals[state_totals['deviation'] > 100].sort_values('deviation', ascending=False)
        under_performers = state_totals[state_totals['deviation'] < -50].sort_values('deviation')
        
        print(f"\n🏆 Over-performing States (>100% above median):")
        if len(over_performers) > 0:
            print(over_performers[['state', 'total', 'deviation']].to_string(index=False))
        else:
            print("   None")
        
        print(f"\n⚠️ Under-performing States (>50% below median):")
        if len(under_performers) > 0:
            print(under_performers[['state', 'total', 'deviation']].to_string(index=False))
        else:
            print("   None")
        
        # Save report
        output_path = OUTPUT_DATA_DIR / f'geographic_anomalies_{data_type}.csv'
        state_totals.to_csv(output_path, index=False)
        print(f"\n💾 Saved geographic analysis to: {output_path}")
        
        return state_totals
    
    # =========================================================================
    # COMPREHENSIVE ANOMALY REPORT
    # =========================================================================
    
    def generate_full_report(self, data_type='enrolment'):
        """
        Run all anomaly detection methods and generate comprehensive report.
        """
        print(f"\n{'#'*60}")
        print(f"# COMPREHENSIVE ANOMALY REPORT - {data_type.upper()}")
        print(f"{'#'*60}")
        
        # Load data
        df = self.load_data(data_type)
        
        # Run all methods
        zscore_results = self.detect_zscore_outliers(df, data_type)
        iforest_results = self.detect_isolation_forest(df, data_type)
        temporal_results = self.detect_temporal_anomalies(df, data_type)
        geo_results = self.detect_geographic_anomalies(df, data_type)
        
        print(f"\n{'='*60}")
        print(f"✅ ANOMALY DETECTION COMPLETE for {data_type.upper()}")
        print(f"{'='*60}")
        
        return {
            'zscore': zscore_results,
            'isolation_forest': iforest_results,
            'temporal': temporal_results,
            'geographic': geo_results
        }


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    """
    Run anomaly detection for all three datasets.
    """
    detector = AnomalyDetector()
    
    # Analyze all datasets
    datasets = ['enrolment', 'demographic', 'biometric']
    results = {}
    
    for data_type in datasets:
        results[data_type] = detector.generate_full_report(data_type)
    
    print(f"\n{'#'*60}")
    print("# ALL ANOMALY DETECTION COMPLETE!")
    print(f"# Reports saved in: {OUTPUT_DATA_DIR}")
    print(f"# Models saved in: {MODEL_DIR}")
    print(f"# Charts saved in: {OUTPUT_DATA_DIR / 'figures'}")
    print(f"{'#'*60}")
