import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd 
import numpy as np

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

global_styles = {"height": "100vh"}

# Sidebar styling
SIDEBAR_STYLE = {
    "backgroundColor": "#17202A",
    "color": "white",
    "padding": "20px",
    "width": "280px",
    "position": "fixed",
    "top": 0,
    "left": 0,
    "transition": "all 0.4s ease-in-out",
    "overflow-x": "hidden",
    "boxShadow": "2px 0px 10px rgba(0, 0, 0, 0.2)",
    "zIndex": 2,
    "bottom": 0,
    "minHeight": "100vh",
    "display": "flex",
    "flexDirection": "column",
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
    "marginRight": "20px",
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
                dbc.NavLink("Heart Disease Worldwide", href="/choropleth", active="exact", className="text-white"),
                dbc.NavLink("Mortality Rate Analysis", href="/time-series", active="exact", className="text-white"),
                dbc.NavLink("Risk Factor Correlation Analysis", href="/correlation", active="exact", className="text-white"),
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
    locationmode="country names",  # Ensures it matches country names
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

# Load gapminder dataset
df = px.data.gapminder()
np.random.seed(36)
df['heart_disease_prevalence'] = np.random.uniform(5, 65, size=len(df))
df['incidence_rate'] = np.random.uniform(1, 25, size=len(df))  # Synthetic incidence rate
df['mortality_rate'] = np.random.uniform(2, 35, size=len(df))  # Synthetic mortality rate

# Visualization functions for choropleths and bar plots
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

# Generate placeholder data for correlation plot
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

choropleth_layout = dbc.Container([
            html.H1("Heart Disease Worldwide", style={"textAlign": "center", 'marginBottom': '40px'}),
            # html.H5("Choropleth Map", style={"textAlign": "left", 'marginBottom': '10px'}),
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
                value= df['year'].min()

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


correlation_layout = dbc.Container([

dbc.Col([
    html.H5("Feature Correlation Heatmap", style={'textAlign': 'left', 'marginBottom': '10px'}),
    dbc.Col([
        #heading
        dcc.Dropdown(
            id='heatmap-dropdown',
            options=[{'label': col, 'value': col} for col in data.columns[:-1]],
            value=[data.columns[0], data.columns[1]],
            multi=True,
            placeholder="Select features for heatmap"
        ),
        dcc.Graph(id='heatmap')
    ], width=12, style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'marginBottom': '20px'}),
    html.H5("Feature Scatterplot", style={'textAlign': 'left', 'marginBottom': '10px'}),
    dbc.Col([
        #heading
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
    ], width=12, style={'backgroundColor': '#f8f9fa', 'padding': '20px'})
])
])

mortality_layout = dbc.Container([
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
                    style={'flex': '1', 'minWidth': '300px','backgroundColor': '#f8f9fa', 'padding': '20px'}
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
                    style={'flex': '1', 'minWidth': '300px', 'backgroundColor': '#f8f9fa', 'padding': '20px', 'marginLeft':'10px'}
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


# App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    toggle_button,
    content,
    
    
], style=global_styles)

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
    # starting_year = df['year'].min()
    if pathname == "/choropleth":
        return choropleth_layout
    elif pathname == "/time-series":
        return html.Div([
            mortality_layout
        ])
    elif pathname == "/correlation":
        return html.Div([
            html.H1("Risk Factor Correlation Analysis", style={'textAlign': 'center', 'marginBottom': '40px'}),
            correlation_layout
        ])
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