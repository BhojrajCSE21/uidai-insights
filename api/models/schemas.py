"""
Pydantic Schemas for UIDAI Insights API
========================================

These are the request/response models that define the API contract.
FastAPI uses these for:
1. Automatic validation of requests
2. Auto-generated OpenAPI/Swagger documentation
3. Type hints and IDE support

💡 WHY PYDANTIC?
- Industry standard for Python APIs
- Automatic data validation
- Great Swagger docs generation
- JP Morgan and Big 4 expect this pattern
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class RiskCategory(str, Enum):
    """Risk level categories for states."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DataType(str, Enum):
    """Types of Aadhaar data."""
    enrolment = "enrolment"
    demographic = "demographic"
    biometric = "biometric"


# =============================================================================
# RESPONSE MODELS - Analytics
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., example="healthy")
    timestamp: datetime
    version: str = Field(..., example="1.0.0")
    environment: str = Field(..., example="development")


class StateSummary(BaseModel):
    """Summary metrics for a single state."""
    state: str = Field(..., example="Uttar Pradesh")
    total_records: int = Field(..., example=702047)
    age_0_5: int = Field(default=0, example=364276)
    age_5_17: int = Field(default=0, example=327696)
    age_18_plus: int = Field(default=0, example=10075)
    percentage_of_total: float = Field(..., example=16.49)


class StateListResponse(BaseModel):
    """Response containing list of states."""
    total_states: int
    states: List[StateSummary]


class MonthlyTrend(BaseModel):
    """Monthly trend data point."""
    year_month: str = Field(..., example="2025-01")
    total: int = Field(..., example=1523456)
    data_type: str = Field(..., example="enrolment")


class TrendsResponse(BaseModel):
    """Response containing monthly trends."""
    data_type: str
    total_months: int
    trends: List[MonthlyTrend]


class OverallSummary(BaseModel):
    """Overall system summary."""
    total_records: Dict[str, int] = Field(
        ..., 
        example={"enrolment": 4256789, "demographic": 2345678, "biometric": 3456789}
    )
    total_states: int = Field(..., example=36)
    total_anomalies_detected: int = Field(..., example=81966)
    date_range: Dict[str, str] = Field(
        ..., 
        example={"start": "2024-01-01", "end": "2025-08-31"}
    )
    last_updated: datetime


# =============================================================================
# RESPONSE MODELS - Risk Scores
# =============================================================================

class RiskScore(BaseModel):
    """Risk score for a single state."""
    state: str = Field(..., example="Uttar Pradesh")
    risk_score: float = Field(..., ge=0, le=100, example=100.0)
    risk_category: RiskCategory = Field(..., example="HIGH")
    geographic_component: float = Field(..., example=40.0)
    zscore_component: float = Field(..., example=30.0)
    volume_component: float = Field(..., example=30.0)
    total_records: int = Field(..., example=702047)
    anomaly_flags: int = Field(..., example=5)


class RiskScoresResponse(BaseModel):
    """Response containing risk scores."""
    total_states: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    scores: List[RiskScore]


# =============================================================================
# RESPONSE MODELS - Business Impact
# =============================================================================

class FraudSeverity(BaseModel):
    """Fraud analysis by severity level."""
    count: int
    potential_savings_inr: float
    description: str


class FraudAnalysis(BaseModel):
    """Fraud savings breakdown."""
    total_anomalies_analyzed: int
    high_severity: FraudSeverity
    medium_severity: FraudSeverity
    low_severity: FraudSeverity
    total_potential_savings_inr: float
    manual_audit_cost_avoided_inr: float
    total_value_generated_inr: float


class ROIAnalysis(BaseModel):
    """ROI metrics."""
    system_cost_annual_inr: float
    total_value_generated_inr: float
    net_benefit_inr: float
    roi_percentage: float
    payback_period_months: float
    efficiency_multiplier: str


class BusinessImpactResponse(BaseModel):
    """Complete business impact summary."""
    fraud_analysis: FraudAnalysis
    roi_analysis: ROIAnalysis
    high_risk_states: int
    total_recommendations: int
    generated_at: datetime


# =============================================================================
# RESPONSE MODELS - Recommendations
# =============================================================================

class Recommendation(BaseModel):
    """Single recommendation item."""
    priority: str = Field(..., example="CRITICAL")
    state: str = Field(..., example="Uttar Pradesh")
    recommendation: str = Field(..., example="Immediate audit required")
    action: str = Field(..., example="Deploy investigation team")
    expected_impact: str = Field(..., example="Prevent potential fraud")


class RecommendationsResponse(BaseModel):
    """Response containing recommendations."""
    total_recommendations: int
    critical_count: int
    high_priority_count: int
    recommendations: List[Recommendation]


# =============================================================================
# REQUEST MODELS
# =============================================================================

class ForecastRequest(BaseModel):
    """Request for forecasting endpoint."""
    state: Optional[str] = Field(None, example="Maharashtra")
    data_type: DataType = Field(default=DataType.enrolment)
    periods: int = Field(default=6, ge=1, le=24, example=6)


class ForecastResponse(BaseModel):
    """Forecast response."""
    state: Optional[str]
    data_type: str
    periods_forecasted: int
    forecast: List[Dict[str, Any]]
    confidence_interval: float = Field(..., example=0.95)


# =============================================================================
# ERROR MODELS
# =============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str
    status_code: int
    timestamp: datetime
