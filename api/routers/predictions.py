"""
Risk & Predictions Router
=========================

Endpoints for risk scores and business impact:
- Risk scores by state
- High-risk state list
- Business impact metrics
- Recommendations

💡 These endpoints expose your ML models and business analysis as APIs.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List

from api.models.schemas import (
    RiskScoresResponse,
    RiskScore,
    BusinessImpactResponse,
    FraudAnalysis,
    FraudSeverity,
    ROIAnalysis,
    RecommendationsResponse,
    Recommendation
)
from api.services.data_service import data_service


router = APIRouter(prefix="/risk", tags=["Risk & Predictions"])


@router.get(
    "/scores",
    response_model=RiskScoresResponse,
    summary="Get All Risk Scores",
    description="Get risk scores for all states, sorted by risk level."
)
async def get_all_risk_scores():
    """
    Get risk scores for all states.
    
    Returns all states with:
    - Risk score (0-100)
    - Risk category (HIGH/MEDIUM/LOW)
    - Component breakdown
    """
    scores = data_service.get_risk_scores()
    
    if not scores:
        raise HTTPException(
            status_code=404,
            detail="Risk scores not found. Run business_impact.py first."
        )
    
    high_count = len([s for s in scores if s["risk_category"] == "HIGH"])
    medium_count = len([s for s in scores if s["risk_category"] == "MEDIUM"])
    low_count = len([s for s in scores if s["risk_category"] == "LOW"])
    
    return RiskScoresResponse(
        total_states=len(scores),
        high_risk_count=high_count,
        medium_risk_count=medium_count,
        low_risk_count=low_count,
        scores=[RiskScore(**s) for s in scores]
    )


@router.get(
    "/scores/{state_name}",
    response_model=RiskScore,
    summary="Get State Risk Score",
    description="Get risk score for a specific state."
)
async def get_state_risk(state_name: str):
    """
    Get risk score for a specific state.
    
    Args:
        state_name: Name of the state (case-insensitive)
        
    Returns:
        Risk score details for the state
    """
    score = data_service.get_risk_by_state(state_name)
    
    if not score:
        raise HTTPException(
            status_code=404,
            detail=f"Risk score for '{state_name}' not found"
        )
    
    return RiskScore(**score)


@router.get(
    "/high-risk",
    response_model=RiskScoresResponse,
    summary="Get High-Risk States",
    description="Get only states with HIGH risk category."
)
async def get_high_risk_states():
    """
    Get all high-risk states that need immediate attention.
    
    These are states with risk score >= 70.
    """
    high_risk = data_service.get_high_risk_states()
    
    return RiskScoresResponse(
        total_states=len(high_risk),
        high_risk_count=len(high_risk),
        medium_risk_count=0,
        low_risk_count=0,
        scores=[RiskScore(**s) for s in high_risk]
    )


# =============================================================================
# Business Impact Router
# =============================================================================

business_router = APIRouter(prefix="/business", tags=["Business Impact"])


@business_router.get(
    "/impact",
    response_model=BusinessImpactResponse,
    summary="Get Business Impact",
    description="Get complete business impact analysis including fraud savings and ROI."
)
async def get_business_impact():
    """
    Get business impact metrics.
    
    Returns:
    - Fraud analysis (savings by severity)
    - ROI analysis (return on investment)
    - High-risk state count
    - Total recommendations
    """
    impact = data_service.get_business_impact()
    
    if not impact:
        raise HTTPException(
            status_code=404,
            detail="Business impact data not found. Run business_impact.py first."
        )
    
    # Parse fraud analysis
    fraud = impact.get("fraud_analysis", {})
    fraud_analysis = FraudAnalysis(
        total_anomalies_analyzed=fraud.get("total_anomalies_analyzed", 0),
        high_severity=FraudSeverity(**fraud.get("high_severity", {"count": 0, "potential_savings_inr": 0, "description": "N/A"})),
        medium_severity=FraudSeverity(**fraud.get("medium_severity", {"count": 0, "potential_savings_inr": 0, "description": "N/A"})),
        low_severity=FraudSeverity(**fraud.get("low_severity", {"count": 0, "potential_savings_inr": 0, "description": "N/A"})),
        total_potential_savings_inr=fraud.get("total_potential_savings_inr", 0),
        manual_audit_cost_avoided_inr=fraud.get("manual_audit_cost_avoided_inr", 0),
        total_value_generated_inr=fraud.get("total_value_generated_inr", 0)
    )
    
    # Parse ROI analysis
    roi = impact.get("roi_analysis", {})
    roi_analysis = ROIAnalysis(
        system_cost_annual_inr=roi.get("system_cost_annual_inr", 0),
        total_value_generated_inr=roi.get("total_value_generated_inr", 0),
        net_benefit_inr=roi.get("net_benefit_inr", 0),
        roi_percentage=roi.get("roi_percentage", 0),
        payback_period_months=roi.get("payback_period_months", 0),
        efficiency_multiplier=str(roi.get("efficiency_multiplier", "N/A"))
    )
    
    # Get counts
    risk = impact.get("risk_analysis", {})
    rec = impact.get("recommendations", {})
    
    return BusinessImpactResponse(
        fraud_analysis=fraud_analysis,
        roi_analysis=roi_analysis,
        high_risk_states=risk.get("high_risk_states", 0),
        total_recommendations=rec.get("total_recommendations", 0),
        generated_at=datetime.now()
    )


@business_router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Get Recommendations",
    description="Get actionable recommendations based on risk analysis."
)
async def get_recommendations():
    """
    Get all recommendations for action.
    
    Returns prioritized list of actions:
    - CRITICAL: Immediate attention
    - HIGH: This week
    - INFO: Best practices
    """
    recs = data_service.get_recommendations()
    
    critical = len([r for r in recs if r["priority"] == "CRITICAL"])
    high = len([r for r in recs if r["priority"] == "HIGH"])
    
    return RecommendationsResponse(
        total_recommendations=len(recs),
        critical_count=critical,
        high_priority_count=high,
        recommendations=[Recommendation(**r) for r in recs]
    )
