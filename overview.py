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
        dbc.icons.FONT_AWESOME,
        "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
    ]
)
app.config.suppress_callback_exceptions = True

# Load data
df = pd.read_parquet('dataset/FINAL_MERGED_DATA_reimputed.parquet', engine="pyarrow")


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
                    ],
                    className="text-center fw-semibold mb-3 p-3 rounded shadow-sm",
                    style={
                        "fontSize": "clamp(1.7rem, 4vw, 2.7rem)",
                        "marginBottom": "1rem",
                        "background": "linear-gradient(135deg, #17202A 0%, #2C3E50 100%)",
                        "color": "white",
                        "fontFamily": "'Segoe UI', system-ui, -apple-system, sans-serif",
                        "lineHeight": "1.4"
                    }
                ),
            ])
        ]),

        # Key Statistics Cards
        dbc.Row([

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{total_countries}",
                                className="text-center mb-2", style={"color": "navy", "fontSize": "clamp(1.1rem, 4vw, 2rem)",
                                                                     "fontWeight": "bold"}),
                        html.P("Total Countries and Territories Analyzed for Data",
                               className="text-center text-muted"),
                    ])
                ], className="mb-4 shadow-sm text-center")
            ], xs=12, sm=6, md=6, lg=3),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{latest_year}",
                                className="text-center mb-2", style={"color": "navy","fontSize": "clamp(1.1rem, 4vw, "
                                          "2rem)", "fontWeight": "bold"}),
                        html.P("Most Recent Year for which data is available",
                               className="text-center text-muted"),

                    ])
                ], className="shadow-sm mb-4")
            ], xs=12, sm=6, md=6, lg=3),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{avg_mortality:,.0f}",
                                className="text-center mb-2", style={"color": "navy","fontSize": "clamp(1.1rem, 4vw, 2rem)",
                                                                     "fontWeight": "bold"}),
                        html.P("Average Mortality Rate (per 100,000 people)",
                               className="text-center text-muted"),
                    ])
                ], className="shadow-sm mb-4")
            ], xs=12, sm=6, md=6, lg=3),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{avg_prevalence:,.0f}",
                                className="text-center mb-2", style={"color": "navy","fontSize": "clamp(1.1rem, 4vw, 2rem)",
                                                                     "fontWeight": "bold"}),
                        html.P("Average Prevalence Rate (per 100,000 people)",
                               className="text-center text-muted"),
                    ])
                ], className="mb-4 shadow-sm")
            ], xs=12, sm=6, md=6, lg=3),

        ],),

        # Quick Insights Section
        dbc.Row([
            dbc.Col([
                html.H2("Quick Insights", className="text-center fw-semibold mb-3 p-2 bg-light rounded shadow-sm "
                                                    "border")
            ], width=12),

            # Top Countries Table and GDP & Health Expenditure side by side
            dbc.Row([
                # Top Countries Table Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H5("Top 8 Countries by Selected Metric", className="text-center")
                        ),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label('Select Metric:'),
                                    dcc.Dropdown(
                                        id='metric-selector',
                                        options=[
                                            {'label': 'Prevalence Rate', 'value': 'PrevalenceRate'},
                                            {'label': 'Incidence Rate', 'value': 'IncidenceRate'},
                                            {'label': 'Mortality Rate', 'value': 'MortalityRate'}
                                        ],
                                        value='MortalityRate',
                                        style={'marginBottom': '38px'}
                                    ),
                                ], xs=12, md=6),
                                dbc.Col([
                                    html.Label('Select Year:'),
                                    dcc.Dropdown(
                                        id='year-selector',
                                        options=[{'label': str(year), 'value': year}
                                                 for year in sorted(df['Year'].unique(), reverse=True)],
                                        value=df['Year'].max(),
                                        style={'marginBottom': '20px'}
                                    ),
                                ], xs=12, md=6),
                            ]),
                            dash_table.DataTable(
                                id='top-countries-table',
                                style_table={'height': '350px', 'overflowY': 'auto'},
                                style_cell={
                                    'textAlign': 'left',
                                    'padding': '10px',
                                    'backgroundColor': 'white',
                                    'fontFamily': 'Open Sans, sans-serif'
                                },
                                style_header={
                                    'backgroundColor': '#f8f9fa',
                                    'fontWeight': 'bold',
                                    'fontFamily': 'Open Sans, sans-serif'
                                },
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}
                                ]
                            )
                        ])
                    ], className="mb-4 shadow-sm border d-flex flex-column")
                ], xs=12, lg=6),

                # GDP & Health Expenditure Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H5("Global GDP & Health Expenditure Trend", className="text-center")
                        ),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=px.line(
                                    df[df['Gender'] == 'Both'].groupby('Year')[
                                        ['GDP', 'Health_Expenditure (% of GDP)']
                                    ].mean().reset_index(),
                                    x='Year',
                                    y=['GDP', 'Health_Expenditure (% of GDP)']
                                ).update_layout(
                                    yaxis=dict(title='GDP ($)'),
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
                                    # height=550,
                                    # margin={'t': 20}
                                ).for_each_trace(
                                    lambda t: t.update(
                                        yaxis='y2') if t.name == 'Health_Expenditure (% of GDP)' else t
                                )
                            )
                        ])
                    ], className="mb-4 shadow-sm border h-80")
                ], xs=12, lg=6),
            ]),

            # Life Expectancy Card (full width)
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H5("Life Expectancy & Health Expenditure Trends", className="text-center")
                        ),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=px.line(
                                    df[df['Gender'] == 'Both'].groupby('Year')[
                                        ['Life_Expectancy', 'Health_Expenditure (% of GDP)']
                                    ].mean().reset_index(),
                                    x='Year',
                                    y=['Life_Expectancy', 'Health_Expenditure (% of GDP)']
                                ).update_layout(
                                    yaxis=dict(title='Life Expectancy (years)'),
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
                                    height=500
                                ).for_each_trace(
                                    lambda t: t.update(
                                        yaxis='y2') if t.name == 'Health_Expenditure (% of GDP)' else t
                                )
                            )
                        ])
                    ], className="mb-4 shadow-sm border h-80")
                ], width=12),
            ]),

            # Risk Factors Card (full width)
            dbc.Row([
                dbc.Col([
                    dbc.Col([
                        html.H2("Average Global Risk Factors (2023)",
                                className="text-center fw-semibold mb-3 p-2 bg-light rounded shadow-sm border")
                    ], width=12),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div([
                                        html.H4(
                                            f"{df[df['Year'] == df['Year'].max()]['Obesity_Prevalence_Rate'].mean():,.1f}%",
                                            style={"color": "navy", "display": "inline"}
                                        ),
                                        html.I(
                                            className=f"fas {'fa-arrow-up text-danger' if df[df['Year'] == df['Year'].max()]['Obesity_Prevalence_Rate'].mean() > df[df['Year'] == df['Year'].max() - 1]['Obesity_Prevalence_Rate'].mean() else 'fa-arrow-down text-success'}"
                                        ),
                                    ], style={"display": "flex", "justifyContent": "center",
                                              "alignItems": "center", "gap": "10px"}),
                                    html.P("Obesity Prevalence Rate", className="text-center text-muted"),
                                ])
                            ], className="shadow-sm border", style={"height": "120px"})
                        ], xs=12, sm=6, lg=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div([
                                        html.H4(
                                            f"{df[df['Year'] == df['Year'].max()]['Activity_Prevalence_Rate'].mean():,.1f}%",
                                            style={"color": "navy", "display": "inline"}
                                        ),
                                        html.I(
                                            className=f"fas {'fa-arrow-up text-success' if df[df['Year'] == df['Year'].max()]['Activity_Prevalence_Rate'].mean() > df[df['Year'] == df['Year'].max() - 1]['Activity_Prevalence_Rate'].mean() else 'fa-arrow-down text-danger'}"
                                        ),
                                    ], style={"display": "flex", "justifyContent": "center",
                                              "alignItems": "center", "gap": "10px"}),
                                    html.P("Physical Activity Rate", className="text-center text-muted"),
                                ])
                            ], className="shadow-sm border", style={"height": "120px"})
                        ], xs=12, sm=6, lg=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div([
                                        html.H4(
                                            f"{df[df['Year'] == df['Year'].max()]['Alcohol_Value'].mean():,.1f}",
                                            style={"color": "navy", "display": "inline"}
                                        ),
                                        html.I(
                                            className=f"fas {'fa-arrow-up text-danger' if df[df['Year'] == df['Year'].max()]['Alcohol_Value'].mean() > df[df['Year'] == df['Year'].max() - 1]['Alcohol_Value'].mean() else 'fa-arrow-down text-success'}"
                                        ),
                                    ], style={"display": "flex", "justifyContent": "center",
                                              "alignItems": "center", "gap": "10px"}),
                                    html.P("Alcohol Consumption (Liters per capita)",
                                           className="text-center text-muted"),
                                ])
                            ], className="shadow-sm border", style={"height": "120px"})
                        ], xs=12, sm=6, lg=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div([
                                        html.H4(
                                            f"{df[df['Year'] == df['Year'].max()]['Diabetes_Prevalence_Rate'].mean():,.1f}%",
                                            style={"color": "navy", "display": "inline"}
                                        ),
                                        html.I(
                                            className=f"fas {'fa-arrow-up text-danger' if df[df['Year'] == df['Year'].max()]['Diabetes_Prevalence_Rate'].mean() > df[df['Year'] == df['Year'].max() - 1]['Diabetes_Prevalence_Rate'].mean() else 'fa-arrow-down text-success'}"
                                        ),
                                    ], style={"display": "flex", "justifyContent": "center",
                                              "alignItems": "center", "gap": "10px"}),
                                    html.P("Diabetes Prevalence Rate", className="text-center text-muted"),
                                ])
                            ], className="shadow-sm border", style={"height": "120px"})
                        ], xs=12, sm=6, lg=3),
                    ]),
                    html.P(
                        "↑↓ Arrows indicate change compared to 2022 averages",
                        className="text-center text-muted small mb-4 mt-4",
                        style={"fontSize": "0.9rem"}
                    )
                ], width=12),
            ])

        ]),

        # Data Sources and Info Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.Col([
                        html.H2("Data Sources",
                                className="text-center fw-semibold mb-3 p-2 bg-light rounded shadow-sm border")
                    ], width=12),
                    dbc.CardBody([
                        html.Div([
                            html.P(
                                "This dashboard synthesizes data from multiple authoritative global health and economic databases:",
                                className="lead text-center mb-4"
                            ),
                            dbc.ListGroup([
                                dbc.ListGroupItem([
                                    html.A("WHO Global Health Observatory",
                                           href="https://www.who.int/data/gho",
                                           target="_blank",
                                           className="fw-bold text-decoration-none",
                                           style={"color": "navy"}),
                                    html.Span(" - Comprehensive risk factor and economic data",
                                              className="text-muted ms-2")
                                ], className="border-0 bg-transparent"),
                                dbc.ListGroupItem([
                                    html.A("Global Burden of Disease (GBD) Study",
                                           href="https://www.healthdata.org/research-analysis/gbd-data",
                                           target="_blank",
                                           className="fw-bold text-decoration-none",
                                           style={"color": "navy"}),
                                    html.Span(" - Primary source for health metrics and disease indicators",
                                              className="text-muted ms-2",)
                                ], className="border-0 bg-transparent"),
                                dbc.ListGroupItem([
                                    html.A("NCD Risk Factor Collaboration (NCD-RisC)",
                                           href="https://ncdrisc.org/data-downloads.html",
                                           target="_blank",
                                           className="fw-bold text-decoration-none",
                                           style={"color": "navy"}),
                                    html.Span(" - Comprehensive risk factor data",
                                              className="text-muted ms-2")
                                ], className="border-0 bg-transparent"),
                                dbc.ListGroupItem([
                                    html.A("Gapminder Dataset",
                                           href="https://www.gapminder.org/data/",
                                           target="_blank",
                                           className="fw-bold text-decoration-none",
                                           style={"color": "navy"}),
                                    html.Span(" - Global demographic and health trends",
                                              className="text-muted ms-2")
                                ], className="border-0 bg-transparent"),
                                dbc.ListGroupItem([
                                    html.A("World Bank",
                                           href="https://databank.worldbank.org/",
                                           target="_blank",
                                           className="fw-bold text-decoration-none",
                                           style={"color": "navy"}),
                                    html.Span(" - GDP per capita (PPP) economic indicators",
                                              className="text-muted ms-2")
                                ], className="border-0 bg-transparent")
                            ], flush=True, className="mb-4"),
                            html.P([
                                "By integrating these diverse sources, we offer a comprehensive, multi-dimensional ",
                                "analysis of global heart disease patterns, economic contexts, and health trends."
                            ], className="text-center text-muted fst-italic mb-0")
                        ], className="px-2")
                    ], className="py-4")
                ], className="shadow-sm border-0 h-100")
            ], xs=12, md=12, lg=12, className="mx-auto")
        ], className="py-3")
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
