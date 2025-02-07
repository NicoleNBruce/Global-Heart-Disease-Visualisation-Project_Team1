# -*- coding: utf-8 -*-

# Importing necessary libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import pycountry_convert as pc

# Load dataset
df_main = pd.read_csv('FINAL_MERGED_DATA_reimputed.csv')

# Function to map country to continent


def country_to_continent(country_name):
    try:
        # Get the country code (alpha2) from the country name
        country_code = pc.country_name_to_country_alpha2(country_name)
        # Get the continent code from the country code
        continent_code = pc.country_alpha2_to_continent_code(country_code)
        # Convert continent code to full name
        continent_name = pc.convert_continent_code_to_continent_name(
            continent_code)
        return continent_name
    except:
        return None  # Return None for countries that cannot be mapped


# Add a 'Continent' column to the dataset
df_main['Continent'] = df_main['Country'].apply(country_to_continent)

# Drop rows where 'Continent' is None (if any)
df_main = df_main.dropna(subset=['Continent'])

# Initialize the Dash app with suppressed callback exceptions
app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Sidebar styling and layout (unchanged)
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
        html.H2("Global Heart Disease Dashboard",
                className="text-white text-center"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Overview", href="/", active="exact",
                            className="text-white"),
                dbc.NavLink("Choropleth Maps", href="/choropleth",
                            active="exact", className="text-white"),
                dbc.NavLink("Metric Analysis", href="/risk-factors",
                            active="exact", className="text-white"),
                dbc.NavLink("Correlation Analysis", href="/correlation",
                            active="exact", className="text-white"),
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
    "☰", id="sidebar-toggle", className="btn btn-primary", style=TOGGLE_STYLE
)

content = html.Div(id="page-content", style=CONTENT_STYLE1)

# App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    toggle_button,
    content,
])

# Plot functions (unchanged except for average_mortality_per_country)


def prevalence_rate_by_continent():
    avg_prevalence_by_continent = df_main.groupby(
        'Continent')['PrevalenceRate'].mean().reset_index()
    fig = px.bar(avg_prevalence_by_continent, x='Continent', y='PrevalenceRate',
                 title='Average PrevalenceRate by Continent',
                 labels={'PrevalenceRate': 'Prevalence Rate',
                         'Continent': 'Continent'},
                 template='plotly_white', color='Continent')
    fig.update_layout(title_x=0.5)
    return fig


def risk_factors_by_region(region_type, risk_factor):
    region_column = 'Continent' if region_type == 'Continent' else 'Country'
    avg_risk_by_region = df_main.groupby(
        region_column)[risk_factor].mean().reset_index()
    fig = px.bar(avg_risk_by_region, x=region_column, y=risk_factor,
                 title=f'Average {risk_factor.replace("_", " ")} by {region_type}',
                 labels={risk_factor: risk_factor.replace(
                     '_', ' '), region_column: region_type},
                 template='plotly_white', color=region_column)
    fig.update_layout(title_x=0.5)
    return fig


def age_grouped_mortality_rate():
    other_ages_df = df_main[df_main['Age_Group'] != 'Age-standardized']
    mean_mortality_by_year_age = other_ages_df.groupby(
        ['Year', 'Age_Group'])['MortalityRate'].mean().reset_index()
    fig = px.line(mean_mortality_by_year_age, x='Year', y='MortalityRate', color='Age_Group',
                  title='Global Mortality Rate Over Time',
                  labels={
                      'MortalityRate': 'Mortality Rate (per 100,000)', 'Year': 'Year'},
                  template='plotly_white', line_shape='spline')
    age_groups = mean_mortality_by_year_age['Age_Group'].unique()
    fig.update_layout(
        updatemenus=[dict(
            buttons=[dict(args=[{"visible": [True] * len(fig.data)}], label="All Ages", method="update")] +
                    [dict(args=[{"visible": [trace.name == age_group for trace in fig.data]}],
                          label=age_group, method="update") for age_group in age_groups],
            direction="down", pad={"r": 10, "t": 10}, showactive=True, x=0.1, xanchor="left", y=1.1, yanchor="top"
        )],
        title_x=0.5
    )
    return fig


def country_gender_mortality_rate():
    age_standardized_df = df_main[df_main['Age_Group'] == 'Age-standardized']
    mean_mortality_by_year_country_gender = age_standardized_df.groupby(
        ['Year', 'Country', 'Gender'])['MortalityRate'].mean().reset_index()
    fig = px.line(mean_mortality_by_year_country_gender, x='Year', y='MortalityRate', color='Country', line_dash='Gender',
                  title='Age-Standardized Mortality Rate by Country and Gender',
                  labels={
                      'MortalityRate': 'Mortality Rate (per 100,000)', 'Year': 'Year'},
                  template='plotly_white', line_shape='spline')
    countries = mean_mortality_by_year_country_gender['Country'].unique()
    for trace in fig.data:
        trace.visible = False
    fig.update_layout(
        updatemenus=[dict(
            buttons=[dict(label="Select a Country", method="update", args=[{"visible": [False] * len(fig.data)}])] +
                    [dict(label=country, method="update", args=[{"visible": [(trace.name.startswith(country)) for trace in fig.data]}],
                          execute=True) for country in countries],
            direction="down", pad={"r": 10, "t": 10}, showactive=True, x=0.1, xanchor="left", y=1.15, yanchor="top"
        )],
        title_x=0.5
    )
    return fig


def average_mortality_per_country():
    avg_mortality_per_country = df_main.groupby(['Country_Code', 'Country'])[
        'MortalityRate'].mean().reset_index()
    avg_mortality_per_country = avg_mortality_per_country.sort_values(
        by='MortalityRate', ascending=False)
    fig = px.bar(avg_mortality_per_country,
                 x='Country_Code',
                 y='MortalityRate',
                 title='Average Mortality Rate per Country',
                 template='plotly_white',
                 color='Country_Code',
                 hover_data={'Country_Code': False, 'Country': True})
    fig.update_layout(
        title_x=0.5,
        xaxis=dict(rangeslider=dict(visible=True), type="category"),
        # Adjusted y-axis range
        yaxis=dict(
            range=[0, avg_mortality_per_country['MortalityRate'].max() * 1.1])
    )
    return fig

# Callback to update page content


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/choropleth":
        return html.Div([
            html.H3("Choropleth Maps Page", style={"textAlign": "center"}),
        ])
    elif pathname == "/risk-factors":
        return dbc.Container([
            html.H3("Metric Analysis", style={
                    "textAlign": "center", "marginBottom": "20px"}),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=prevalence_rate_by_continent()),
                        width=12, lg=6, className="mb-4"),
                dbc.Col(dcc.Graph(figure=age_grouped_mortality_rate()),
                        width=12, lg=6, className="mb-4"),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=country_gender_mortality_rate()),
                        width=12, className="mb-4"),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=average_mortality_per_country()),
                        width=12, className="mb-4"),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.Label("Select Region Type:"),
                    dcc.Dropdown(
                        id='region-type-dropdown',
                        options=[
                            {'label': 'Continent', 'value': 'Continent'},
                            {'label': 'Country', 'value': 'Country'}
                        ],
                        value='Continent',
                        clearable=False
                    ),
                    html.Label("Select Risk Factor:"),
                    dcc.Dropdown(
                        id='risk-factor-dropdown',
                        options=[
                            {'label': 'Alcohol Value', 'value': 'Alcohol_Value'},
                            {'label': 'Diabetes Prevalence Rate',
                                'value': 'Diabetes_Prevalence_Rate'},
                            {'label': 'Activity Prevalence Rate',
                                'value': 'Activity_Prevalence_Rate'},
                            {'label': 'Obesity Prevalence Rate',
                                'value': 'Obesity_Prevalence_Rate'}
                        ],
                        value='Alcohol_Value',
                        clearable=False
                    ),
                    dcc.Graph(id='risk-factors-by-region-plot')
                ], width=12, className="mb-4"),
            ], className="mb-4"),
        ], fluid=True)
    elif pathname == "/correlation":
        return html.Div([
            html.H3("Correlation Analysis Page",
                    style={"textAlign": "center"}),
        ])
    return html.Div([
        html.H3("Overview", style={"textAlign": "center"}),
    ])

# Callback to update the risk factors plot


@app.callback(
    Output('risk-factors-by-region-plot', 'figure'),
    Input('region-type-dropdown', 'value'),
    Input('risk-factor-dropdown', 'value')
)
def update_risk_factors_plot(region_type, risk_factor):
    return risk_factors_by_region(region_type, risk_factor)

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
