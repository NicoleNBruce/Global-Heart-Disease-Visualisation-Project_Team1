import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

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
                dbc.NavLink("Mortality Plots", href="/time-series", active="exact", className="text-white"),  # Changed here
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
app.layout = html.Div([dcc.Location(id="url"), sidebar, toggle_button, content])


# Callback to update page content
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/choropleth":
        return html.Div([html.H3("Choropleth Maps Page", style={"textAlign": "center"})])
    elif pathname == "/time-series":
        return html.Div([
            html.H1("Mortality Rate Analysis Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),  # This title can also be updated if needed

            html.Div([
                dcc.Graph(
                    id='global-mortality',
                    figure={
                        'data': [
                            go.Scatter(
                                x=[1, 2, 3, 4, 5],
                                y=[10, 11, 12, 13, 14],
                                mode='lines',
                                name='Global Mortality'
                            )
                        ],
                        'layout': go.Layout(
                            title='Global Mortality Rate Over Time',
                            xaxis={'title': 'Year'},
                            yaxis={'title': 'Mortality Rate'},
                        )
                    },
                    style={'flex': '1', 'minWidth': '300px'}
                ),
                dcc.Graph(
                    id='global-age-std-mortality',
                    figure={
                        'data': [
                            go.Scatter(
                                x=[1, 2, 3, 4, 5],
                                y=[3, 4, 5, 6, 7],
                                mode='lines',
                                name='Age-Standardized Mortality'
                            )
                        ],
                        'layout': go.Layout(
                            title='Global Age-Standardized Mortality Over Time',
                            xaxis={'title': 'Year'},
                            yaxis={'title': 'Mortality Rate'},
                        )
                    },
                    style={'flex': '1', 'minWidth': '300px'}
                ),
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}),

            html.Div([dcc.Graph(
                id='mortality-country-gender',
                figure={
                    'data': [
                        go.Scatter(
                            x=[1, 2, 3, 4, 5],
                            y=[1, 2, 3, 4, 5],
                            mode='lines',
                            name='Mortality by Gender Over Time'
                        )
                    ],
                    'layout': go.Layout(
                        title='Mortality by Gender Over Time',
                        xaxis={'title': 'Year'},
                        yaxis={'title': 'Mortality Rate'},
                    )
                },
                style={'width': '100%'}
            )], style={'marginTop': '20px'}),

            html.Div([dcc.Graph(
                id='avg-mortality-country',
                figure={
                    'data': [
                        go.Bar(
                            x=["USA", "China", "India", "Germany", "Brazil"],
                            y=[5, 6, 7, 8, 9],
                            name="Average Mortality by Country"
                        )
                    ],
                    'layout': go.Layout(
                        title='Average Mortality by Country',
                        xaxis={'title': 'Country'},
                        yaxis={'title': 'Mortality Rate'},
                    )
                },
                style={'width': '100%'}
            )], style={'marginTop': '20px'})
        ])
    elif pathname == "/correlation":
        return html.Div([html.H3("Correlation Analysis Page", style={"textAlign": "center"})])
    return html.Div([html.H3("Overview", style={"textAlign": "center"})])


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
