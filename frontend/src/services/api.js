/**
 * API Service for UIDAI Insights
 * Connects to FastAPI backend
 */

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// API functions
export const apiService = {
  // Health check
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Analytics
  getSummary: async () => {
    const response = await api.get('/analytics/summary');
    return response.data;
  },

  getStates: async (dataType = 'enrolment') => {
    const response = await api.get('/analytics/states', {
      params: { data_type: dataType }
    });
    return response.data;
  },

  getStateByName: async (stateName, dataType = 'enrolment') => {
    const response = await api.get(`/analytics/states/${encodeURIComponent(stateName)}`, {
      params: { data_type: dataType }
    });
    return response.data;
  },

  getMonthlyTrends: async (dataType = 'enrolment') => {
    const response = await api.get('/analytics/trends/monthly', {
      params: { data_type: dataType }
    });
    return response.data;
  },

  // Risk
  getRiskScores: async () => {
    const response = await api.get('/risk/scores');
    return response.data;
  },

  getHighRiskStates: async () => {
    const response = await api.get('/risk/high-risk');
    return response.data;
  },

  getStateRisk: async (stateName) => {
    const response = await api.get(`/risk/scores/${encodeURIComponent(stateName)}`);
    return response.data;
  },

  // Business
  getBusinessImpact: async () => {
    const response = await api.get('/business/impact');
    return response.data;
  },

  getRecommendations: async () => {
    const response = await api.get('/business/recommendations');
    return response.data;
  }
};

export default apiService;
