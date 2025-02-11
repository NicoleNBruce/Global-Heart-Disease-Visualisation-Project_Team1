import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import pycountry_convert as pc
import plotly.express as px
from flask_caching import Cache

# Import functions from external scripts
from choropleth import get_region, get_choropleth_layout, register_choropleth_callbacks
from metric_analysis import get_metric_analysis_layout, register_callbacks_metrics
from correlation_page import get_correlation_layout, register_callbacks_corr
from overview import create_overview_layout, register_callbacks_overview

# Load and preprocess the CSV data (used across multiple pages)
df = pd.read_csv("dataset/FINAL_MERGED_DATA_reimputed.csv")
df.loc[:, 'Region'] = df['Country_Code'].apply(get_region)
corr_data = df.copy()
corr_data = corr_data.drop(columns=['Country_Code'], axis=1)

# Unique values for filters
years = sorted(df['Year'].unique())
countries = sorted(df['Country'].unique())

# Sidebar styling and layout
SIDEBAR_STYLE = {
    "backgroundColor": "#17202A",
    "color": "white",
    "height": "100vh",
    "padding": "20px",
    "width": "280px",
    "position": "fixed",
    "top": 0,
    "left": 0,
    "transition": "all 0.4s ease-in-out",
    "overflow-x": "hidden",
    "boxShadow": "2px 0px 10px rgba(0, 0, 0, 0.2)",
    "zIndex": 2,
}

SIDEBAR_HIDDEN = {**SIDEBAR_STYLE, "left": "-280px"}

CONTENT_STYLE1 = {
    "marginLeft": "330px",
    "marginRight": "20px",
    "padding": "30px",
    "transition": "margin-left 0.4s ease-in-out",
}

CONTENT_STYLE2 = {
    "marginLeft": "50px",
    "marginRight": "20px",
    "padding": "30px",
    "transition": "margin-left 0.4s ease-in-out",
}

TOGGLE_STYLE = {
    "backgroundColor": "#17202A",
    "position": "fixed",
    "top": "15px",
    "left": "300px",
    "color": "white",
    "border": "none",
    "padding": "10px 15px",
    "cursor": "pointer",
    "borderRadius": "5px",
    "transition": "left 0.4s ease-in-out",
}

TOGGLE_STYLE_HIDDEN = {**TOGGLE_STYLE, "left": "20px"}

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP,
                          'https://use.fontawesome.com/releases/v5.15.4/css/all.css'],
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}]
)
app.config.suppress_callback_exceptions = True
server = app.server

# Configure caching
cache = Cache(app.server, config={
    'CACHE_TYPE': 'simple',  # In-memory caching
    'CACHE_DEFAULT_TIMEOUT': 300  # Cache timeout in seconds (5 minutes)
})

# Sidebar with navigation links
sidebar = html.Div(
    [
        html.H2("Global Heart Disease Dashboard",
                className="text-white text-center"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-chart-pie me-2"),
                    html.Span("Dashboard Overview", style={"fontSize": "1.1rem"})],
                    href="/",
                    active="exact",
                    className="text-white"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-globe me-2"),
                    html.Span("Global Health Maps", style={"fontSize": "1.1rem"})],
                    href="/choropleth",
                    active="exact",
                    className="text-white"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-chart-line me-2"),
                    html.Span("Trend Analysis", style={"fontSize": "1.1rem"})],
                    href="/metric-analysis",
                    active="exact",
                    className="text-white"
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-chart-bar me-2"),
                    html.Span("Correlation Analysis", style={"fontSize": "1.08rem"})],
                    href="/correlation",
                    active="exact",
                    className="text-white"
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE,
)

# Layout components
toggle_button = html.Button(
    "☰", id="sidebar-toggle", className="btn btn-primary", style=TOGGLE_STYLE)
content = html.Div(id="page-content", style=CONTENT_STYLE1)

# App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    toggle_button,
    content,
])

# Callback to update page content


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/choropleth":
        return get_choropleth_layout(df)
    elif pathname == "/metric-analysis":
        return get_metric_analysis_layout()
    elif pathname == "/correlation":
        return get_correlation_layout()
    return create_overview_layout()



# Callback to toggle sidebar
@app.callback(
    Output("sidebar", "style"),
    Output("page-content", "style"),
    Output("sidebar-toggle", "style"),
    Input("sidebar-toggle", "n_clicks"),
    prevent_initial_call=True
)
def toggle_sidebar(n):
    if n and n % 2 == 1:
        sidebar_style = SIDEBAR_HIDDEN
        toggle_style = TOGGLE_STYLE_HIDDEN
        content_style = CONTENT_STYLE2
    else:
        sidebar_style = SIDEBAR_STYLE
        toggle_style = TOGGLE_STYLE
        content_style = CONTENT_STYLE1
    return sidebar_style, content_style, toggle_style



# Register callbacks for pages
register_callbacks_overview(app)
register_callbacks_metrics(app)
register_choropleth_callbacks(app, df)
register_callbacks_corr(app, cache)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8503)
