"""
Analytics Router
================

Endpoints for Aadhaar data analytics:
- State summaries
- Monthly trends
- Overall statistics

💡 These endpoints expose your data analysis as consumable APIs.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from api.models.schemas import (
    StateListResponse,
    StateSummary,
    TrendsResponse,
    OverallSummary,
    DataType
)
from api.services.data_service import data_service


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/summary",
    response_model=OverallSummary,
    summary="Get Overall Summary",
    description="Get overall system summary including total records, states, and anomalies."
)
async def get_overall_summary():
    """
    Get overall system summary.
    
    Returns:
    - Total records by data type
    - Number of states
    - Total anomalies detected
    - Date range of data
    """
    summary = data_service.get_overall_summary()
    return OverallSummary(**summary)


@router.get(
    "/states",
    response_model=StateListResponse,
    summary="List All States",
    description="Get summary metrics for all states."
)
async def list_states(
    data_type: DataType = Query(
        default=DataType.enrolment,
        description="Type of data to retrieve"
    )
):
    """
    Get all states with their summary metrics.
    
    Args:
        data_type: enrolment, demographic, or biometric
        
    Returns:
        List of states with total records, age breakdowns, and percentages
    """
    states = data_service.get_all_states(data_type.value)
    
    return StateListResponse(
        total_states=len(states),
        states=[StateSummary(**s) for s in states]
    )


@router.get(
    "/states/{state_name}",
    response_model=StateSummary,
    summary="Get State Details",
    description="Get detailed metrics for a specific state."
)
async def get_state(
    state_name: str,
    data_type: DataType = Query(
        default=DataType.enrolment,
        description="Type of data to retrieve"
    )
):
    """
    Get metrics for a specific state.
    
    Args:
        state_name: Name of the state (case-insensitive)
        data_type: enrolment, demographic, or biometric
        
    Returns:
        State summary with all metrics
        
    Raises:
        404: State not found
    """
    state = data_service.get_state_by_name(state_name, data_type.value)
    
    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"State '{state_name}' not found"
        )
    
    return StateSummary(**state)


@router.get(
    "/trends/monthly",
    response_model=TrendsResponse,
    summary="Get Monthly Trends",
    description="Get monthly trend data for the specified data type."
)
async def get_monthly_trends(
    data_type: DataType = Query(
        default=DataType.enrolment,
        description="Type of data to retrieve"
    )
):
    """
    Get monthly trends.
    
    Args:
        data_type: enrolment, demographic, or biometric
        
    Returns:
        List of monthly data points
    """
    trends = data_service.get_monthly_trends(data_type.value)
    
    return TrendsResponse(
        data_type=data_type.value,
        total_months=len(trends),
        trends=trends
    )
