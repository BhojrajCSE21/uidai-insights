"""
AI Chat Router
==============

Provides natural language interface to UIDAI analytics.
Now powered by Google Gemini AI for intelligent responses!

This endpoint parses user queries and returns relevant data
in a conversational format.

Example queries:
- "What's the risk in Maharashtra?"
- "Compare UP and Bihar"
- "Which state needs most attention?"
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
import os
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Google Gemini
import google.generativeai as genai

from api.services.data_service import data_service


router = APIRouter(prefix="/chat", tags=["AI Chat"])

# =============================================================================
# GEMINI AI CONFIGURATION
# =============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENABLED = bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_api_key_here")

if GEMINI_ENABLED:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash-latest")
    print("✅ Gemini AI enabled for intelligent chat responses")
else:
    gemini_model = None
    print("⚠️ Gemini AI disabled - using rule-based responses (set GEMINI_API_KEY in .env)")


class GeminiAssistant:
    """
    Gemini-powered AI assistant for UIDAI analytics.
    
    Uses the data context to answer complex questions about:
    - Risk comparisons
    - Trend analysis
    - Recommendations
    - Open-ended queries
    """
    
    @staticmethod
    def get_data_context() -> str:
        """Build context from available data for Gemini."""
        # Get all relevant data
        risk_scores = data_service.get_risk_scores() or []
        business = data_service.get_business_impact() or {}
        recs = data_service.get_recommendations() or []
        summary = data_service.get_overall_summary() or {}
        
        # Format context
        high_risk = [s for s in risk_scores if s['risk_category'] == 'HIGH']
        context = f"""
You are an AI assistant for UIDAI Aadhaar Insights Dashboard. Answer questions using this data:

## RISK SCORES (Top 10):
{json.dumps(risk_scores[:10], indent=2) if risk_scores else 'No data'}

## HIGH RISK STATES:
{json.dumps(high_risk, indent=2) if high_risk else 'None'}

## BUSINESS IMPACT:
- Total Potential Savings: ₹{business.get('fraud_analysis', {}).get('total_potential_savings_inr', 0):,.0f}
- ROI: {business.get('roi_analysis', {}).get('roi_percentage', 0):.1f}%
- Payback Period: {business.get('roi_analysis', {}).get('payback_period_months', 0)} months
- Total Anomalies: {business.get('fraud_analysis', {}).get('total_anomalies_analyzed', 0):,}

## CRITICAL RECOMMENDATIONS:
{json.dumps([r for r in recs if r.get('priority') == 'CRITICAL'][:3], indent=2) if recs else 'None'}

## OVERALL STATS:
- States Analyzed: {summary.get('total_states', 0)}
- Total Records: {sum(summary.get('total_records', {}).values()) if summary.get('total_records') else 0:,}

INSTRUCTIONS:
- Be concise but informative
- Use emojis for visual appeal
- Format numbers with commas for readability
- If comparing states, use the risk scores
- For recommendations, cite the priority level
- Always provide actionable insights
"""
        return context
    
    @staticmethod
    async def ask(question: str) -> str:
        """Ask Gemini a question with data context."""
        if not gemini_model:
            return None
        
        try:
            context = GeminiAssistant.get_data_context()
            prompt = f"{context}\n\nUser Question: {question}\n\nProvide a helpful, concise answer:"
            
            response = gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini error: {e}")
            return None


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ChatRequest(BaseModel):
    """Chat message from user."""
    message: str = Field(..., min_length=1, max_length=500)


class ChatResponse(BaseModel):
    """Chat response with formatted answer and optional data."""
    response: str
    data: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# QUERY PARSER - Understands Natural Language
# =============================================================================

class QueryParser:
    """
    Parses natural language queries and returns structured intents.
    
    This is a rule-based parser that handles common queries.
    Can be extended with LLM for more complex understanding.
    """
    
    # Patterns for different query types
    PATTERNS = {
        'state_risk': [
            r'risk\s+(?:in|for|of)\s+([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+)\s+risk',
            r'how\s+(?:is|risky)\s+([a-zA-Z\s]+)',
        ],
        'high_risk': [
            r'high\s*risk',
            r'top\s*risk',
            r'risky\s*states',
            r'highest\s*risk',
            r'dangerous',
            r'critical\s*states',
        ],
        'all_risk': [
            r'all\s*risk',
            r'all\s*states',
            r'risk\s*scores',
            r'complete\s*risk',
        ],
        'savings': [
            r'savings?',
            r'fraud',
            r'money\s*saved',
            r'potential\s*savings',
        ],
        'roi': [
            r'roi',
            r'return',
            r'investment',
            r'payback',
        ],
        'summary': [
            r'summary',
            r'overview',
            r'total',
            r'overall',
            r'statistics',
        ],
        'recommendations': [
            r'recommend',
            r'action',
            r'what\s*to\s*do',
            r'next\s*steps',
            r'suggestions',
        ],
        'help': [
            r'^help',
            r'what\s*can\s*you',
            r'how\s*to\s*use',
            r'commands',
        ],
        'greeting': [
            r'^hi$',
            r'^hello',
            r'^hey',
        ],
    }
    
    # State name corrections/aliases
    STATE_ALIASES = {
        'up': 'Uttar Pradesh',
        'mp': 'Madhya Pradesh',
        'wb': 'West Bengal',
        'ap': 'Andhra Pradesh',
        'tn': 'Tamil Nadu',
        'mh': 'Maharashtra',
        'maharashtr': 'Maharashtra',
        'bihar': 'Bihar',
        'raj': 'Rajasthan',
        'guj': 'Gujarat',
        'kar': 'Karnataka',
    }
    
    @classmethod
    def parse(cls, message: str) -> tuple[str, dict]:
        """
        Parse message and return (intent, params).
        
        Returns:
            Tuple of (intent_type, parameters_dict)
        """
        msg_lower = message.lower().strip()
        
        # Check greeting first
        for pattern in cls.PATTERNS['greeting']:
            if re.search(pattern, msg_lower):
                return 'greeting', {}
        
        # Check help
        for pattern in cls.PATTERNS['help']:
            if re.search(pattern, msg_lower):
                return 'help', {}
        
        # Check for state-specific risk query
        for pattern in cls.PATTERNS['state_risk']:
            match = re.search(pattern, msg_lower)
            if match:
                state_name = match.group(1).strip()
                # Normalize state name
                state_name = cls.STATE_ALIASES.get(state_name.lower(), state_name.title())
                return 'state_risk', {'state': state_name}
        
        # Check other patterns
        for intent, patterns in cls.PATTERNS.items():
            if intent in ['state_risk', 'greeting', 'help']:
                continue
            for pattern in patterns:
                if re.search(pattern, msg_lower):
                    return intent, {}
        
        # Default - unknown
        return 'unknown', {}


# =============================================================================
# RESPONSE GENERATOR - Creates Natural Language Responses
# =============================================================================

class ResponseGenerator:
    """Generates natural language responses from data."""
    
    @staticmethod
    def format_currency(val: float) -> str:
        """Format currency in lakhs."""
        if val >= 100000:
            return f"₹{val/100000:.1f}L"
        return f"₹{val:,.0f}"
    
    @staticmethod
    def greeting() -> ChatResponse:
        return ChatResponse(
            response="👋 Hello! I'm your UIDAI Insights assistant. Ask me about risk scores, savings, or recommendations!",
            suggestions=[
                "What's the risk in UP?",
                "Show high risk states",
                "What's our ROI?",
            ]
        )
    
    @staticmethod
    def help() -> ChatResponse:
        return ChatResponse(
            response="""🤖 **I can help you with:**

• **Risk queries**: "What's the risk in Maharashtra?", "Show high risk states"
• **Savings**: "What are the potential savings?", "fraud savings"
• **ROI**: "What's our ROI?", "payback period"
• **Recommendations**: "What actions should we take?"
• **Summary**: "Give me an overview"

Just ask naturally! I'll understand. 😊""",
            suggestions=[
                "Risk in Bihar",
                "Total savings",
                "Recommendations",
            ]
        )
    
    @staticmethod
    def state_risk(state: str) -> ChatResponse:
        score = data_service.get_risk_by_state(state)
        
        if not score:
            # Try fuzzy match
            all_scores = data_service.get_risk_scores()
            matches = [s for s in all_scores if state.lower() in s['state'].lower()]
            if matches:
                score = matches[0]
                state = score['state']
            else:
                return ChatResponse(
                    response=f"❌ I couldn't find risk data for '{state}'. Try a different spelling or ask for 'all states'.",
                    suggestions=["Show all states", "High risk states"]
                )
        
        emoji = "🔴" if score['risk_category'] == 'HIGH' else "🟡" if score['risk_category'] == 'MEDIUM' else "🟢"
        
        return ChatResponse(
            response=f"""{emoji} **{score['state']}** has a **{score['risk_category']}** risk score of **{score['risk_score']}/100**

📊 **Breakdown:**
• Volume Component: {score['volume_component']}
• Geographic Component: {score['geographic_component']}
• Z-Score Component: {score['zscore_component']}

📁 Total Records: {score['total_records']:,}
🚩 Anomaly Flags: {score['anomaly_flags']}""",
            data=score,
            suggestions=["Show high risk states", "Recommendations", "Compare with UP"]
        )
    
    @staticmethod
    def high_risk() -> ChatResponse:
        high_risk = data_service.get_high_risk_states()
        
        if not high_risk:
            return ChatResponse(
                response="✅ Great news! No HIGH risk states found.",
                suggestions=["Show all states", "Summary"]
            )
        
        states_list = "\n".join([
            f"• **{s['state']}**: {s['risk_score']}/100 🔴"
            for s in high_risk[:5]
        ])
        
        return ChatResponse(
            response=f"""🚨 **{len(high_risk)} High Risk States** require immediate attention:

{states_list}

These states have risk scores ≥ 70 and need investigation.""",
            data={"high_risk_states": high_risk},
            suggestions=["Risk in " + high_risk[0]['state'] if high_risk else "Summary", "Recommendations"]
        )
    
    @staticmethod
    def all_risk() -> ChatResponse:
        scores = data_service.get_risk_scores()
        
        if not scores:
            return ChatResponse(response="No risk data available.")
        
        high = len([s for s in scores if s['risk_category'] == 'HIGH'])
        medium = len([s for s in scores if s['risk_category'] == 'MEDIUM'])
        low = len([s for s in scores if s['risk_category'] == 'LOW'])
        
        return ChatResponse(
            response=f"""📊 **Risk Score Distribution**

• 🔴 HIGH Risk: {high} states
• 🟡 MEDIUM Risk: {medium} states
• 🟢 LOW Risk: {low} states

**Total:** {len(scores)} states analyzed""",
            data={"distribution": {"high": high, "medium": medium, "low": low}},
            suggestions=["High risk states", "Top state details"]
        )
    
    @staticmethod
    def savings() -> ChatResponse:
        impact = data_service.get_business_impact()
        
        if not impact:
            return ChatResponse(response="Business impact data not available.")
        
        fraud = impact.get('fraud_analysis', {})
        total_savings = fraud.get('total_potential_savings_inr', 0)
        total_value = fraud.get('total_value_generated_inr', 0)
        
        return ChatResponse(
            response=f"""💰 **Potential Fraud Savings**

• **High Severity** (fraud): {ResponseGenerator.format_currency(fraud.get('high_severity', {}).get('potential_savings_inr', 0))}
• **Medium Severity** (quality): {ResponseGenerator.format_currency(fraud.get('medium_severity', {}).get('potential_savings_inr', 0))}
• **Low Severity** (minor): {ResponseGenerator.format_currency(fraud.get('low_severity', {}).get('potential_savings_inr', 0))}

📈 **Total Potential Savings: {ResponseGenerator.format_currency(total_savings)}**
🎯 **Total Value Generated: {ResponseGenerator.format_currency(total_value)}**""",
            data=fraud,
            suggestions=["What's our ROI?", "Recommendations"]
        )
    
    @staticmethod
    def roi() -> ChatResponse:
        impact = data_service.get_business_impact()
        
        if not impact:
            return ChatResponse(response="ROI data not available.")
        
        roi_data = impact.get('roi_analysis', {})
        
        return ChatResponse(
            response=f"""📈 **Return on Investment Analysis**

• **System Cost:** {ResponseGenerator.format_currency(roi_data.get('system_cost_annual_inr', 0))}/year
• **Value Generated:** {ResponseGenerator.format_currency(roi_data.get('total_value_generated_inr', 0))}
• **Net Benefit:** {ResponseGenerator.format_currency(roi_data.get('net_benefit_inr', 0))}

🚀 **ROI: {roi_data.get('roi_percentage', 0):.0f}%**
⏱️ **Payback Period: {roi_data.get('payback_period_months', 0)} months**
⚡ **Efficiency: {roi_data.get('efficiency_multiplier', 'N/A')}**""",
            data=roi_data,
            suggestions=["Savings breakdown", "Recommendations"]
        )
    
    @staticmethod
    def summary() -> ChatResponse:
        summary = data_service.get_overall_summary()
        impact = data_service.get_business_impact()
        scores = data_service.get_risk_scores()
        
        roi = impact.get('roi_analysis', {}).get('roi_percentage', 0) if impact else 0
        high_risk = len([s for s in scores if s['risk_category'] == 'HIGH']) if scores else 0
        
        return ChatResponse(
            response=f"""📊 **UIDAI Insights Summary**

**📁 Data Volume:**
• Enrolment: {summary['total_records'].get('enrolment', 0):,} records
• Demographic: {summary['total_records'].get('demographic', 0):,} records
• Biometric: {summary['total_records'].get('biometric', 0):,} records

**🚨 Risk Status:**
• {summary['total_states']} states analyzed
• {high_risk} HIGH risk states

**💰 Business Impact:**
• ROI: {roi:.0f}%
• Anomalies detected: {summary['total_anomalies_detected']:,}""",
            data=summary,
            suggestions=["High risk states", "Savings", "Recommendations"]
        )
    
    @staticmethod
    def recommendations() -> ChatResponse:
        recs = data_service.get_recommendations()
        
        if not recs:
            return ChatResponse(response="No recommendations available.")
        
        critical = [r for r in recs if r['priority'] == 'CRITICAL']
        high = [r for r in recs if r['priority'] == 'HIGH']
        
        critical_list = "\n".join([f"• **{r['state']}**: {r['action']}" for r in critical[:3]])
        
        return ChatResponse(
            response=f"""✅ **Action Items**

🚨 **Critical ({len(critical)} items):**
{critical_list if critical_list else "None"}

⚠️ **High Priority:** {len(high)} items

Most urgent: Investigate {critical[0]['state'] if critical else 'top risk states'} immediately.""",
            data={"critical_count": len(critical), "high_count": len(high)},
            suggestions=["High risk states", "ROI", "Summary"]
        )
    
    @staticmethod
    def unknown() -> ChatResponse:
        return ChatResponse(
            response="🤔 I'm not sure what you're asking. Try asking about risk scores, savings, ROI, or recommendations!",
            suggestions=["Help", "Summary", "High risk states"]
        )


# =============================================================================
# CHAT ENDPOINT
# =============================================================================

@router.post(
    "",
    response_model=ChatResponse,
    summary="Chat with AI Assistant",
    description="Send a natural language query about UIDAI data. Powered by Gemini AI for complex queries."
)
async def chat(request: ChatRequest):
    """
    Process natural language query and return response.
    
    For simple queries (risk, ROI, savings), uses fast rule-based parsing.
    For complex queries (comparisons, analysis), uses Gemini AI.
    
    Example queries:
    - "What's the risk in Maharashtra?"
    - "Compare UP and Bihar"
    - "Which state needs most attention?"
    """
    # Parse the query
    intent, params = QueryParser.parse(request.message)
    
    # Generate response based on intent
    generators = {
        'greeting': ResponseGenerator.greeting,
        'help': ResponseGenerator.help,
        'state_risk': lambda: ResponseGenerator.state_risk(params.get('state', '')),
        'high_risk': ResponseGenerator.high_risk,
        'all_risk': ResponseGenerator.all_risk,
        'savings': ResponseGenerator.savings,
        'roi': ResponseGenerator.roi,
        'summary': ResponseGenerator.summary,
        'recommendations': ResponseGenerator.recommendations,
    }
    
    # If known intent, use rule-based response (faster)
    if intent != 'unknown' and intent in generators:
        return generators[intent]()
    
    # For unknown queries, try Gemini AI
    if GEMINI_ENABLED:
        gemini_response = await GeminiAssistant.ask(request.message)
        if gemini_response:
            return ChatResponse(
                response=f"🤖 **AI Response:**\n\n{gemini_response}",
                suggestions=["Show high risk states", "Summary", "Recommendations"]
            )
    
    # Fallback to rule-based unknown response
    return ResponseGenerator.unknown()



# =============================================================================
# SUGGESTIONS ENDPOINT
# =============================================================================

@router.get(
    "/suggestions",
    response_model=List[str],
    summary="Get Query Suggestions",
    description="Get suggested queries for the chat interface."
)
async def get_suggestions():
    """Return list of suggested queries."""
    return [
        "What's the risk in UP?",
        "Show high risk states",
        "What are the potential savings?",
        "What's our ROI?",
        "Give me a summary",
        "What actions should we take?",
    ]
