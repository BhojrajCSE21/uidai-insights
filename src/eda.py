"""
Exploratory Data Analysis (EDA) for UIDAI Aadhaar Data
======================================================

This script performs comprehensive analysis on the cleaned Aadhaar datasets
to uncover patterns, trends, and insights.

EDA Goals:
1. Understand data distributions (descriptive statistics)
2. Identify geographic patterns (state-wise, district-wise)
3. Discover temporal trends (monthly, quarterly)
4. Analyze age demographics (who is enrolling/updating?)
5. Find anomalies and outliers
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.config import PROCESSED_DATA_DIR, OUTPUT_DATA_DIR

# Set visualization style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


class EDAAnalyzer:
    """
    Exploratory Data Analysis class for UIDAI data.
    
    WHY THIS CLASS?
    ---------------
    We use a class to organize all EDA functions together.
    This makes the code:
    - Reusable (can analyze any dataset)
    - Organized (all functions in one place)
    - Easy to extend (add new analysis methods)
    """
    
    def __init__(self):
        """Initialize the analyzer and create output directories."""
        self.figures_dir = OUTPUT_DATA_DIR / 'figures'
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        print("📊 EDA Analyzer initialized")
        print(f"   Figures will be saved to: {self.figures_dir}")
    
    def load_processed_data(self, data_type='enrolment'):
        """
        Load cleaned data from processed directory.
        
        LOGIC:
        ------
        We load the pre-cleaned CSVs and parse dates properly.
        The 'parse_dates' parameter tells pandas to convert date columns
        to datetime objects, which enables time-based analysis.
        """
        print(f"\n📂 Loading processed {data_type} data...")
        
        file_map = {
            'enrolment': 'cleaned_enrolment.csv',
            'demographic': 'cleaned_demographic.csv',
            'biometric': 'cleaned_biometric.csv'
        }
        
        filepath = PROCESSED_DATA_DIR / file_map[data_type]
        df = pd.read_csv(filepath, parse_dates=['date'])
        
        print(f"✅ Loaded {len(df):,} rows")
        return df
    
    # =========================================================================
    # SECTION 1: DESCRIPTIVE STATISTICS
    # =========================================================================
    
    def descriptive_stats(self, df, data_type='enrolment'):
        """
        Generate descriptive statistics for the dataset.
        
        WHAT ARE DESCRIPTIVE STATISTICS?
        ---------------------------------
        These are summary numbers that describe your data:
        - Count: How many rows?
        - Mean: Average value
        - Std: Standard deviation (how spread out the data is)
        - Min/Max: Smallest and largest values
        - Percentiles (25%, 50%, 75%): Data distribution
        
        WHY DO WE NEED THIS?
        --------------------
        Before doing complex analysis, we need to understand:
        - The scale of our data
        - If there are any obvious outliers
        - The typical values we're working with
        """
        print(f"\n{'='*60}")
        print(f"DESCRIPTIVE STATISTICS - {data_type.upper()}")
        print(f"{'='*60}")
        
        # Basic info
        print(f"\n📋 Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
        print(f"📅 Date Range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"🗺️  States: {df['state'].nunique()} unique states/UTs")
        print(f"📍 Districts: {df['district'].nunique()} unique districts")
        print(f"📮 Pincodes: {df['pincode'].nunique()} unique pincodes")
        
        # Numeric columns statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Exclude year, month, quarter, day_of_week from age analysis
        age_cols = [col for col in numeric_cols if 'age' in col.lower()]
        
        if age_cols:
            print(f"\n📊 Age Group Statistics:")
            print(df[age_cols].describe().round(2))
        
        return df.describe()
    
    # =========================================================================
    # SECTION 2: GEOGRAPHIC ANALYSIS (STATE-WISE)
    # =========================================================================
    
    def state_wise_analysis(self, df, data_type='enrolment'):
        """
        Analyze data distribution across states.
        
        LOGIC:
        ------
        1. Group data by state
        2. Sum up all numeric values (enrolments/updates) per state
        3. Calculate percentages
        4. Create visualizations
        
        WHY GROUP BY STATE?
        -------------------
        States have different populations and resources.
        This analysis helps identify:
        - Which states have highest Aadhaar activity?
        - Are there states with surprisingly low activity?
        - Regional patterns in adoption/updates
        """
        print(f"\n{'='*60}")
        print(f"STATE-WISE ANALYSIS - {data_type.upper()}")
        print(f"{'='*60}")
        
        # Identify age columns based on data type
        if data_type == 'enrolment':
            age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
        elif data_type == 'demographic':
            age_cols = ['demo_age_5_17', 'demo_age_17_']
        else:  # biometric
            age_cols = ['bio_age_5_17', 'bio_age_17_']
        
        # Group by state and sum all age columns
        # .groupby('state') groups all rows with the same state together
        # .sum() adds up all the numeric values within each group
        state_summary = df.groupby('state')[age_cols].sum()
        
        # Calculate total per state (sum across all age groups)
        state_summary['total'] = state_summary.sum(axis=1)
        
        # Sort by total (descending) to see top states first
        state_summary = state_summary.sort_values('total', ascending=False)
        
        # Calculate percentage contribution of each state
        total_all = state_summary['total'].sum()
        state_summary['percentage'] = (state_summary['total'] / total_all * 100).round(2)
        
        # Display top 10 states
        print(f"\n🏆 Top 10 States by {data_type.title()}:")
        print(state_summary[['total', 'percentage']].head(10))
        
        # Display bottom 5 states (might need attention)
        print(f"\n⚠️ Bottom 5 States (might need attention):")
        print(state_summary[['total', 'percentage']].tail(5))
        
        # Save state summary
        output_path = OUTPUT_DATA_DIR / f'state_summary_{data_type}.csv'
        state_summary.to_csv(output_path)
        print(f"\n💾 Saved state summary to: {output_path}")
        
        # Create visualization
        self._plot_state_distribution(state_summary, data_type)
        
        return state_summary
    
    def _plot_state_distribution(self, state_summary, data_type):
        """
        Create a horizontal bar chart showing state-wise distribution.
        
        WHY HORIZONTAL BAR CHART?
        -------------------------
        - State names are long, horizontal bars give space for labels
        - Easy to compare values across states
        - Top states appear at the top (intuitive)
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot top 15 states
        top_15 = state_summary['total'].head(15)
        
        # Create horizontal bar chart
        colors = sns.color_palette("viridis", len(top_15))
        bars = ax.barh(range(len(top_15)), top_15.values, color=colors)
        
        # Add state names as y-axis labels
        ax.set_yticks(range(len(top_15)))
        ax.set_yticklabels(top_15.index)
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, top_15.values)):
            ax.text(val + 1000, i, f'{val:,.0f}', va='center', fontsize=9)
        
        # Formatting
        ax.set_xlabel(f'Total {data_type.title()} Count')
        ax.set_title(f'Top 15 States by Aadhaar {data_type.title()}', fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Highest value at top
        
        plt.tight_layout()
        
        # Save figure
        fig_path = self.figures_dir / f'state_distribution_{data_type}.png'
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"📈 Saved chart: {fig_path}")
    
    # =========================================================================
    # SECTION 3: TEMPORAL ANALYSIS (TIME-BASED TRENDS)
    # =========================================================================
    
    def temporal_analysis(self, df, data_type='enrolment'):
        """
        Analyze trends over time.
        
        LOGIC:
        ------
        1. Group data by month/quarter
        2. Sum values to get totals per time period
        3. Look for trends, seasonality, spikes
        
        WHY TEMPORAL ANALYSIS?
        ----------------------
        Time-based patterns reveal:
        - Growth/decline trends
        - Seasonal patterns (more enrolments in certain months?)
        - Impact of government campaigns or events
        - Unusual spikes that might indicate data quality issues
        """
        print(f"\n{'='*60}")
        print(f"TEMPORAL ANALYSIS - {data_type.upper()}")
        print(f"{'='*60}")
        
        # Identify age columns
        if data_type == 'enrolment':
            age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
        elif data_type == 'demographic':
            age_cols = ['demo_age_5_17', 'demo_age_17_']
        else:
            age_cols = ['bio_age_5_17', 'bio_age_17_']
        
        # Create a copy and add total column
        df_temp = df.copy()
        df_temp['total'] = df_temp[age_cols].sum(axis=1)
        
        # Monthly aggregation
        # We extract year-month and group by it
        df_temp['year_month'] = df_temp['date'].dt.to_period('M')
        monthly = df_temp.groupby('year_month')['total'].sum()
        
        print(f"\n📅 Monthly Trend:")
        print(monthly)
        
        # Calculate month-over-month growth
        monthly_growth = monthly.pct_change() * 100
        print(f"\n📈 Month-over-Month Growth (%):")
        print(monthly_growth.dropna().round(2))
        
        # Save monthly trends
        monthly_df = pd.DataFrame({
            'month': monthly.index.astype(str),
            'total': monthly.values,
            'growth_pct': monthly_growth.values
        })
        output_path = OUTPUT_DATA_DIR / f'monthly_trends_{data_type}.csv'
        monthly_df.to_csv(output_path, index=False)
        print(f"\n💾 Saved monthly trends to: {output_path}")
        
        # Create time series visualization
        self._plot_time_series(monthly, data_type)
        
        return monthly
    
    def _plot_time_series(self, monthly, data_type):
        """
        Create a line chart showing trends over time.
        
        WHY LINE CHART?
        ---------------
        - Best for showing continuous trends over time
        - Easy to spot growth, decline, or spikes
        - Can see patterns and seasonality
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convert period index to datetime for plotting
        x = [str(p) for p in monthly.index]
        y = monthly.values
        
        # Plot line with markers
        ax.plot(x, y, marker='o', linewidth=2, markersize=8, color='#2196F3')
        ax.fill_between(range(len(x)), y, alpha=0.3, color='#2196F3')
        
        # Formatting
        ax.set_xlabel('Month')
        ax.set_ylabel(f'Total {data_type.title()} Count')
        ax.set_title(f'Monthly Aadhaar {data_type.title()} Trend', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Format y-axis with commas
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        plt.tight_layout()
        
        # Save figure
        fig_path = self.figures_dir / f'monthly_trend_{data_type}.png'
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"📈 Saved chart: {fig_path}")
    
    # =========================================================================
    # SECTION 4: AGE DEMOGRAPHIC ANALYSIS
    # =========================================================================
    
    def age_analysis(self, df, data_type='enrolment'):
        """
        Analyze distribution across age groups.
        
        LOGIC:
        ------
        1. Sum up totals for each age group
        2. Calculate percentages
        3. Visualize the distribution
        
        WHY AGE ANALYSIS?
        -----------------
        Understanding age demographics reveals:
        - Is the child enrolment program working? (0-5, 5-17)
        - What proportion is adults vs children?
        - Are biometric updates more common in certain age groups?
        """
        print(f"\n{'='*60}")
        print(f"AGE DEMOGRAPHIC ANALYSIS - {data_type.upper()}")
        print(f"{'='*60}")
        
        # Identify age columns based on data type
        if data_type == 'enrolment':
            age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
            age_labels = ['Children (0-5)', 'Youth (5-17)', 'Adults (18+)']
        elif data_type == 'demographic':
            age_cols = ['demo_age_5_17', 'demo_age_17_']
            age_labels = ['Youth (5-17)', 'Adults (17+)']
        else:
            age_cols = ['bio_age_5_17', 'bio_age_17_']
            age_labels = ['Youth (5-17)', 'Adults (17+)']
        
        # Calculate totals for each age group
        age_totals = df[age_cols].sum()
        total = age_totals.sum()
        
        # Create summary DataFrame
        age_summary = pd.DataFrame({
            'Age Group': age_labels,
            'Total': age_totals.values,
            'Percentage': (age_totals.values / total * 100).round(2)
        })
        
        print(f"\n👥 Age Group Distribution:")
        print(age_summary.to_string(index=False))
        
        # Create pie chart
        self._plot_age_distribution(age_summary, data_type)
        
        return age_summary
    
    def _plot_age_distribution(self, age_summary, data_type):
        """
        Create a pie chart showing age distribution.
        
        WHY PIE CHART?
        --------------
        - Perfect for showing parts of a whole (percentages)
        - Easy to understand at a glance
        - Good for categorical comparisons
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        explode = [0.02] * len(age_summary)  # Slight separation between slices
        
        wedges, texts, autotexts = ax.pie(
            age_summary['Total'],
            labels=age_summary['Age Group'],
            autopct='%1.1f%%',
            explode=explode[:len(age_summary)],
            colors=colors[:len(age_summary)],
            startangle=90,
            textprops={'fontsize': 12}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_fontweight('bold')
        
        ax.set_title(f'Age Distribution - Aadhaar {data_type.title()}', 
                     fontsize=14, fontweight='bold')
        
        # Add legend with actual numbers
        legend_labels = [f"{row['Age Group']}: {row['Total']:,.0f}" 
                        for _, row in age_summary.iterrows()]
        ax.legend(legend_labels, loc='lower right', fontsize=10)
        
        plt.tight_layout()
        
        # Save figure
        fig_path = self.figures_dir / f'age_distribution_{data_type}.png'
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"📈 Saved chart: {fig_path}")
    
    # =========================================================================
    # SECTION 5: COMPREHENSIVE REPORT
    # =========================================================================
    
    def generate_full_report(self, data_type='enrolment'):
        """
        Run all analyses and generate a comprehensive report.
        
        This is the main entry point that combines all analyses.
        """
        print(f"\n{'#'*60}")
        print(f"# COMPREHENSIVE EDA REPORT - {data_type.upper()}")
        print(f"{'#'*60}")
        
        # Load data
        df = self.load_processed_data(data_type)
        
        # Run all analyses
        self.descriptive_stats(df, data_type)
        state_summary = self.state_wise_analysis(df, data_type)
        monthly_trend = self.temporal_analysis(df, data_type)
        age_summary = self.age_analysis(df, data_type)
        
        print(f"\n{'='*60}")
        print(f"✅ EDA COMPLETE for {data_type.upper()}")
        print(f"{'='*60}")
        
        return {
            'state_summary': state_summary,
            'monthly_trend': monthly_trend,
            'age_summary': age_summary
        }


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    """
    Run EDA for all three datasets.
    
    This block only runs when you execute this file directly:
        python src/eda.py
    
    It won't run if you import this file as a module.
    """
    analyzer = EDAAnalyzer()
    
    # Analyze all three datasets
    datasets = ['enrolment', 'demographic', 'biometric']
    results = {}
    
    for data_type in datasets:
        results[data_type] = analyzer.generate_full_report(data_type)
    
    print(f"\n{'#'*60}")
    print("# ALL EDA REPORTS GENERATED SUCCESSFULLY!")
    print(f"# Check output folder: {OUTPUT_DATA_DIR}")
    print(f"# Charts saved in: {OUTPUT_DATA_DIR / 'figures'}")
    print(f"{'#'*60}")
