import plotly.express as px
import pandas as pd
import pycountry
import pycountry_convert as pc
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output

continent_map = {
    'NA': 'North America', 'SA': 'South America', 'EU': 'Europe',
    'AS': 'Asia', 'OC': 'Oceania', 'AF': 'Africa'
}

manual_region_mapping = {
    'XKX': 'Europe', 'OWID_KOS': 'Europe', 'SXM': 'North America', 'TLS': 'Asia'}

# Tooltip style
tooltip_style = {
    "color": "white",
    "backgroundColor": "#333",
    "borderRadius": "5px",
    "padding": "8px",
    "fontSize": "14px"
}

metric_labels = {
    'MortalityRate': 'Mortality Rate (per 100,000)',
    'IncidenceRate': 'Incidence Rate (per 100,000)',
    'PrevalenceRate': 'Prevalence Rate (per 100,000)',
    'GDP': 'GDP per Capita (USD)',
    'Health_Expenditure (% of GDP)': 'Healthcare Expenditure (% of GDP)'
}


def alpha3_to_alpha2(alpha3_code):
    """
        Convert a three-letter country code (ISO Alpha-3) to a two-letter country code (ISO Alpha-2).

        Parameters:
        alpha3_code (str): Three-letter country code.

        Returns:
        str: Two-letter country code or None if not found.
        """
    country = pycountry.countries.get(alpha_3=alpha3_code)
    return country.alpha_2 if country else None


def get_region(country_code):
    """
        Retrieve the region (continent) of a given country code.

        Parameters:
        country_code (str): Two-letter or three-letter country code.

        Returns:
        str: Continent name or 'Unknown Region' if not found.
        """
    if country_code in manual_region_mapping:
        return manual_region_mapping[country_code]
    if len(country_code) == 3:
        country_code = alpha3_to_alpha2(country_code)
    return continent_map.get(pc.country_alpha2_to_continent_code(country_code), 'Unknown Region')


def create_choropleth(df, year, continent, metric, age_group, gender, economic_indicator=None):
    """
        Generate an interactive choropleth map based on health or economic metrics.

        Parameters:
        df (DataFrame): Input data containing health metrics.
        year (int): Selected year for visualization.
        continent (str): Continent filter.
        metric (str): Health metric to visualize.
        age_group (str): Selected age group filter.
        gender (str): Selected gender filter.
        economic_indicator (str, optional): Economic metric to visualize instead of health metrics.

        Returns:
        plotly.graph_objects.Figure: Choropleth map visualization.
        """

    # Data filtering based on user selections
    filtered_df = df[df['Year'] == year]
    if continent != "All":
        filtered_df = filtered_df[filtered_df['Region'] == continent]
    if age_group != "Age-standardized":
        filtered_df = filtered_df[filtered_df['Age_Group'] == age_group]
    if gender != "All":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]

    # Determine which metric to use and the color scale
    if economic_indicator and economic_indicator != 'None':
        selected_metric = economic_indicator
        color_scale = 'Pubu'
    else:
        selected_metric = metric
        color_scale = 'Gnbu'

    continent_scope_mapping = {
        'North America': 'north america',
        'South America': 'south america',
        'Europe': 'europe',
        'Asia': 'asia',
        'Oceania': 'world',
        'Africa': 'africa',
        'All': 'world'
    }

    # Updated hover text with lighter styling and better spacing
    filtered_df = filtered_df.copy() # Avoiding SettingWithCopyWarning
    filtered_df.loc[:, 'Hover_Text'] = filtered_df.apply(
        lambda row: (
            f"<span style='font-family: Arial, sans-serif;'>"
            f"<span style='font-size: 16px; color: #2c3e50; font-weight: 600;'>{row['Country']}</span><br><br>"
            f"<span style='color: #7f8c8d; font-size: 12px;'>📅 Year:</span> "
            f"<span style='color: #3498db; font-weight: 500;font-size: 12px;'>{year}</span><br>"
            f"<span style='color: #7f8c8d; font-size: 12px;'>📊 {metric_labels[selected_metric]}:</span> "
            f"<span style='color: #27ae60; font-weight: 500; font-size: 12px;'"
            f">{row[selected_metric]:,.2f}</span><br>"
            + (f"<span style='color: #7f8c8d; font-size: 12px;'>💰 GDP:</span> "
               f"<span style='font-size: 12px; color: #e67e22; font-weight: 500;'>${row['GDP']:,.2f}</span><br>"
               if ('GDP' in filtered_df.columns and pd.notna(row['GDP']) and
                   selected_metric != 'GDP') else "")
            + (f"<span style='color: #7f8c8d; font-size: 12px;'>🏥 Health Expenditure:</span> "
               f"<span style='color: #e74c3c; font-weight: 500; font-size: 12px;'"
               f">{row['Health_Expenditure (% of GDP)']:,.2f}%</span>"
               if ('Health_Expenditure (% of GDP)' in filtered_df.columns and
                   pd.notna(row['Health_Expenditure (% of GDP)']) and
                   selected_metric != 'Health_Expenditure (% of GDP)') else "")
            + "</span>"
        ),
        axis=1
    )

    # Choropleth map generation
    fig = px.choropleth(
        filtered_df,
        locations='Country_Code',
        color=selected_metric,
        hover_name=None,
        hover_data={'Hover_Text': True, 'Country_Code': False},
        custom_data=['Hover_Text'],  # Add custom data for hover template
        color_continuous_scale=color_scale,
        title=f'{metric_labels.get(selected_metric, selected_metric)} Distribution ({year})'
    )

    # Update hover template to use custom hover text
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>"
    )

    fig.update_layout(
        autosize=True,
        margin={"r": 10, "t": 80, "l": 10, "b": 10},
        coloraxis_colorbar=dict(
            title=f"{selected_metric.replace('_', ' ').title()} (%)",
            x=1.05,
            len=0.6,
            thickness=20
        ),
        geo=dict(
            showframe=False,
            projection_type='natural earth',
            projection_scale=1.2,
            scope=continent_scope_mapping.get(continent, 'world')
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            bordercolor="#e5e5e5",
            font_family="Arial, sans-serif"
        )
    )

    return fig


def create_barplot(df, year, continent, metric, age_group, gender):
    """
    Create a horizontal bar plot to show the top 10 countries based on a selected metric.

    Parameters:
    df (DataFrame): Input data containing health metrics.
    year (int): Selected year for visualization.
    continent (str): Continent filter.
    metric (str): Health metric to visualize.
    age_group (str): Selected age group filter.
    gender (str): Selected gender filter.

    Returns:
    plotly.graph_objects.Figure: Bar plot visualization.
    """

    filtered_df = df[df['Year'] == year]
    if continent != "All":
        filtered_df = filtered_df[filtered_df['Region'] == continent]
    if age_group != "Age-standardized":
        filtered_df = filtered_df[filtered_df['Age_Group'] == age_group]
    if gender != "All":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]

    # Ensure data is available
    if filtered_df.empty:
        return px.bar(
            title=f'No data available for selected filters',
            labels={'x': 'Country', 'y': metric}
        )

    # Handle NaN values and sorting
    top_10_countries = (
        filtered_df.dropna(subset=[metric])
        .nlargest(10, metric)[['Country', metric, 'Region', 'GDP']]
        .sort_values(metric, ascending=True)
    )

    # Create custom hover text with rich formatting
    top_10_countries['hover_text'] = top_10_countries.apply(
        lambda row: (
            f"<span style='font-family: Arial, sans-serif; font-size: 16px;'>"
            f"<b style='color: #2c3e50;'>{row['Country']}</b><br><br>"
            f"<span style='color: #7f8c8d;'>🌐 Region:</span> "
            f"<span style='color: #3498db; font-weight: bold;'>{row['Region']}</span><br>"
            f"<span style='color: #7f8c8d;'>📊 {metric.replace('_', ' ').title()}:</span> "
            f"<span style='color: #27ae60; font-weight: bold;'>{row[metric]:,.2f}</span><br>"
            f"<span style='color: #7f8c8d;'>💰 GDP per capita:</span> "
            f"<span style='color: #e67e22; font-weight: bold;'>${row['GDP']:,.2f}</span>"
            "</span>"
        ),
        axis=1
    )

    # Enhanced bar plot with more styling
    fig = px.bar(
        top_10_countries,
        x=metric,
        y='Country',
        orientation='h',
        color='Country',
        custom_data=['hover_text'],  # Add custom hover data
        title=f'Top 10 Countries - {metric_labels[metric]} ({year})'
    )

    fig.update_traces(
        # Use custom hover text
        hovertemplate='%{customdata[0]}<extra></extra>',
    )

    fig.update_layout(
        height=700,
        title_x=0.5,
        xaxis_title=metric_labels[metric],
        yaxis_title='Country',
        bargap=0.2,
        template='plotly_white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Arial, sans-serif",
            bordercolor="#e5e5e5"
        )
    )

    return fig


def create_scatter_plot(df, year, continent, metric, economic_indicator, age_group, gender):
    """
    Generate a scatter plot to analyze the correlation between a health metric and an economic indicator.

    Parameters:
    df (DataFrame): Input data containing health and economic metrics.
    year (int): Selected year for visualization.
    continent (str): Continent filter.
    metric (str): Health metric for the Y-axis.
    economic_indicator (str): Economic indicator for the X-axis.
    age_group (str): Selected age group filter.
    gender (str): Selected gender filter.

    Returns:
    plotly.graph_objects.Figure: Scatter plot visualization.
    """
    # Filter data
    filtered_df = df[df['Year'] == year]
    if continent != "All":
        filtered_df = filtered_df[filtered_df['Region'] == continent]
    if age_group != "Age-standardized":
        filtered_df = filtered_df[filtered_df['Age_Group'] == age_group]
    if gender != "All":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]

    # Handle data availability
    filtered_df = filtered_df.dropna(subset=[metric, economic_indicator])
    if filtered_df.empty:
        return px.scatter(title=f"No data available for selected filters")

    # Create scatter plot with formatted labels
    fig = px.scatter(
        filtered_df,
        x=economic_indicator,
        y=metric,
        color="Region",
        hover_name="Country",
        title=f'Correlation: {metric_labels[economic_indicator]} vs {metric_labels[metric]} ({year})',
        trendline="ols",
        labels={
            economic_indicator: metric_labels[economic_indicator],
            metric: metric_labels[metric]
        }
    )

    # Update layout with consistent formatting
    fig.update_layout(
        height=700,
        title_x=0.5,
        template='plotly_white',
        xaxis_title=metric_labels[economic_indicator],
        yaxis_title=metric_labels[metric],
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial, sans-serif",
            bordercolor="#e5e5e5"
        )
    )

    return fig


def get_choropleth_layout(df):
    """
    Generate the layout for the choropleth map dashboard, including filter dropdowns and graph components.

    Parameters:
    df (DataFrame): Input dataset containing available options for dropdowns.

    Returns:
    html.Div: Dash HTML layout containing filters, maps, and visualizations.
    """

    starting_year = df['Year'].min()

    # Common styles
    map_style = {
        'width': '100%',
        'height': '700px',
        'overflow': 'hidden',
        'margin-bottom': '2rem'
    }

    dropdown_style = {
        'className': 'responsive-dropdown fw-bold mb-2',
        'clearable': False
    }

    header_style = {
        "fontSize": "clamp(1.7rem, 4vw, 2.7rem)",
        "marginBottom": "1rem",
        "background": "linear-gradient(135deg, #17202A 0%, #2C3E50 100%)",
        "color": "white",
        "fontFamily": "'Segoe UI', system-ui, -apple-system, sans-serif",
        "lineHeight": "1.4"
    }

    # Dropdown configurations
    dropdowns = [
        {
            'label': "Select Region",
            'id': 'continent-dropdown',
            'options': [{'label': 'All', 'value': 'All'}] +
                       [{'label': region, 'value': region} for region in df['Region'].unique()],
            'value': 'All',
            'tooltip': "Choose a region to filter data geographically."
        },
        {
            'label': "Select Year",
            'id': 'year-dropdown',
            'options': [{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
            'value': starting_year,
            'tooltip': "Select the year of interest for the data."
        },
        {
            'label': "Select Health Metric",
            'id': 'metric-dropdown',
            'options': [
                {'label': 'Mortality Rate', 'value': 'MortalityRate'},
                {'label': 'Incidence Rate', 'value': 'IncidenceRate'},
                {'label': 'Prevalence Rate', 'value': 'PrevalenceRate'}
            ],
            'value': 'PrevalenceRate',
            'tooltip': "Select a health-related metric for visualization."
        },
        {
            'label': "Select Economic Indicator",
            'id': 'economic-indicator-dropdown',
            'options': [
                {'label': 'None', 'value': 'None'},
                {'label': 'GDP per capita', 'value': 'GDP'},
                {'label': 'Health Expenditure (% of GDP)', 'value': 'Health_Expenditure (% of GDP)'}
            ],
            'value': 'None',
            'tooltip': "Selecting an economic indicator will replace the health metric map with the chosen economic data."
        },
        {
            'label': "Select Age Group",
            'id': 'age-group-dropdown',
            'options': [{'label': age, 'value': age} for age in sorted(df['Age_Group'].unique()) if
                        age != 'No Age Group'],
            'value': 'Age-standardized',
            'tooltip': "Select an age group to filter data accordingly. 'Age-standardized' includes all age groups."
        },
        {
            'label': "Select Gender",
            'id': 'gender-dropdown',
            'options': [
                {'label': 'All', 'value': 'All'},
                {'label': 'Female', 'value': 'Female'},
                {'label': 'Male', 'value': 'Male'}
            ],
            'value': 'All',
            'tooltip': "Choose 'All' for both genders or filter by 'Male' or 'Female'."
        }
    ]

    return html.Div([
        # Header
        html.H3(
            "Heart Disease Atlas",
            className="text-center fw-semibold mb-3 p-3 rounded shadow-sm",
            style=header_style
        ),

        # Subtitle
        html.H5(
            "Exploring the Relationship Between Economic Factors and Heart Health Outcomes Worldwide",
            className="text-center text-muted mb-3",
            style={
                "fontSize": "clamp(1rem, 2vw, 1.25rem)",
                "fontWeight": "normal",
                "lineHeight": "1.3"
            }
        ),

        # Filter Card
        dbc.Card(
            dbc.CardBody(
                dbc.Row([
                            dbc.Col([
                                html.Label(dropdown['label'], className="fw-bold mb-2"),
                                html.Span("ⓘ",
                                          id=f"{dropdown['id'].split('-')[0]}-tooltip",
                                          style={"cursor": "pointer", "marginLeft": "8px", "fontSize": "18px",
                                                 "color": "#0d6efd"}),
                                dbc.Tooltip(dropdown['tooltip'],
                                            target=f"{dropdown['id'].split('-')[0]}-tooltip",
                                            placement="right",
                                            style=tooltip_style),
                                dcc.Dropdown(
                                    id=dropdown['id'],
                                    options=dropdown['options'],
                                    value=dropdown['value'],
                                    **dropdown_style
                                )
                            ], xs=12, sm=12, md=4, lg=4, xl=4)
                            for dropdown in dropdowns[:3]
                        ] + [
                            dbc.Col([
                                html.Label(dropdown['label'], className="fw-bold mb-2"),
                                html.Span("ⓘ",
                                          id=f"{dropdown['id'].split('-')[0]}-tooltip",
                                          style={"cursor": "pointer", "marginLeft": "8px", "fontSize": "18px",
                                                 "color": "#0d6efd"}),
                                dbc.Tooltip(dropdown['tooltip'],
                                            target=f"{dropdown['id'].split('-')[0]}-tooltip",
                                            placement="right",
                                            style=tooltip_style),
                                dcc.Dropdown(
                                    id=dropdown['id'],
                                    options=dropdown['options'],
                                    value=dropdown['value'],
                                    **dropdown_style
                                )
                            ], xs=12, sm=12, md=4, lg=4, xl=4)
                            for dropdown in dropdowns[3:]
                        ], className="g-3")
            ),
            className='bg-light border rounded p-3 shadow-sm mb-4'
        ),

        # Maps Container
        dbc.Row([
            dbc.Col([
                # Health Metric Map
                dcc.Graph(id='choropleth-map', style=map_style),

                # Economic Map
                html.Div([
                    html.H4("Economic Indicator Map", className="text-center mb-3"),
                    dcc.Loading(
                        id="loading-economic-map",
                        type="default",
                        children=[dcc.Graph(id='economic-choropleth-map', style=map_style)]
                    )
                ], id='economic-map-container', style={'display': 'none'}),

                # Scatter Plot
                html.Div([
                    html.Hr(),
                    html.H4("Scatter Plot", className="text-center mb-3"),
                    dcc.Loading(
                        id="loading-scatter-plot",
                        type="default",
                        children=[
                            dcc.Graph(
                                id='scatter-plot',
                                style={'height': '600px', 'width': '100%'}
                            )
                        ]
                    )
                ], id='scatter-container', style={'display': 'none'})
            ], width=12)
        ], className="mb-4"),

        html.Hr(),

        # Bar Plot
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='bar-plot',
                    style={'height': '700px', 'width': '100%'}
                )
            ], width=12)
        ])
    ])


# Supplementary CSS to enhance responsiveness
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    {
        'href': 'assets/custom-responsive.css',
        'rel': 'stylesheet'
    }
]


def register_choropleth_callbacks(app, df):
    @app.callback(
        [Output("choropleth-map", "figure"),
         Output("economic-choropleth-map", "figure"),
         Output("economic-map-container", "style"),
         Output("bar-plot", "figure"),
         Output('scatter-plot', 'figure'),
         Output("scatter-container", "style")],
        [Input("year-dropdown", "value"),
         Input("continent-dropdown", "value"),
         Input("metric-dropdown", "value"),
         Input("economic-indicator-dropdown", "value"),
         Input("age-group-dropdown", "value"),
         Input("gender-dropdown", "value")],
        prevent_initial_call=False
    )
    def update_plots(year, continent, metric, economic_indicator, age_group, gender):
        # Set default values
        year = year or df['Year'].min()
        continent = continent or 'All'
        metric = metric or 'PrevalenceRate'
        age_group = age_group or 'Age-standardized'
        gender = gender or 'Both'

        # Create the primary health metric choropleth and bar plot
        choropleth_fig = create_choropleth(
            df, year, continent, metric, age_group, gender)
        bar_fig = create_barplot(
            df, year, continent, metric, age_group, gender)

        # Default hidden styles for economic maps and scatter plot
        economic_map_style = {'display': 'none'}
        scatter_plot_style = {'display': 'none'}

        # Placeholder figures
        economic_choropleth_fig = px.choropleth(
            title='Select an Economic Indicator')
        scatter_fig = px.scatter(title="Select an Economic Indicator")

        # Show economic choropleth and scatter plot if an economic indicator is selected
        if economic_indicator and economic_indicator != 'None':
            economic_choropleth_fig = create_choropleth(
                df, year, continent, metric, age_group, gender, economic_indicator)
            economic_map_style = {'display': 'block'}
            scatter_plot_style = {'display': 'block'}

            scatter_fig = px.scatter(
                df[df['Year'] == year],
                x=economic_indicator,
                y=metric,
                color="Region",
                size="Population" if "Population" in df.columns else None,
                hover_name="Country",
                title=f"{metric} vs {economic_indicator} ({year})"
            )

        return choropleth_fig, economic_choropleth_fig, economic_map_style, bar_fig, scatter_fig, scatter_plot_style
