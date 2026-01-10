import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc
import dash_bootstrap_components as dbc
import random
import numpy as np

# Load locations data
def load_locations():
    df = pd.read_csv("data/locations.csv")
    return df

def reports_layout():
    df = load_locations()

    # Generate dummy visit data for demonstration
    df['visits'] = [random.randint(10, 100) for _ in range(len(df))]

    # Bar Chart: Compare visits per location (top 10) - MOVED TO TOP
    top_locations = df.nlargest(10, 'visits')
    bar_fig = px.bar(
        top_locations, 
        x='name', 
        y='visits', 
        title='Top 10 Locations by Visits',
        color='visits',
        color_continuous_scale='Blues'
    )
    bar_fig.update_layout(
        xaxis_title="Location Name",
        yaxis_title="Number of Visits",
        font=dict(size=12, color='white'),
        title_font=dict(size=16, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white'))
    )
    bar_fig.update_xaxes(tickangle=45)

    # Line Chart: Trends over time (dummy hourly data) - MOVED UP
    hours = list(range(24))
    visits_over_time = [random.randint(50, 200) for _ in hours]
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=hours, 
        y=visits_over_time, 
        mode='lines+markers',
        name='Visits',
        line=dict(color='#17a2b8', width=3),
        marker=dict(size=6, color='#17a2b8')
    ))
    line_fig.update_layout(
        title='Visits Over Time (Hourly)',
        xaxis_title='Hour of Day',
        yaxis_title='Number of Visits',
        font=dict(size=12, color='white'),
        title_font=dict(size=16, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(color='white'), tickfont=dict(color='white'))
    )

    # Pie Chart: Percentage of visits by building - MOVED DOWN
    building_visits = df.groupby('building')['visits'].sum().reset_index()
    pie_fig = px.pie(
        building_visits, 
        values='visits', 
        names='building', 
        title='Visits Distribution by Building',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    pie_fig.update_layout(
        font=dict(size=12, color='white'),
        title_font=dict(size=16, color='white'),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    pie_fig.update_traces(textposition='inside', textinfo='percent+label')

    # Histogram: Distribution of visits - MOVED UP
    hist_fig = px.histogram(
        df, 
        x='visits', 
        title='Distribution of Visits per Location',
        nbins=20,
        color_discrete_sequence=['#28a745']
    )
    hist_fig.update_layout(
        xaxis_title="Number of Visits",
        yaxis_title="Frequency",
        font=dict(size=12, color='white'),
        title_font=dict(size=16, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(color='white'), tickfont=dict(color='white'))
    )

    # Scatter Plot: User activity vs time - MOVED DOWN
    scatter_x = [random.randint(0, 23) for _ in range(100)]
    scatter_y = [random.randint(0, 100) for _ in range(100)]
    scatter_fig = px.scatter(
        x=scatter_x, 
        y=scatter_y, 
        title='User Activity vs Time',
        color=scatter_y,
        color_continuous_scale='RdYlGn'
    )
    scatter_fig.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Activity Level",
        font=dict(size=12, color='white'),
        title_font=dict(size=16, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(color='white'), tickfont=dict(color='white'))
    )

    # Heatmap: Route usage (dummy grid) - MOVED TO BOTTOM
    heatmap_data = np.random.rand(10, 10) * 100
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=heatmap_data, 
        colorscale='Plasma',
        x=[f'Route {i+1}' for i in range(10)],
        y=[f'Destination {i+1}' for i in range(10)]
    ))
    heatmap_fig.update_layout(
        title='Route Usage Heatmap',
        xaxis_title='Origin Routes',
        yaxis_title='Destination Routes',
        font=dict(size=12, color='white'),
        title_font=dict(size=16, color='white'),
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return dbc.Container(fluid=True, children=[
        html.H3("Analytics Dashboard", className="mb-4 text-primary fw-bold"),

        # REARRANGED ORDER: Bar chart first (most important)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top Locations by Visits", className="bg-primary text-white fw-bold"),
                    dbc.CardBody(dcc.Graph(figure=bar_fig, config={'displayModeBar': False}))
                ], className="mb-4 shadow")
            ], md=12)
        ]),

        # Line chart second
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Visits Over Time", className="bg-info text-white fw-bold"),
                    dbc.CardBody(dcc.Graph(figure=line_fig, config={'displayModeBar': False}))
                ], className="mb-4 shadow")
            ], md=12)
        ]),

        # Pie chart and histogram side by side
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Building Distribution", className="bg-success text-white fw-bold"),
                    dbc.CardBody(dcc.Graph(figure=pie_fig, config={'displayModeBar': False}))
                ], className="mb-4 shadow")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Visits Distribution", className="bg-warning text-white fw-bold"),
                    dbc.CardBody(dcc.Graph(figure=hist_fig, config={'displayModeBar': False}))
                ], className="mb-4 shadow")
            ], md=6)
        ]),

        # Scatter plot and heatmap at bottom
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("User Activity Analysis", className="bg-secondary text-white fw-bold"),
                    dbc.CardBody(dcc.Graph(figure=scatter_fig, config={'displayModeBar': False}))
                ], className="mb-4 shadow")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Route Usage Matrix", className="bg-dark text-white fw-bold"),
                    dbc.CardBody(dcc.Graph(figure=heatmap_fig, config={'displayModeBar': False}))
                ], className="mb-4 shadow")
            ], md=6)
        ])
    ])

def register_reports_callbacks(app):
    # No dynamic callbacks needed for now
    pass