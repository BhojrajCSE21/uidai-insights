"""
UIDAI Aadhaar Insights Dashboard
================================

This is an interactive web dashboard built with Dash and Plotly.
It visualizes all the analysis we've done on the Aadhaar data.

WHAT IS DASH?
-------------
Dash is a Python framework for building web applications.
It's built on top of:
- Flask (web server)
- React (frontend)
- Plotly (interactive charts)

WHY USE DASH?
-------------
1. Pure Python - no need to learn JavaScript
2. Interactive charts out of the box
3. Easy to deploy (Heroku, AWS, etc.)
4. Looks professional for a resume project!

HOW DASH WORKS:
---------------
1. Layout: Define what components appear on the page (HTML elements, graphs)
2. Callbacks: Define interactivity (when user selects X, update chart Y)
3. Server: Dash runs a Flask server to serve the app

This demonstrates the job requirement:
"Build, maintain and optimize data dashboards and KPI monitoring systems"
"""

# =============================================================================
# IMPORTS
# =============================================================================

import dash
from dash import dcc, html, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import PROCESSED_DATA_DIR, OUTPUT_DATA_DIR

# =============================================================================
# DATA LOADING
# =============================================================================

def load_all_data():
    """
    Load all processed datasets and analysis results.
    
    WHY LOAD AT STARTUP?
    --------------------
    Loading data once at startup is more efficient than loading
    on every user interaction. For larger datasets, you might
    use caching (e.g., @cache decorator) or a database.
    """
    data = {}
    
    # Load processed datasets
    for data_type in ['enrolment', 'demographic', 'biometric']:
        filepath = PROCESSED_DATA_DIR / f'cleaned_{data_type}.csv'
        if filepath.exists():
            data[data_type] = pd.read_csv(filepath, parse_dates=['date'])
    
    # Load state summaries
    for data_type in ['enrolment', 'demographic', 'biometric']:
        filepath = OUTPUT_DATA_DIR / f'state_summary_{data_type}.csv'
        if filepath.exists():
            data[f'{data_type}_state'] = pd.read_csv(filepath)
    
    # Load monthly trends
    for data_type in ['enrolment', 'demographic', 'biometric']:
        filepath = OUTPUT_DATA_DIR / f'monthly_trends_{data_type}.csv'
        if filepath.exists():
            data[f'{data_type}_monthly'] = pd.read_csv(filepath)
    
    # Load anomaly reports
    for data_type in ['enrolment', 'demographic', 'biometric']:
        filepath = OUTPUT_DATA_DIR / f'zscore_outliers_{data_type}.csv'
        if filepath.exists():
            data[f'{data_type}_anomalies'] = pd.read_csv(filepath)
    
    return data

# Load data at startup
print("📊 Loading data for dashboard...")
DATA = load_all_data()
print(f"✅ Loaded {len(DATA)} datasets")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_age_columns(data_type):
    """Get the age column names for each dataset type."""
    if data_type == 'enrolment':
        return ['age_0_5', 'age_5_17', 'age_18_greater']
    elif data_type == 'demographic':
        return ['demo_age_5_17', 'demo_age_17_']
    else:
        return ['bio_age_5_17', 'bio_age_17_']

def calculate_kpis(data_type):
    """
    Calculate Key Performance Indicators (KPIs) for the dashboard header.
    
    WHAT ARE KPIs?
    --------------
    KPIs are measurable values that indicate how well something is performing.
    For Aadhaar data, relevant KPIs include:
    - Total enrolments/updates
    - Number of active states
    - Average daily activity
    - Growth rate
    
    WHY SHOW KPIs?
    --------------
    KPIs give executives a quick overview without reading detailed charts.
    The job description specifically mentions "KPI monitoring systems"!
    """
    if data_type not in DATA:
        return {'total': 0, 'states': 0, 'districts': 0, 'avg_daily': 0}
    
    df = DATA[data_type]
    age_cols = get_age_columns(data_type)
    
    total = df[age_cols].sum().sum()
    states = df['state'].nunique()
    districts = df['district'].nunique()
    days = df['date'].nunique()
    avg_daily = total / days if days > 0 else 0
    
    return {
        'total': total,
        'states': states,
        'districts': districts,
        'avg_daily': avg_daily
    }

# =============================================================================
# CHART CREATION FUNCTIONS
# =============================================================================

def create_state_map(data_type):
    """
    Create a choropleth map showing state-wise distribution.
    
    WHAT IS A CHOROPLETH MAP?
    -------------------------
    A map where regions are colored based on a value.
    Darker colors = higher values, lighter = lower values.
    
    WHY USE MAPS?
    -------------
    - Geographic patterns are immediately visible
    - Executives can quickly spot problem regions
    - More engaging than tables of numbers
    """
    if f'{data_type}_state' not in DATA:
        return go.Figure()
    
    df = DATA[f'{data_type}_state'].copy()
    
    # For Plotly to work, we need to use the 'total' column
    fig = px.bar(
        df.head(15),  # Top 15 states
        x='total',
        y='state' if 'state' in df.columns else df.index,
        orientation='h',
        title=f'Top 15 States - {data_type.title()}',
        labels={'total': 'Total Count', 'state': 'State'},
        color='total',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=500,
        margin=dict(l=150, r=20, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333')
    )
    
    return fig

def create_trend_chart(data_type):
    """
    Create a line chart showing monthly trends.
    
    WHY LINE CHARTS FOR TRENDS?
    ---------------------------
    - Shows progression over time
    - Easy to spot growth/decline
    - Can identify seasonality and anomalies
    """
    if f'{data_type}_monthly' not in DATA:
        return go.Figure()
    
    df = DATA[f'{data_type}_monthly'].copy()
    
    fig = go.Figure()
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['total'],
        mode='lines+markers',
        name='Total',
        line=dict(color='#3498db', width=3),
        marker=dict(size=10)
    ))
    
    # Add fill under the line
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['total'],
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False
    ))
    
    fig.update_layout(
        title=f'Monthly Trend - {data_type.title()}',
        xaxis_title='Month',
        yaxis_title='Total Count',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333')
    )
    
    return fig

def create_age_pie(data_type):
    """
    Create a pie chart showing age distribution.
    
    WHY PIE CHARTS?
    ---------------
    - Perfect for showing parts of a whole
    - Easy to understand percentages at a glance
    - Visually appealing for presentations
    """
    if data_type not in DATA:
        return go.Figure()
    
    df = DATA[data_type]
    age_cols = get_age_columns(data_type)
    
    # Calculate totals for each age group
    totals = [df[col].sum() for col in age_cols]
    
    # Create labels based on data type
    if data_type == 'enrolment':
        labels = ['Children (0-5)', 'Youth (5-17)', 'Adults (18+)']
    else:
        labels = ['Youth (5-17)', 'Adults (17+)']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=totals,
        hole=0.4,  # Makes it a donut chart
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1'][:len(labels)]
    )])
    
    fig.update_layout(
        title=f'Age Distribution - {data_type.title()}',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333')
    )
    
    return fig

def create_anomaly_chart(data_type):
    """
    Create a scatter plot showing anomalies.
    
    WHY SCATTER PLOTS FOR ANOMALIES?
    --------------------------------
    - Shows distribution of all points
    - Outliers are visually obvious
    - Can encode multiple variables (x, y, color, size)
    """
    if f'{data_type}_anomalies' not in DATA:
        return go.Figure()
    
    df = DATA[f'{data_type}_anomalies'].copy()
    
    # Limit to top 100 anomalies for performance
    df = df.nlargest(100, 'zscore')
    
    fig = px.scatter(
        df,
        x='zscore',
        y='total',
        color='state',
        hover_data=['district', 'date'],
        title=f'Top Anomalies by Z-Score - {data_type.title()}'
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333')
    )
    
    return fig

def create_heatmap(data_type):
    """
    Create a heatmap showing activity by state and month.
    
    WHY HEATMAPS?
    -------------
    - Shows 2D patterns (state vs time)
    - Color intensity shows activity level
    - Can spot both temporal and geographic patterns simultaneously
    """
    if data_type not in DATA:
        return go.Figure()
    
    df = DATA[data_type].copy()
    age_cols = get_age_columns(data_type)
    
    # Calculate total and group by state and month
    df['total'] = df[age_cols].sum(axis=1)
    pivot = df.pivot_table(
        values='total',
        index='state',
        columns='month',
        aggfunc='sum'
    )
    
    # Limit to top 20 states for readability
    top_states = df.groupby('state')['total'].sum().nlargest(20).index
    pivot = pivot.loc[pivot.index.isin(top_states)]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Viridis',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=f'Activity Heatmap (State × Month) - {data_type.title()}',
        xaxis_title='Month',
        yaxis_title='State',
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333')
    )
    
    return fig

# =============================================================================
# DASH APP INITIALIZATION
# =============================================================================

"""
CREATING THE DASH APP
---------------------
The Dash app object is the core of our application.
- external_stylesheets: CSS for styling (we use a modern theme)
- suppress_callback_exceptions: Needed when using tabs/dynamic content
"""

# Using a modern CSS framework for better styling
external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap'
]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)

# This is needed for deployment
server = app.server

# =============================================================================
# APP LAYOUT
# =============================================================================

"""
DEFINING THE LAYOUT
-------------------
The layout defines the structure of our dashboard.
Think of it like HTML, but using Python objects.

Key components:
- html.Div: A container (like <div> in HTML)
- html.H1: A heading (like <h1>)
- dcc.Dropdown: An interactive dropdown menu
- dcc.Graph: A Plotly chart
- dcc.Tabs: Tabbed navigation

The layout is hierarchical - components nested inside containers.
"""

# Custom CSS styles
COLORS = {
    'background': '#f8f9fa',
    'card': '#ffffff',
    'primary': '#3498db',
    'secondary': '#2ecc71',
    'text': '#2c3e50',
    'border': '#e9ecef'
}

CARD_STYLE = {
    'backgroundColor': COLORS['card'],
    'borderRadius': '10px',
    'padding': '20px',
    'margin': '10px',
    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
}

KPI_STYLE = {
    'textAlign': 'center',
    'padding': '20px',
    'backgroundColor': COLORS['card'],
    'borderRadius': '10px',
    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
    'margin': '10px'
}

app.layout = html.Div([
    # =========================================================================
    # HEADER SECTION
    # =========================================================================
    html.Div([
        html.H1(
            '🔍 UIDAI Aadhaar Insights Dashboard',
            style={
                'textAlign': 'center',
                'color': COLORS['text'],
                'fontFamily': 'Inter, sans-serif',
                'marginBottom': '10px'
            }
        ),
        html.P(
            'Analyzing Societal Trends in Aadhaar Enrolment and Updates',
            style={
                'textAlign': 'center',
                'color': '#7f8c8d',
                'marginBottom': '20px'
            }
        ),
        
        # Dataset selector
        html.Div([
            html.Label('Select Dataset:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='dataset-selector',
                options=[
                    {'label': '📝 Enrolment Data', 'value': 'enrolment'},
                    {'label': '📋 Demographic Updates', 'value': 'demographic'},
                    {'label': '🔐 Biometric Updates', 'value': 'biometric'}
                ],
                value='enrolment',
                style={'width': '300px', 'display': 'inline-block'}
            )
        ], style={'textAlign': 'center', 'marginBottom': '30px'}),
        
    ], style={'backgroundColor': COLORS['card'], 'padding': '20px', 'marginBottom': '20px'}),
    
    # =========================================================================
    # KPI CARDS SECTION
    # =========================================================================
    html.Div([
        # KPI Card 1: Total Count
        html.Div([
            html.H3(id='kpi-total', style={'color': COLORS['primary'], 'fontSize': '36px'}),
            html.P('Total Records', style={'color': '#7f8c8d'})
        ], style={**KPI_STYLE, 'width': '22%', 'display': 'inline-block'}),
        
        # KPI Card 2: States
        html.Div([
            html.H3(id='kpi-states', style={'color': COLORS['secondary'], 'fontSize': '36px'}),
            html.P('States/UTs', style={'color': '#7f8c8d'})
        ], style={**KPI_STYLE, 'width': '22%', 'display': 'inline-block'}),
        
        # KPI Card 3: Districts
        html.Div([
            html.H3(id='kpi-districts', style={'color': '#e74c3c', 'fontSize': '36px'}),
            html.P('Districts', style={'color': '#7f8c8d'})
        ], style={**KPI_STYLE, 'width': '22%', 'display': 'inline-block'}),
        
        # KPI Card 4: Daily Average
        html.Div([
            html.H3(id='kpi-daily', style={'color': '#9b59b6', 'fontSize': '36px'}),
            html.P('Daily Average', style={'color': '#7f8c8d'})
        ], style={**KPI_STYLE, 'width': '22%', 'display': 'inline-block'}),
        
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    # =========================================================================
    # CHARTS SECTION - ROW 1
    # =========================================================================
    html.Div([
        # State Distribution Chart
        html.Div([
            dcc.Graph(id='state-chart')
        ], style={**CARD_STYLE, 'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Monthly Trend Chart
        html.Div([
            dcc.Graph(id='trend-chart')
        ], style={**CARD_STYLE, 'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ]),
    
    # =========================================================================
    # CHARTS SECTION - ROW 2
    # =========================================================================
    html.Div([
        # Age Distribution Pie Chart
        html.Div([
            dcc.Graph(id='age-pie')
        ], style={**CARD_STYLE, 'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Anomaly Scatter Plot
        html.Div([
            dcc.Graph(id='anomaly-chart')
        ], style={**CARD_STYLE, 'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ]),
    
    # =========================================================================
    # HEATMAP SECTION
    # =========================================================================
    html.Div([
        dcc.Graph(id='heatmap')
    ], style={**CARD_STYLE}),
    
    # =========================================================================
    # FOOTER
    # =========================================================================
    html.Div([
        html.P(
            '📊 Built with Dash & Plotly | Data: UIDAI Aadhaar',
            style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '20px'}
        )
    ])
    
], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'})

# =============================================================================
# CALLBACKS (INTERACTIVITY)
# =============================================================================

"""
CALLBACKS EXPLAINED
-------------------
Callbacks are what make Dash interactive!

Structure:
- @callback decorator specifies:
  - Output: Which component to update and which property
  - Input: Which component triggers the update and which property
  
- The function takes the Input value and returns the new Output value

Example:
When user selects "demographic" from dropdown,
the callback updates all charts to show demographic data.
"""

@callback(
    [
        Output('kpi-total', 'children'),
        Output('kpi-states', 'children'),
        Output('kpi-districts', 'children'),
        Output('kpi-daily', 'children'),
        Output('state-chart', 'figure'),
        Output('trend-chart', 'figure'),
        Output('age-pie', 'figure'),
        Output('anomaly-chart', 'figure'),
        Output('heatmap', 'figure')
    ],
    [Input('dataset-selector', 'value')]
)
def update_dashboard(selected_dataset):
    """
    Update all dashboard components when dataset selection changes.
    
    LOGIC:
    1. Calculate KPIs for selected dataset
    2. Create all charts for selected dataset
    3. Return all updated values
    
    This single callback updates everything at once,
    which is more efficient than multiple separate callbacks.
    """
    # Calculate KPIs
    kpis = calculate_kpis(selected_dataset)
    
    # Format KPI values
    kpi_total = f"{kpis['total']:,.0f}"
    kpi_states = f"{kpis['states']}"
    kpi_districts = f"{kpis['districts']:,}"
    kpi_daily = f"{kpis['avg_daily']:,.0f}"
    
    # Create charts
    state_fig = create_state_map(selected_dataset)
    trend_fig = create_trend_chart(selected_dataset)
    age_fig = create_age_pie(selected_dataset)
    anomaly_fig = create_anomaly_chart(selected_dataset)
    heatmap_fig = create_heatmap(selected_dataset)
    
    return (
        kpi_total, kpi_states, kpi_districts, kpi_daily,
        state_fig, trend_fig, age_fig, anomaly_fig, heatmap_fig
    )

# =============================================================================
# RUN THE APP
# =============================================================================

"""
RUNNING THE DASHBOARD
---------------------
When you run 'python dashboard_app.py', this block executes.

- debug=True: Auto-reloads when you change code, shows errors
- host='0.0.0.0': Accessible from any device on the network
- port=8050: The port to access (http://localhost:8050)

For production, set debug=False!
"""

if __name__ == '__main__':
    print("🚀 Starting UIDAI Insights Dashboard...")
    print("📊 Access at: http://localhost:8050")
    app.run(debug=True, host='0.0.0.0', port=8050)
