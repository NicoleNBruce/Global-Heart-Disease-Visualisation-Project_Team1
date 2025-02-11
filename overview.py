import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
    ]
)
app.config.suppress_callback_exceptions = True

# Load data
df = pd.read_csv('dataset/FINAL_MERGED_DATA_reimputed.csv')


def create_overview_layout():
    # Calculate key statistics from the dataset
    total_countries = df['Country'].nunique()
    latest_year = df['Year'].max()
    avg_mortality = df[df['Gender'] == 'Both']['MortalityRate'].mean()
    avg_prevalence = df[df['Gender'] == 'Both']['PrevalenceRate'].mean()

    return html.Div([
        # Header Section
        dbc.Row([
            dbc.Col([
                html.H3(
                    [
                        "Global Heart Disease ",
                        "Analytics Overview ",
                        # html.Span("📊")
                    ],
                    className="text-center fw-semibold mb-3 p-2 bg-light rounded shadow-sm",
                    style={
                        "fontSize": "clamp(1.5rem, 4vw, 2.5rem)",
                        "marginBottom": "0.5rem",
                        "color": "#2C3E50",
                        "fontFamily": "'Segoe UI', system-ui, -apple-system, sans-serif",
                        "lineHeight": "1.4"
                    }
                ),
                html.P(
                    "Welcome to the Global Heart Disease Dashboard. This interactive platform provides comprehensive "
                    "insights into heart disease patterns and trends across different regions, demographics, and "
                    "economic indicators.",
                    className="lead text-center mb-4"
                ),
            ])
        ]),

        # Key Statistics Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{total_countries}",
                                className="text-center mb-2", style={ "color":"navy"}),
                        html.P("Total Countries and Territories Analyzed for Data",
                               className="text-center text-muted"),
                    ])
                ], className="mb-4 text-center")
            ], width=3),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{latest_year}",
                                className="text-center mb-2", style={ "color":"navy"}),
                        html.P("Most Recent Year for which data is available",
                               className="text-center text-muted"),
                               
                    ])
                ], className="mb-4")
            ], width=3),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{avg_mortality:,.0f}",
                                className="text-center mb-2", style={ "color":"navy"}),
                        html.P("Average Mortality Rate (per 100,000 people)",
                               className="text-center text-muted"),
                    ])
                ], className="mb-4")
            ], width=3),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{avg_prevalence:,.0f}",
                                className="text-center mb-2", style={ "color":"navy"}),
                        html.P("Average Prevalence Rate (per 100,000 people)",
                               className="text-center text-muted"),
                    ])
                ], className="mb-4")
            ], width=3),
        ],),

        # Quick Insights Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H4("Quick Insights", className="mb-0 text-center")),
                    dbc.CardBody([
                        # First row - Table and Mortality Trend
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H5("Top 8 Countries by Selected Metric",
                                            style={'textAlign': 'center', 'marginBottom': '20px'}),
                                    dbc.Row([
                                        dbc.Col([
                                            html.Label('Select Metric:'),
                                            dcc.Dropdown(
                                                id='metric-selector',
                                                options=[
                                                    {'label': 'Prevalence Rate',
                                                        'value': 'PrevalenceRate'},
                                                    {'label': 'Incidence Rate',
                                                        'value': 'IncidenceRate'},
                                                    {'label': 'Mortality Rate',
                                                        'value': 'MortalityRate'}
                                                ],
                                                value='MortalityRate',
                                                style={'marginBottom': '20px'}
                                            ),
                                        ], width=6),
                                        dbc.Col([
                                            html.Label('Select Year:'),
                                            dcc.Dropdown(
                                                id='year-selector',
                                                options=[{'label': str(year), 'value': year}
                                                         for year in sorted(df['Year'].unique(), reverse=True)],
                                                value=df['Year'].max(),
                                                style={'marginBottom': '20px'}
                                            ),
                                        ], width=6),
                                    ]),
                                    dash_table.DataTable(
                                        id='top-countries-table',
                                        style_table={
                                            'height': '350px', 'overflowY': 'auto'},
                                        style_cell={
                                            'textAlign': 'left', 'padding': '10px', 'backgroundColor': 'white', 'fontFamily': 'Open Sans, sans-serif'},
                                        style_header={
                                            'backgroundColor': '#f8f9fa', 'fontWeight': 'bold', 'fontFamily': 'Open Sans, sans-serif'},
                                        style_data_conditional=[
                                            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}]
                                    )
                                ], style={'height': '100%'})
                            ], width=6),
                            dbc.Col([
                                html.H5("Global GDP & Health Expenditure Trend",
                                        style={'textAlign': 'center', 'marginBottom': '20px'}),
                                dcc.Graph(
                                    figure=px.line(
                                        df[df['Gender'] == 'Both'].groupby('Year')[
                                            ['GDP',
                                                'Health_Expenditure (% of GDP)']
                                        ].mean().reset_index(),
                                        x='Year',
                                        y=['GDP',
                                            'Health_Expenditure (% of GDP)']
                                    ).update_layout(
                                        yaxis=dict(
                                            title='GDP ($)'),
                                        yaxis2=dict(
                                            title='Health Expenditure (% of GDP)',
                                            overlaying='y',
                                            side='right'
                                        ),
                                        legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="right",
                                            x=1
                                        ),
                                        height=450,
                                        margin={'t': 20}
                                    ).for_each_trace(
                                        lambda t: t.update(
                                            yaxis='y2') if t.name == 'Health_Expenditure (% of GDP)' else t
                                    )
                                )
                            ], width=6),
                        ], className="mb-4", style={'alignItems': 'stretch'}),

                        # Second row - Full width Life Expectancy & Health Expenditure
                        dbc.Row([
                            dbc.Col([
                                html.H5("Life Expectancy & Health Expenditure Trends",
                                        style={'textAlign': 'center', 'marginBottom': '20px'}),
                                dcc.Graph(
                                    figure=px.line(
                                        df[df['Gender'] == 'Both'].groupby('Year')[
                                            ['Life_Expectancy',
                                                'Health_Expenditure (% of GDP)']
                                        ].mean().reset_index(),
                                        x='Year',
                                        y=['Life_Expectancy',
                                            'Health_Expenditure (% of GDP)']
                                    ).update_layout(
                                        yaxis=dict(
                                            title='Life Expectancy (years)'),
                                        yaxis2=dict(
                                            title='Health Expenditure (% of GDP)',
                                            overlaying='y',
                                            side='right'
                                        ),
                                        legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="right",
                                            x=1
                                        ),
                                        height=500  # Made the graph taller
                                    ).for_each_trace(
                                        lambda t: t.update(
                                            yaxis='y2') if t.name == 'Health_Expenditure (% of GDP)' else t
                                    )
                                )
                            ], width=12),  # Changed to full width
                        ]),

                        # Third row - Risk Factor Cards
                        dbc.Row([
                            dbc.Col([
                                html.H5("Global Risk Factors (Latest Year Average)",
                                        style={'textAlign': 'center', 'marginBottom': '20px'}),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardBody([
                                                html.H4(f"{df[df['Year'] == df['Year'].max()]['Obesity_Prevalence_Rate'].mean():,.1f}%",
                                                        className="text-center mb-2", style={ "color":"navy"}),
                                                html.P("Obesity Prevalence Rate",
                                                       className="text-center text-muted"),
                                            ])
                                        ], className="mb-4")
                                    ], width=3),
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardBody([
                                                html.H4(f"{df[df['Year'] == df['Year'].max()]['Activity_Prevalence_Rate'].mean():,.1f}%",
                                                        className="text-center mb-2", style={ "color":"navy"}),
                                                html.P("Physical Activity Rate",
                                                       className="text-center text-muted"),
                                            ])
                                        ], className="mb-4")
                                    ], width=3),
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardBody([
                                                html.H4(f"{df[df['Year'] == df['Year'].max()]['Alcohol_Value'].mean():,.1f}",
                                                        className="text-center mb-2", style={ "color":"navy"}),
                                                html.P("Alcohol Consumption (Liters per capita)",
                                                       className="text-center text-muted"),
                                            ])
                                        ], className="mb-4")
                                    ], width=3),
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardBody([
                                                html.H4(f"{df[df['Year'] == df['Year'].max()]['Diabetes_Prevalence_Rate'].mean():,.1f}%",
                                                        className="text-center mb-2", style={ "color":"navy"}),
                                                html.P("Diabetes Prevalence Rate",
                                                       className="text-center text-muted"),
                                            ])
                                        ], className="mb-4")
                                    ], width=3),
                                ])
                            ])
                        ]),
                    ])
                ], className="mb-4")
            ])
        ]),

        # Data Sources and Info Section
        # Data Sources and Info Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H4("Data Sources", className="mb-0 text-center")),
                    dbc.CardBody([
                        html.P([
                            "This dashboard synthesizes data from multiple authoritative global health and economic databases: ",
                            html.Ul([
                                html.Li([
                                    html.Span("WHO Global Health Observatory ", style={"fontWeight": "bold"}),
                                    "- Comprehensive risk factor and economic data"
                                ]),
                                html.Li([
                                    html.Span("Global Burden of Disease (GBD) Study ", style={"fontWeight": "bold"}),
                                    "- Primary source for health metrics and disease indicators"
                                ]),
                                html.Li([
                                    html.Span("NCD Risk Factor Collaboration (NCD-RisC) ", style={"fontWeight": "bold"}),
                                    "- Comprehensive risk factor data"
                                ]),
                                html.Li([
                                    html.Span("Gapminder Dataset ", style={"fontWeight": "bold"}),
                                    "- Global demographic and health trends"
                                ]),
                                html.Li([
                                    html.Span("World Bank ", style={"fontWeight": "bold"}),
                                    "- GDP per capita (PPP) economic indicators"
                                ])
                            ], className="list-unstyled text-muted")
                        ], className="text-center"),
                        html.P([
                            "By integrating these diverse sources, we offer a comprehensive, multi-dimensional ",
                            "analysis of global heart disease patterns, economic contexts, and health trends."
                        ], className="text-center text-muted mt-3")
                    ])
                ], className="mb-4")
            ])
        ]),
    ])


def register_callbacks_overview(app):

    @app.callback(
        Output("world-map", "figure"),
        Input("year-selector", "value")
    )
    def update_map(selected_year):
        filtered_df = df[df['Year'] == selected_year]
        return px.choropleth(
            filtered_df,
            locations='Country_Code',  # Updated to use Country_Code instead of Country
            color='PrevalenceRate',
            title=f'Heart Disease Prevalence ({selected_year})',
            color_continuous_scale='Reds'
        )



    @app.callback(
        Output('top-countries-table', 'data'),
        Output('top-countries-table', 'columns'),
        Input('metric-selector', 'value'),
        Input('year-selector', 'value')
    )
    def update_top_countries(selected_metric, selected_year):
        # Filter data for the selected year and 'Both' gender
        filtered_df = df[
            (df['Year'] == selected_year) &
            (df['Gender'] == 'Both')
        ]

        # Get top 8 countries
        top_8_df = filtered_df.nlargest(7, selected_metric)[
            ['Country', selected_metric]]

        # Round the metric values to 2 decimal places
        top_8_df[selected_metric] = top_8_df[selected_metric].round(2)

        # Add rank column
        top_8_df.insert(0, 'Rank', range(1, 8))

        # Create columns for the table
        columns = [
            {'name': 'Rank', 'id': 'Rank'},
            {'name': 'Country', 'id': 'Country'},
            {'name': f'{selected_metric} (per 100,000)', 'id': selected_metric}
        ]

        # Convert DataFrame to dict for the table
        data = top_8_df.to_dict('records')

        return data, columns


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
