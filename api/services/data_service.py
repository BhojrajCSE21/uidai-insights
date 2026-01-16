"""
Data Service Layer for UIDAI Insights API
==========================================

This service provides data access for the API endpoints.
It loads data from CSV files and the business_impact module.

💡 WHY A SERVICE LAYER?
- Separation of concerns (API routes don't directly access data)
- Easier to swap data sources (CSV → Database → Cloud)
- Caching can be added at this layer
- Testability - mock this layer for unit tests
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import OUTPUT_DATA_DIR, PROCESSED_DATA_DIR


class DataService:
    """
    Data access service for UIDAI analytics.
    
    This class provides methods to:
    - Load state summaries
    - Get risk scores
    - Retrieve business impact metrics
    - Access monthly trends
    
    Example:
        service = DataService()
        states = service.get_all_states()
    """
    
    def __init__(self):
        """Initialize the data service with file paths."""
        self.output_dir = OUTPUT_DATA_DIR
        self.processed_dir = PROCESSED_DATA_DIR
        
        # Cache for loaded data
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self._cache_ttl_seconds = 300  # 5 minutes
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache_timestamp:
            return False
        age = (datetime.now() - self._cache_timestamp[key]).total_seconds()
        return age < self._cache_ttl_seconds
    
    def _set_cache(self, key: str, data: Any):
        """Set cache with timestamp."""
        self._cache[key] = data
        self._cache_timestamp[key] = datetime.now()
    
    # =========================================================================
    # STATE SUMMARY METHODS
    # =========================================================================
    
    def get_all_states(self, data_type: str = "enrolment") -> List[Dict]:
        """
        Get summary for all states.
        
        Args:
            data_type: 'enrolment', 'demographic', or 'biometric'
            
        Returns:
            List of state dictionaries with metrics
        """
        cache_key = f"states_{data_type}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        filepath = self.output_dir / f"state_summary_{data_type}.csv"
        
        if not filepath.exists():
            return []
        
        df = pd.read_csv(filepath)
        
        # Standardize column names
        df.columns = df.columns.str.lower()
        
        states = []
        for _, row in df.iterrows():
            state_data = {
                "state": row.get("state", "Unknown"),
                "total_records": int(row.get("total", 0)),
                "age_0_5": int(row.get("age_0_5", 0)),
                "age_5_17": int(row.get("age_5_17", 0)),
                "age_18_plus": int(row.get("age_18_greater", row.get("age_18_plus", 0))),
                "percentage_of_total": float(row.get("percentage", 0))
            }
            states.append(state_data)
        
        self._set_cache(cache_key, states)
        return states
    
    def get_state_by_name(self, state_name: str, data_type: str = "enrolment") -> Optional[Dict]:
        """
        Get summary for a specific state.
        
        Args:
            state_name: Name of the state (case-insensitive)
            data_type: 'enrolment', 'demographic', or 'biometric'
            
        Returns:
            State dictionary or None if not found
        """
        states = self.get_all_states(data_type)
        
        for state in states:
            if state["state"].lower() == state_name.lower():
                return state
        
        return None
    
    # =========================================================================
    # RISK SCORES METHODS
    # =========================================================================
    
    def get_risk_scores(self) -> List[Dict]:
        """
        Get risk scores for all states.
        
        Returns:
            List of risk score dictionaries
        """
        cache_key = "risk_scores"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        filepath = self.output_dir / "risk_scores_by_state.csv"
        
        if not filepath.exists():
            return []
        
        df = pd.read_csv(filepath)
        
        scores = []
        for _, row in df.iterrows():
            score_data = {
                "state": row.get("State", "Unknown"),
                "risk_score": float(row.get("Risk_Score", 0)),
                "risk_category": row.get("Risk_Category", "LOW"),
                "geographic_component": float(row.get("Geographic_Component", 0)),
                "zscore_component": float(row.get("ZScore_Component", 0)),
                "volume_component": float(row.get("Volume_Component", 0)),
                "total_records": int(row.get("Total_Records", 0)),
                "anomaly_flags": int(row.get("Anomaly_Flags", 0))
            }
            scores.append(score_data)
        
        self._set_cache(cache_key, scores)
        return scores
    
    def get_high_risk_states(self) -> List[Dict]:
        """
        Get only high-risk states.
        
        Returns:
            List of high-risk state dictionaries
        """
        all_scores = self.get_risk_scores()
        return [s for s in all_scores if s["risk_category"] == "HIGH"]
    
    def get_risk_by_state(self, state_name: str) -> Optional[Dict]:
        """
        Get risk score for a specific state.
        
        Args:
            state_name: Name of the state (case-insensitive)
            
        Returns:
            Risk score dictionary or None if not found
        """
        scores = self.get_risk_scores()
        
        for score in scores:
            if score["state"].lower() == state_name.lower():
                return score
        
        return None
    
    # =========================================================================
    # BUSINESS IMPACT METHODS
    # =========================================================================
    
    def get_business_impact(self) -> Optional[Dict]:
        """
        Get business impact metrics.
        
        Returns:
            Business impact dictionary or None if not found
        """
        cache_key = "business_impact"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        filepath = self.output_dir / "business_impact_summary.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        self._set_cache(cache_key, data)
        return data
    
    # =========================================================================
    # RECOMMENDATIONS METHODS
    # =========================================================================
    
    def get_recommendations(self) -> List[Dict]:
        """
        Get all recommendations.
        
        Returns:
            List of recommendation dictionaries
        """
        cache_key = "recommendations"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        filepath = self.output_dir / "recommendations.csv"
        
        if not filepath.exists():
            return []
        
        df = pd.read_csv(filepath)
        
        recommendations = []
        for _, row in df.iterrows():
            rec_data = {
                "priority": row.get("Priority", "INFO"),
                "state": row.get("State", "Unknown"),
                "recommendation": row.get("Recommendation", ""),
                "action": row.get("Action", ""),
                "expected_impact": row.get("Expected_Impact", "")
            }
            recommendations.append(rec_data)
        
        self._set_cache(cache_key, recommendations)
        return recommendations
    
    # =========================================================================
    # TRENDS METHODS
    # =========================================================================
    
    def get_monthly_trends(self, data_type: str = "enrolment") -> List[Dict]:
        """
        Get monthly trends data.
        
        Args:
            data_type: 'enrolment', 'demographic', or 'biometric'
            
        Returns:
            List of monthly trend dictionaries
        """
        cache_key = f"trends_{data_type}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        filepath = self.output_dir / f"monthly_trends_{data_type}.csv"
        
        if not filepath.exists():
            return []
        
        df = pd.read_csv(filepath)
        
        trends = []
        for _, row in df.iterrows():
            # Handle different column names
            year_month = row.get("year_month", row.get("month", "Unknown"))
            total = row.get("total", row.get("count", 0))
            
            trend_data = {
                "year_month": str(year_month),
                "total": int(total),
                "data_type": data_type
            }
            trends.append(trend_data)
        
        self._set_cache(cache_key, trends)
        return trends
    
    # =========================================================================
    # SUMMARY METHODS
    # =========================================================================
    
    def get_overall_summary(self) -> Dict:
        """
        Get overall system summary.
        
        Returns:
            Dictionary with overall metrics
        """
        # Get total records per data type
        total_records = {}
        total_states = 0
        
        for data_type in ["enrolment", "demographic", "biometric"]:
            states = self.get_all_states(data_type)
            total = sum(s["total_records"] for s in states)
            total_records[data_type] = total
            total_states = max(total_states, len(states))
        
        # Get business impact for anomaly count
        impact = self.get_business_impact() or {}
        fraud_analysis = impact.get("fraud_analysis", {})
        total_anomalies = fraud_analysis.get("total_anomalies_analyzed", 0)
        
        return {
            "total_records": total_records,
            "total_states": total_states,
            "total_anomalies_detected": total_anomalies,
            "date_range": {
                "start": "2024-01-01",  # Could be computed from data
                "end": "2025-08-31"
            },
            "last_updated": datetime.now()
        }


# Singleton instance for the application
data_service = DataService()
