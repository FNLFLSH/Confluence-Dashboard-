import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
from datetime import datetime
import os
from src.parser_json import load_and_parse_confluence_data
from src.utils import standardize_fields, add_quarter_column

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Confluence Report Dashboard"

# Global variable to store parsed data
parsed_data = None

def load_data():
    """Load and parse the Confluence data"""
    global parsed_data
    try:
        data_file = "data/report_confluence.json"
        if os.path.exists(data_file):
            parsed_data = load_and_parse_confluence_data(data_file)
            parsed_data = standardize_fields(parsed_data)
            parsed_data = add_quarter_column(parsed_data)
            return True
        else:
            print(f"Data file not found: {data_file}")
            return False
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

# Load data on startup
data_loaded = load_data()

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("📊 Confluence Report Dashboard", 
                    className="text-primary mb-3 text-center"),
            html.P("Interactive visualization of release reports and module changes", 
                   className="text-muted text-center mb-4")
        ])
    ]),
    
    # Status Alert
    dbc.Row([
        dbc.Col([
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                f"Data Status: {'✅ Loaded' if data_loaded and parsed_data else '❌ Not Available'}"
            ], color="success" if data_loaded and parsed_data else "danger", className="mb-4")
        ])
    ]),
    
    # Main Content
    dbc.Row([
        # Left Column - Charts
        dbc.Col([
            # Summary Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="total-releases", className="card-title text-center"),
                            html.P("Total Releases", className="card-text text-center text-muted")
                        ])
                    ], className="mb-3")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="total-modules", className="card-title text-center"),
                            html.P("Active Modules", className="card-text text-center text-muted")
                        ])
                    ], className="mb-3")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="total-quarters", className="card-title text-center"),
                            html.P("Time Periods", className="card-text text-center text-muted")
                        ])
                    ], className="mb-3")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="new-releases", className="card-title text-center"),
                            html.P("New Releases", className="card-text text-center text-muted")
                        ])
                    ], className="mb-3")
                ], width=3)
            ]),
            
            # Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📈 Releases by Category"),
                        dbc.CardBody([
                            dcc.Graph(id="category-chart")
                        ])
                    ], className="mb-3")
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📅 Releases Over Time"),
                        dbc.CardBody([
                            dcc.Graph(id="timeline-chart")
                        ])
                    ], className="mb-3")
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🏗️ Top Modules by Activity"),
                        dbc.CardBody([
                            dcc.Graph(id="modules-chart")
                        ])
                    ], className="mb-3")
                ])
            ])
        ], width=8),
        
        # Right Column - Filters and Details
        dbc.Col([
            # Filters
            dbc.Card([
                dbc.CardHeader("🔍 Filters"),
                dbc.CardBody([
                    html.Label("Category:"),
                    dcc.Dropdown(
                        id="category-filter",
                        options=[
                            {"label": "All Categories", "value": "all"},
                            {"label": "Bug Fix", "value": "Bug Fix"},
                            {"label": "Enhancement", "value": "Enhancement"},
                            {"label": "New Feature", "value": "New Feature"},
                            {"label": "Other", "value": "Other"}
                        ],
                        value="all",
                        className="mb-3"
                    ),
                    
                    html.Label("Quarter:"),
                    dcc.Dropdown(
                        id="quarter-filter",
                        options=[{"label": "All Quarters", "value": "all"}],
                        value="all",
                        className="mb-3"
                    ),
                    
                    html.Label("Module:"),
                    dcc.Dropdown(
                        id="module-filter",
                        options=[{"label": "All Modules", "value": "all"}],
                        value="all",
                        className="mb-3"
                    ),
                    
                    dbc.Button("Reset Filters", id="reset-filters", 
                              color="secondary", className="w-100")
                ])
            ], className="mb-3"),
            
            # Data Table
            dbc.Card([
                dbc.CardHeader("📋 Release Details"),
                dbc.CardBody([
                    html.Div(id="data-table")
                ])
            ])
        ], width=4)
    ])
], fluid=True)

# Callbacks
@callback(
    [Output("total-releases", "children"),
     Output("total-modules", "children"),
     Output("total-quarters", "children"),
     Output("new-releases", "children"),
     Output("category-filter", "options"),
     Output("quarter-filter", "options"),
     Output("module-filter", "options")],
    [Input("reset-filters", "n_clicks")]
)
def update_summary_stats(n_clicks):
    if not parsed_data:
        return "N/A", "N/A", "N/A", "N/A", [], [], []
    
    df = pd.DataFrame(parsed_data)
    
    # Calculate stats
    total_releases = len(df)
    total_modules = len(df['ModuleName'].dropna().unique())
    total_quarters = len(df['Quarter'].dropna().unique())
    new_releases = len(df[df.get('NewRelease', False) == True])
    
    # Filter options
    categories = [{"label": "All Categories", "value": "all"}] + [
        {"label": cat, "value": cat} for cat in df['Category'].unique() if cat
    ]
    
    quarters = [{"label": "All Quarters", "value": "all"}] + [
        {"label": q, "value": q} for q in sorted(df['Quarter'].dropna().unique())
    ]
    
    modules = [{"label": "All Modules", "value": "all"}] + [
        {"label": mod, "value": mod} for mod in sorted(df['ModuleName'].dropna().unique()) if mod
    ]
    
    return total_releases, total_modules, total_quarters, new_releases, categories, quarters, modules

@callback(
    Output("category-chart", "figure"),
    [Input("category-filter", "value"),
     Input("quarter-filter", "value"),
     Input("module-filter", "value")]
)
def update_category_chart(category, quarter, module):
    if not parsed_data:
        return go.Figure()
    
    df = pd.DataFrame(parsed_data)
    
    # Apply filters
    if category != "all":
        df = df[df['Category'] == category]
    if quarter != "all":
        df = df[df['Quarter'] == quarter]
    if module != "all":
        df = df[df['ModuleName'] == module]
    
    # Count by category
    category_counts = df['Category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="Distribution by Category",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

@callback(
    Output("timeline-chart", "figure"),
    [Input("category-filter", "value"),
     Input("quarter-filter", "value"),
     Input("module-filter", "value")]
)
def update_timeline_chart(category, quarter, module):
    if not parsed_data:
        return go.Figure()
    
    df = pd.DataFrame(parsed_data)
    
    # Apply filters
    if category != "all":
        df = df[df['Category'] == category]
    if quarter != "all":
        df = df[df['Quarter'] == quarter]
    if module != "all":
        df = df[df['ModuleName'] == module]
    
    # Count by quarter
    quarter_counts = df['Quarter'].value_counts().sort_index()
    
    fig = px.bar(
        x=quarter_counts.index,
        y=quarter_counts.values,
        title="Releases by Quarter",
        labels={'x': 'Quarter', 'y': 'Number of Releases'}
    )
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

@callback(
    Output("modules-chart", "figure"),
    [Input("category-filter", "value"),
     Input("quarter-filter", "value"),
     Input("module-filter", "value")]
)
def update_modules_chart(category, quarter, module):
    if not parsed_data:
        return go.Figure()
    
    df = pd.DataFrame(parsed_data)
    
    # Apply filters
    if category != "all":
        df = df[df['Category'] == category]
    if quarter != "all":
        df = df[df['Quarter'] == quarter]
    if module != "all":
        df = df[df['ModuleName'] == module]
    
    # Count by module (top 10)
    module_counts = df['ModuleName'].value_counts().head(10)
    
    fig = px.bar(
        x=module_counts.values,
        y=module_counts.index,
        orientation='h',
        title="Top Modules by Activity",
        labels={'x': 'Number of Releases', 'y': 'Module Name'}
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

@callback(
    Output("data-table", "children"),
    [Input("category-filter", "value"),
     Input("quarter-filter", "value"),
     Input("module-filter", "value")]
)
def update_data_table(category, quarter, module):
    if not parsed_data:
        return html.P("No data available")
    
    df = pd.DataFrame(parsed_data)
    
    # Apply filters
    if category != "all":
        df = df[df['Category'] == category]
    if quarter != "all":
        df = df[df['Quarter'] == quarter]
    if module != "all":
        df = df[df['ModuleName'] == module]
    
    # Limit to 20 rows for performance
    df_display = df.head(20)
    
    # Create table
    table_rows = []
    for _, row in df_display.iterrows():
        table_rows.append(
            html.Tr([
                html.Td(row.get('Title', '')[:50] + '...' if len(str(row.get('Title', ''))) > 50 else row.get('Title', '')),
                html.Td(row.get('Category', '')),
                html.Td(row.get('Date', '')),
                html.Td(row.get('ModuleName', '')[:30] + '...' if len(str(row.get('ModuleName', ''))) > 30 else row.get('ModuleName', ''))
            ])
        )
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Title"),
                html.Th("Category"),
                html.Th("Date"),
                html.Th("Module")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, bordered=True, hover=True, size="sm")
    
    return table

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050) 