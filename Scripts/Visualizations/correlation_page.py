import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
# import plotly.figure_factory as ff
import plotly.graph_objects as go
import pandas as pd 
import numpy as np

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True



# Sidebar styling
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
    "marginLeft": "300px",
    "marginRight": "20px",
    "padding": "30px",
    "transition": "margin-left 0.4s ease-in-out",
}

CONTENT_STYLE2 = {
    "marginLeft": "20px",
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

# Generate placeholder data
np.random.seed(42)
data = pd.DataFrame(np.random.rand(10, 10), columns=[f"Feature_{i}" for i in range(10)])
data["Heart_Disease_Prevalence"] = np.random.rand(10) * 100

def create_heatmap(selected_features):
    if not selected_features:
        selected_features = data.columns[:5]
    corr_matrix = data[selected_features].corr()
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale="deep")
    return fig

def create_scatterplot(x_feature, y_feature):
    if not x_feature or not y_feature:
        return go.Figure()
    fig = px.scatter(data, x=x_feature, y=y_feature, title=f"Impact of {x_feature} on {y_feature}")
    fig.add_trace(go.Scatter(x=data[x_feature], y=np.poly1d(np.polyfit(data[x_feature], data[y_feature], 1))(data[x_feature]), mode='lines', name='Trendline'))
    return fig




correlation_layout = dbc.Container([

dbc.Col([
    dbc.Col([
        dcc.Dropdown(
            id='heatmap-dropdown',
            options=[{'label': col, 'value': col} for col in data.columns[:-1]],
            value=[data.columns[0], data.columns[1]],
            multi=True,
            placeholder="Select features for heatmap"
        ),
        dcc.Graph(id='heatmap')
    ], width=12),
    dbc.Col([
        dcc.Dropdown(
            id='scatter-dropdown-x',
            options=[{'label': col, 'value': col} for col in data.columns[:-1]],
            placeholder="Select X-axis feature"
        ),
        dcc.Dropdown(
            id='scatter-dropdown-y',
            options=[{'label': col, 'value': col} for col in data.columns[:-1]],
            placeholder="Select Y-axis feature"
        ),
        dcc.Graph(id='scatterplot')
    ], width=12)
])
])




# App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    toggle_button,
    content,
    
])


@app.callback(
    Output('heatmap', 'figure'),
    Input('heatmap-dropdown', 'value')
)
def update_heatmap(selected_features):
    return create_heatmap(selected_features)

@app.callback(
    Output('scatterplot', 'figure'),
    [Input('scatter-dropdown-x', 'value'), Input('scatter-dropdown-y', 'value')]
)
def update_scatterplot(x_feature, y_feature):
    return create_scatterplot(x_feature, y_feature)


# Callback to update page content
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/choropleth":
        return html.Div([
            html.H3("Choropleth Maps Page", style={"textAlign": "center"}),
            # Add choropleth map component here
        ])
    elif pathname == "/time-series":
        return html.Div([
            html.H3("Time Series Page", style={"textAlign": "center"}),
            # Add time series plots here
        ])
    elif pathname == "/correlation":
        return html.Div([
            html.H3("Correlation Analysis Page", style={"textAlign": "center"}),
            # Add correlation visualizations here
            correlation_layout
        ])
    return html.Div([
        html.H3("Overview", style={"textAlign": "center"}),
        # Add homepage elements here
    ])


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


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
