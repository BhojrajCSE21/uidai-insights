# 📋 Methodology Documentation

## UIDAI Aadhaar Insights Analysis

This document details the complete methodology adopted for analyzing UIDAI Aadhaar enrolment and update data.

---

## 1. Data Sources

### Datasets Used

| Dataset             | Source    | Records   | Time Period         |
| ------------------- | --------- | --------- | ------------------- |
| Aadhaar Enrolment   | UIDAI API | 1,006,029 | Mar 2025 - Dec 2025 |
| Demographic Updates | UIDAI API | 2,071,700 | Jan 2025 - Dec 2025 |
| Biometric Updates   | UIDAI API | 1,861,108 | Jan 2025 - Dec 2025 |

### Data Schema

**Enrolment Data:**
| Column | Type | Description |
|--------|------|-------------|
| date | Date | Enrolment date |
| state | String | State/UT name |
| district | String | District name |
| pincode | Integer | 6-digit pincode |
| age_0_5 | Integer | Children aged 0-5 years |
| age_5_17 | Integer | Youth aged 5-17 years |
| age_18_greater | Integer | Adults aged 18+ years |

**Demographic/Biometric Updates:**
| Column | Type | Description |
|--------|------|-------------|
| date | Date | Update date |
| state | String | State/UT name |
| district | String | District name |
| pincode | Integer | 6-digit pincode |
| demo/bio*age_5_17 | Integer | Youth updates |
| demo/bio_age_17* | Integer | Adult updates |

---

## 2. Data Preprocessing

### 2.1 Data Loading

```python
# Recursive file discovery
files = RAW_DATA_DIR.glob('**/*enrolment*.csv')

# Combine multiple CSV files
combined_df = pd.concat([pd.read_csv(f) for f in files])
```

### 2.2 Date Handling

- Converted string dates to datetime objects
- Used `dayfirst=True` for DD-MM-YYYY format
- Extracted temporal features (year, month, quarter, day_of_week)

### 2.3 Pincode Validation

- Standardized to exactly 6 digits using `str.zfill(6)`
- Removed records with invalid pincode lengths

### 2.4 Age Validation

- Applied constraints: 0 ≤ age ≤ 150
- Removed records outside valid range

### 2.5 Duplicate Removal

- Identified and removed exact duplicate rows
- Enrolment: 22,957 duplicates removed (2.3%)
- Demographic: 814,930 duplicates removed (39.3%)
- Biometric: 331,436 duplicates removed (17.8%)

### 2.6 Data Quality Summary

| Dataset     | Original  | After Cleaning | Retained |
| ----------- | --------- | -------------- | -------- |
| Enrolment   | 1,006,029 | 981,295        | 97.5%    |
| Demographic | 2,071,700 | 1,225,607      | 59.2%    |
| Biometric   | 1,861,108 | 1,476,599      | 79.3%    |

---

## 3. Exploratory Data Analysis (EDA)

### 3.1 Descriptive Statistics

- Dataset shape, column types, null values
- Summary statistics (mean, std, min, max, percentiles)
- Unique value counts for categorical columns

### 3.2 Geographic Analysis

**Method:** Group by state → Sum age columns → Calculate percentage

**Key Findings:**

- Top 3 states (Enrolment): UP, Bihar, MP (47% of total)
- Geographic concentration in North India

### 3.3 Temporal Analysis

**Method:** Group by month → Calculate totals → Compute growth rates

**Key Findings:**

- August 2025: Major enrolment spike (~5x normal)
- January 2025: Biometric update peak (8M+)

### 3.4 Age Demographic Analysis

**Method:** Sum each age column → Calculate percentages

**Key Findings:**

- Enrolment: 68.5% children (0-5), 29% youth, 2.5% adults
- Updates: 89.5% adults (demographic), 50-50 (biometric)

---

## 4. Anomaly Detection

### 4.1 Statistical Method (Z-Score)

**Formula:**

```
Z = (X - μ) / σ
```

**Threshold:** |Z| > 3 (top/bottom 0.3%)

**Results:**
| Dataset | Outliers | Percentage |
|---------|----------|------------|
| Enrolment | 69,850 | 7.1% |
| Demographic | 31,544 | 2.6% |
| Biometric | 104,748 | 7.1% |

### 4.2 Machine Learning (Isolation Forest)

**Algorithm:** Unsupervised anomaly detection based on the principle that anomalies are "few and different."

**Hyperparameters:**

- `contamination = 0.01` (expected 1% anomalies)
- `n_estimators = 100` (number of trees)
- `random_state = 42` (reproducibility)

**Features Used:**

- Age group counts
- Month
- Day of week

### 4.3 Time Series Method (Rolling Window)

**Method:**

1. Aggregate daily totals
2. Calculate rolling mean and std (window=7 days)
3. Flag values outside: μ ± 2σ

**Detected:**

- Spikes: Unusually high activity days
- Drops: Unusually low activity days

### 4.4 Geographic Anomaly Detection

**Method:**

1. Aggregate state totals
2. Compare to median (robust to outliers)
3. Flag >100% above or >50% below median

**Found:**

- Over-performers: UP, Maharashtra, Bihar
- Under-performers: Island territories, small UTs
- Data quality issues: Duplicate state names with different capitalization

---

## 5. Visualization

### 5.1 Static Visualizations (Matplotlib/Seaborn)

- Bar charts: State-wise distribution
- Line charts: Monthly trends
- Pie charts: Age group distribution
- Scatter plots: Anomaly visualization
- Heatmaps: State × Month activity

### 5.2 Interactive Dashboard (Dash/Plotly)

- Dataset selector dropdown
- KPI cards with real-time updates
- Interactive hover tooltips
- Responsive layout

---

## 6. Tools and Technologies

| Purpose               | Tool                  |
| --------------------- | --------------------- |
| Data Processing       | Python, Pandas, NumPy |
| Machine Learning      | Scikit-learn          |
| Static Visualization  | Matplotlib, Seaborn   |
| Interactive Dashboard | Dash, Plotly          |
| Model Persistence     | Joblib                |
| Version Control       | Git, GitHub           |

---

## 7. Reproducibility

### Running the Analysis

```bash
# 1. Preprocess data
python src/data_preprocessing.py

# 2. Run EDA
python src/eda.py

# 3. Run anomaly detection
python src/anomaly_detection.py

# 4. Launch dashboard
python dashboards/dashboard_app.py
```

### Output Files

All outputs are saved to `data/outputs/`:

- CSV reports for each analysis
- PNG visualizations in `figures/`
- Trained models in `models/`

---

## 8. Limitations and Future Work

### Limitations

1. **Data coverage**: Analysis limited to 2025 data
2. **Population normalization**: Raw counts, not per-capita
3. **External factors**: No correlation with external events

### Future Improvements

1. Add population-normalized metrics
2. Integrate with census data for deeper analysis
3. Add predictive forecasting models
4. Expand to multi-year trend analysis
5. Add district-level drill-down

---

## 9. References

1. UIDAI Official Portal - https://uidai.gov.in/
2. Scikit-learn Documentation - https://scikit-learn.org/
3. Plotly Dash Documentation - https://dash.plotly.com/
4. Pandas Documentation - https://pandas.pydata.org/

---

_Document generated: January 2026_
