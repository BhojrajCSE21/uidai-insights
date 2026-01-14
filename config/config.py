"""
Configuration settings for UIDAI Analysis Project
"""
import os
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = ROOT_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
OUTPUT_DATA_DIR = DATA_DIR / 'outputs'

# Model directory
MODEL_DIR = ROOT_DIR / 'models'

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DATA_DIR, MODEL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data file paths
ENROLMENT_FILE = RAW_DATA_DIR / 'enrolment_data.csv'
DEMOGRAPHIC_UPDATE_FILE = RAW_DATA_DIR / 'demographic_update_data.csv'
BIOMETRIC_UPDATE_FILE = RAW_DATA_DIR / 'biometric_update_data.csv'

# Processed file paths
CLEANED_ENROLMENT = PROCESSED_DATA_DIR / 'cleaned_enrolment.csv'
CLEANED_UPDATES = PROCESSED_DATA_DIR / 'cleaned_updates.csv'

# Output file paths
STATE_SUMMARY = OUTPUT_DATA_DIR / 'state_summary.csv'
MONTHLY_TRENDS = OUTPUT_DATA_DIR / 'monthly_trends.csv'
ANOMALY_REPORT = OUTPUT_DATA_DIR / 'anomaly_report.csv'

# Model file paths
ANOMALY_MODEL = MODEL_DIR / 'anomaly_detector.pkl'
PREDICTION_MODEL = MODEL_DIR / 'prediction_model.pkl'

# Analysis parameters
AGE_MIN = 0
AGE_MAX = 150
PINCODE_LENGTH = 6

# ML model parameters
ANOMALY_CONTAMINATION = 0.01  # 1% expected anomalies
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Dashboard settings
DASHBOARD_HOST = 'localhost'
DASHBOARD_PORT = 8050
DASHBOARD_DEBUG = True

# Print confirmation (remove the print at end)
# Don't print here as it causes issues
