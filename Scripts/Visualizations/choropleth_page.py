import dash
from dash import dcc, html
from dash import callback_context
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np

# Load gapminder dataset
df = px.data.gapminder()
np.random.seed(36)
df['heart_disease_prevalence'] = np.random.uniform(5, 65, size=len(df))
df['incidence_rate'] = np.random.uniform(1, 25, size=len(df))  # Synthetic incidence rate
df['mortality_rate'] = np.random.uniform(2, 35, size=len(df))  # Synthetic mortality rate

# Visualization functions
def create_choropleth(year, continent, metric):
    filtered_df = df[df['year'] == year]
    if continent != "All":
        filtered_df = filtered_df[filtered_df['continent'] == continent]

    fig = px.choropleth(
        filtered_df,
        locations='iso_alpha',
        color=metric,
        hover_name='country',
        color_continuous_scale='Blues',
        title=f'Global {metric.replace("_", " ").title()} ({year}) - {continent if continent != "All" else "All Continents"}'
    )
    fig.update_layout(height=600, coloraxis_colorbar=dict(title=f"{metric.replace('_', ' ').title()} (%)"))
    return fig

def create_barplot(year, continent, metric):
    filtered_df = df[df['year'] == year]
    if continent != "All":
        filtered_df = filtered_df[filtered_df['continent'] == continent]

    top_5_countries = (
        filtered_df.nlargest(5, metric)[['country', metric]]
    )
    fig = px.bar(
        top_5_countries,
        y=metric,
        x='country',
        color='country',
        title=f'Top 5 Countries with Highest {metric.replace("_", " ").title()} ({year}) - {continent if continent != "All" else "All Continents"}'
    )
    fig.update_layout(
        height=500,
        yaxis_title='',
        xaxis_title=f'{metric.replace("_", " ").title()} (%)',
        bargap=0.2,
        bargroupgap=0.1
    )
    return fig

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

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

# Sidebar with navigation links
sidebar = html.Div(
    [
        html.H2("Global Heart Disease Dashboard", className="text-white text-center"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Overview", href="/", active="exact", className="text-white"),
                dbc.NavLink("Choropleth Maps", href="/choropleth", active="exact", className="text-white"),
                dbc.NavLink("Time Series", href="/time-series", active="exact", className="text-white"),
                dbc.NavLink("Correlation Analysis", href="/correlation", active="exact", className="text-white"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE,
)

# Collapsible sidebar button
toggle_button = html.Button(
    "☰", id="sidebar-toggle", className="btn btn-primary",
    style=TOGGLE_STYLE
)

content = html.Div(
    id="page-content",
    style=CONTENT_STYLE1
)

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
    starting_year = df['year'].min()
    if pathname == "/choropleth":
        return html.Div([
            html.H3("Choropleth Map", style={"textAlign": "center"}),
            html.Label("Select Continent", className="fw-bold"),
            dcc.Dropdown(
                id='continent-dropdown',
                options=[{'label': 'All', 'value': 'All'}] +
                        [{'label': cont, 'value': cont} for cont in df['continent'].unique()],
                value='All',
                clearable=False,
                style={"marginBottom": "20px"}
            ),
            html.Label("Select Year", className="fw-bold"),
            dcc.Slider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                step=5,
                marks={str(year): str(year) for year in df['year'].unique()},
                value=starting_year
            ),
            html.Label("Select Metric", className="fw-bold"),
            dcc.Dropdown(
                id='metric-dropdown',
                options=[
                    {'label': 'Heart Disease Prevalence', 'value': 'heart_disease_prevalence'},
                    {'label': 'Incidence Rate', 'value': 'incidence_rate'},
                    {'label': 'Mortality Rate', 'value': 'mortality_rate'}
                ],
                value='heart_disease_prevalence',
                clearable=False,
                style={"marginBottom": "20px"}
            ),
            dcc.Graph(id='choropleth-map'),
            html.Hr(),
            dcc.Graph(id='bar-plot')
        ])
    elif pathname == "/time-series":
        return html.Div([
            html.H3("Time Series Page", style={"textAlign": "center"}),
        ])
    elif pathname == "/correlation":
        return html.Div([
            html.H3("Correlation Analysis Page", style={"textAlign": "center"}),
        ])
    return html.Div([
        html.H3("Overview", style={"textAlign": "center"}),
    ])

@app.callback(
    Output("choropleth-map", "figure"),
    Output("bar-plot", "figure"),
    Input("year-slider", "value"),
    Input("continent-dropdown", "value"),
    Input("metric-dropdown", "value"),
    prevent_initial_call="initial_loading"
)
def update_choropleth_and_barplot(year, continent, metric):
    if year is None or continent is None or metric is None:
        year = df['year'].min()  # Default to the minimum year
        continent = 'All'  # Default to 'All' continents
        metric = 'heart_disease_prevalence'  # Default to heart disease prevalence
    return create_choropleth(year, continent, metric), create_barplot(year, continent, metric)


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

if __name__ == "__main__":
    app.run_server(debug=True)
