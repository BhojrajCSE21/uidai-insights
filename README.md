# 🔍 UIDAI Aadhaar Insights Dashboard

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-2.0+-green.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Unlocking Societal Trends in Aadhaar Enrolment and Updates**  
> A comprehensive data analytics project analyzing UIDAI Aadhaar data to discover patterns, detect anomalies, and provide actionable insights.

---

## 📊 Problem Statement

Identify meaningful patterns, trends, anomalies, and predictive indicators in UIDAI Aadhaar enrolment and update data. Translate findings into clear insights that support informed decision-making and system improvements.

---

## 🎯 Key Features

| Feature                       | Description                                        |
| ----------------------------- | -------------------------------------------------- |
| **Data Preprocessing**        | Automated pipeline for cleaning 3+ million records |
| **Exploratory Data Analysis** | State-wise, temporal, and demographic analysis     |
| **Anomaly Detection**         | Z-score, Isolation Forest, and time-series methods |
| **Interactive Dashboard**     | Real-time visualizations with Dash/Plotly          |
| **Power BI Export**           | Pre-formatted data for Power BI dashboards         |

---

## 📁 Project Structure

```
uidai-insights/
├── config/
│   └── config.py              # Configuration settings
├── data/
│   ├── raw/                   # Original API data
│   ├── processed/             # Cleaned datasets
│   └── outputs/               # Analysis results & exports
├── dashboards/
│   ├── dashboard_app.py       # Interactive Dash dashboard
│   └── export_for_powerbi.py  # Power BI data export
├── docs/
│   ├── methodology.md         # Detailed methodology
│   └── findings.md            # Key findings
├── models/
│   └── *.pkl                  # Trained ML models
├── src/
│   ├── data_preprocessing.py  # Data cleaning pipeline
│   ├── eda.py                 # Exploratory analysis
│   └── anomaly_detection.py   # ML anomaly detection
├── requirements.txt
└── README.md
```

---

## �️ Technology Stack

| Category             | Technologies                                    |
| -------------------- | ----------------------------------------------- |
| **Languages**        | Python 3.10+, SQL                               |
| **Data Processing**  | Pandas, NumPy                                   |
| **Machine Learning** | Scikit-learn (Isolation Forest, StandardScaler) |
| **Visualization**    | Plotly, Matplotlib, Seaborn                     |
| **Dashboard**        | Dash (Python), Power BI                         |
| **Database**         | PostgreSQL                                      |

---

## 📊 Datasets Used

| Dataset         | Records | Columns                                                           | Description               |
| --------------- | ------- | ----------------------------------------------------------------- | ------------------------- |
| **Enrolment**   | 1M+     | date, state, district, pincode, age_0_5, age_5_17, age_18_greater | New Aadhaar registrations |
| **Demographic** | 2M+     | date, state, district, pincode, demo*age_5_17, demo_age_17*       | Demographic updates       |
| **Biometric**   | 1.8M+   | date, state, district, pincode, bio*age_5_17, bio_age_17*         | Biometric updates         |

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/BhojrajCSE21/uidai-insights.git
cd uidai-insights
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Data Pipeline

```bash
# Preprocess raw data
python src/data_preprocessing.py

# Run exploratory analysis
python src/eda.py

# Run anomaly detection
python src/anomaly_detection.py
```

### 4. Launch Dashboard

```bash
cd dashboards
python dashboard_app.py
# Open browser: http://localhost:8050
```

---

## 📈 Key Findings

### Enrolment Insights

- 🏆 **Top State**: Uttar Pradesh (702K+ enrolments)
- 👶 **68.5% are children (0-5 years)** - Child enrolment programs are highly effective
- 📈 **Major spike in August 2025** - Possible government campaign effect

### Demographic Updates

- 🏆 **Top State**: Uttar Pradesh (3.6M+ updates)
- 👥 **89.5% are adults** - Adults update their details more frequently
- ⚠️ **Data quality issue**: Inconsistent state name capitalization detected

### Biometric Updates

- 🏆 **Top State**: Maharashtra (3.9M+ updates)
- 📊 **50-50 split** between youth and adults
- 📈 **January 2025 spike**: 8M+ updates in single month

### Anomalies Detected

- **81,966 statistical outliers** across all datasets
- Geographic anomalies reveal underperforming regions
- Temporal spikes correlate with potential policy changes

---

## 🔍 Methodology

### 1. Data Preprocessing

- Date parsing and validation
- Pincode standardization (6 digits)
- Age range validation (0-150)
- Duplicate removal
- Feature engineering (year, month, quarter extraction)

### 2. Exploratory Data Analysis

- Descriptive statistics
- State-wise distribution analysis
- Temporal trend analysis
- Age demographic breakdown

### 3. Anomaly Detection

| Method               | Purpose                              |
| -------------------- | ------------------------------------ | --- | ---- |
| **Z-Score**          | Statistical outliers (               | Z   | > 3) |
| **Isolation Forest** | ML-based multi-dimensional anomalies |
| **Rolling Window**   | Time-series spikes and drops         |
| **Geographic**       | Under/over-performing regions        |

### 4. Visualization

- Interactive Dash dashboard with:
  - KPI cards
  - State distribution charts
  - Monthly trend analysis
  - Age demographic pie charts
  - Anomaly scatter plots
  - State×Month heatmaps

---

## 📊 Dashboard Preview

The interactive dashboard includes:

- **Dataset Selector**: Switch between Enrolment, Demographic, Biometric
- **KPI Cards**: Total records, states, districts, daily average
- **Charts**: Bar charts, line charts, pie charts, heatmaps
- **Anomaly Visualization**: Scatter plots highlighting outliers

---

## 📂 Output Files

```
data/outputs/
├── figures/                    # Generated visualizations
├── state_summary_*.csv         # State-wise aggregations
├── monthly_trends_*.csv        # Monthly trend data
├── zscore_outliers_*.csv       # Z-score anomalies
├── isolation_forest_*.csv      # ML anomalies
├── temporal_anomalies_*.csv    # Time-series anomalies
└── powerbi_exports/            # Power BI ready data
    ├── fact_aadhaar_transactions.csv
    ├── dim_states.csv
    ├── dim_date.csv
    └── anomalies.csv
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Bhojraj** - [GitHub](https://github.com/BhojrajCSE21)

---

## 🙏 Acknowledgments

- UIDAI for providing the Aadhaar datasets
- Plotly/Dash community for excellent visualization tools
- Scikit-learn for machine learning algorithms
