# UIDAI Societal Insights - Aadhaar Enrolment & Update Analysis

## 🎯 Project Overview
Data analytics project analyzing UIDAI Aadhaar enrolment and update patterns to uncover societal trends, detect anomalies, and provide predictive insights for improved decision-making.

## 📊 Problem Statement
Identify meaningful patterns, trends, and anomalies in Aadhaar enrolment and update data to support UIDAI's system improvements and policy decisions.

## 🛠️ Technology Stack
- **Languages**: Python, SQL
- **Database**: PostgreSQL
- **Libraries**: Pandas, NumPy, Scikit-learn, Plotly
- **Dashboard**: Dash, Power BI
- **Tools**: Jupyter Notebook, Git

## 📁 Project Structure
uidai-societal-insights/
├── data/ # Raw and processed datasets
├── notebooks/ # Jupyter notebooks for analysis
├── src/ # Python source code
├── dashboards/ # Interactive dashboards
├── models/ # Trained ML models
└── docs/ # Documentation


## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/uidai-societal-insights.git
cd uidai-societal-insights

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt


# Create PostgreSQL database
createdb uidai_db

# Run data pipeline
python src/database.py


python src/dashboard_app.py
# Open browser: http://localhost:8050
