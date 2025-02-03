import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_table
import plotly.express as px
import pandas as pd
import numpy as np

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

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



# Dummy data
ov_data = pd.DataFrame({
    "Country": ["Ghana", "Chad", "Nigeria", "India", "USA"],
    "Prevalence Rate": [30, 25, 22, 20, 18],
    "Mortality Rate": [150, 140, 130, 120, 110],
    "Incidence Rate": [50, 45, 42, 40, 38],
    "Trend": ["down", "up", "down", "up", "down"],
    "ISO Code": ["GHA", "TCD", "NGA", "IND", "USA"]  # ISO codes for the map
})

# Overview Choropleth map setup
fig = px.choropleth(
    ov_data, 
    locations="Country", 
    locationmode="country names",  
    color_discrete_sequence=["#17202A"],  # All highlighted countries in blue
    title="Countries with Available Data"
)



def create_info_card(title, description, color="#17202A"):
    return dbc.Col([
        html.Div([
            html.H6(title, style={"color": "white", "marginBottom": "3px", "textAlign": "left",}),
            html.P(description, style={
                   "color": "white", 
                   "fontSize": "30px",
                    "margin": "0",
                    "fontWeight": "bold",
                    "paddingBottom": "16px"
                       })
        ], style={
            "backgroundColor": color,
            "padding": "10px 20px",
            "borderRadius": "5px",
            "height": "100px",
            "display": "flex",
            "flexDirection": "column",
            
        })
    ], xs=12, sm=12, md=4)


sidebar = html.Div([
    html.H2("Global Heart Disease Dashboard",
            className="text-white text-center"),
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("Overview", href="/", active="exact",
                    className="text-white"),
        dbc.NavLink("Choropleth Maps", href="/choropleth",
                    active="exact", className="text-white"),
        dbc.NavLink("Time Series", href="/time-series",
                    active="exact", className="text-white"),
        dbc.NavLink("Correlation Analysis", href="/correlation",
                    active="exact", className="text-white"),
    ], vertical=True, pills=True),
], id="sidebar", style=SIDEBAR_STYLE)

toggle_button = html.Button(
    "☰", id="sidebar-toggle", className="btn btn-primary", style=TOGGLE_STYLE)

content = html.Div(id="page-content", style=CONTENT_STYLE1)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    toggle_button,
    content,
])


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/choropleth":
        return html.Div([html.H3("Choropleth Maps Page", style={"textAlign": "center"})])
    elif pathname == "/time-series":
        return html.Div([html.H3("Time Series Page", style={"textAlign": "center"})])
    elif pathname == "/correlation":
        return html.Div([html.H3("Correlation Analysis Page", style={"textAlign": "center"})])
    # Overview page with responsive layout
    return html.Div([
        html.H1("Overview", style={
                "textAlign": "center", "marginBottom": "30px"}),

        # Info cards row
        dbc.Row([
            create_info_card("Global Average Prevalence (Age standardised)",
                             "24%"),
            create_info_card("Global Average Incidence (Per 100,000)", "13%"),
            create_info_card("Global Average Mortality (Per 100,000)", "120 ")
        ], className="mb-4 g-3", style={"margin": "0 auto", "width": "90%"}),
     
        dbc.Row([
            html.Div([
                dcc.Graph(id="choropleth-map", figure=fig)
            ], style={"width": "50%",}),

            html.Div([
                dcc.Dropdown(
                    id="metric-dropdown-ov",
                    options=[
                        {"label": "Prevalence Rate", "value": "Prevalence Rate"},
                        {"label": "Mortality Rate", "value": "Mortality Rate"},
                        {"label": "Incidence Rate", "value": "Incidence Rate"}
                    ],
                    value="Prevalence Rate",
                    clearable=False
                ),
                dash_table.DataTable(
                    id="top5-table",
                    columns=[
                        {"name": "Country", "id": "Country"},
                        {"name": "Rate", "id": "Rate"},
                        {"name": "Trend", "id": "Trend", "presentation": "markdown"}
                    ],
                    style_table={"margin-top": "10px"},
                    style_cell={"textAlign": "left"},
                )
            ], style={"width": "50%", "display": "inline-block", "marginTop": "20px"})
        ], style={"backgroundColor": "#f8f9fa", "padding": "10px"}),
        # Trends graph
            dbc.Col([
                html.H5("Trends Over Time", style={"textAlign": "center", "marginTop": "16px"}),
                dcc.Graph(
                    figure=px.line(
                        pd.DataFrame({
                            'year': range(1990, 2021),
                            'Alcohol': np.random.normal(50, 10, 31),
                            'Diabetes': 20 + 10 * np.sin(np.linspace(0, 2 * np.pi, 31)),
                            'Obesity': 30 + 10 * np.sin(np.linspace(0, 2 * np.pi, 31)),
                            'Physical Inactivity': np.random.normal(50, 35, 20).mean()
                        }).melt(id_vars='year', var_name='variable', value_name='value'),
                        x='year',
                        y='value',
                        color='variable',
                        labels={'value': 'Average Rate'},
                        height=250
                    ).update_layout(
                        margin=dict(l=0, r=0, t=30, b=0),
                        legend_title="Risk Factors",
                        xaxis_title="Year",
                        yaxis_title="Prevalence Rate"
                    )
                )
            ], style={"backgroundColor": "#f8f9fa", "padding": "20px", "marginTop": "10px"})
    ])

@app.callback(
    Output("top5-table", "data"),
    Input("metric-dropdown-ov", "value")
)
def update_table(selected_metric):

    sorted_data = ov_data.sort_values(by=selected_metric, ascending=False).head(5)
    sorted_data["Rate"] = sorted_data[selected_metric]
    sorted_data["Trend"] = sorted_data["Trend"].apply(
        lambda x: "⬆️ Upward trend" if x == "up" else "⬇️ Downward trend"
    )
    return sorted_data[["Country", "Rate", "Trend"]].to_dict("records")


@app.callback(
    [Output("sidebar", "style"),
     Output("page-content", "style"),
     Output("sidebar-toggle", "style")],
    Input("sidebar-toggle", "n_clicks"),
    prevent_initial_call=True
)
def toggle_sidebar(n):
    if n and n % 2 == 1:
        return SIDEBAR_HIDDEN, CONTENT_STYLE2, TOGGLE_STYLE_HIDDEN
    return SIDEBAR_STYLE, CONTENT_STYLE1, TOGGLE_STYLE


if __name__ == "__main__":
    app.run_server(debug=True)
