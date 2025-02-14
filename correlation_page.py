import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pycountry_convert as pc
from flask_caching import Cache

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

# global_styles = {"height": "100vh"}
# Tooltip style
tooltip_style = {
    "color": "white",
    "backgroundColor": "#333",
    "borderRadius": "5px",
    "padding": "8px",
    "fontSize": "14px"
}

# Dataset
data = pd.read_parquet("dataset/FINAL_MERGED_DATA_reimputed.parquet", engine="pyarrow")

# Unique values for filters
years = sorted(data['Year'].unique())
countries = sorted(data['Country'].unique())
age_groups = sorted(data['Age_Group'].unique())
genders = ['Male', 'Female', 'Both']

custom_continent_map = {

    "Asia": ["Democratic Republic of Timor-Leste", "Republic of Turkey", 'Lao PDR'],
    "Africa": ["Cote d'Ivoire", 'Guinea Bissau', 'Republic of Rwanda',
               'Republic of Sudan'],
}

corr_data = data.copy()
corr_data = corr_data.drop(columns=['Country_Code'], axis=1)


def get_correlation_layout():
    """
        Creates the layout for the correlation analysis page of the dashboard.

        Returns:
            dbc.Container: A Bootstrap container containing the complete layout including:
                - Title and subtitle
                - Filter section (year and country selectors)
                - Correlation heatmap with feature selection
                - Scatter plot with x and y axis feature selection
                - Sankey diagram with target feature selection
        """
    return dbc.Container([
        html.H1(
            ["Heart Disease Risk Factor Explorer ",
             ],
            className="text-center fw-semibold mb-3 p-3 rounded shadow-sm",
            style={
                "fontSize": "clamp(1.7rem, 4vw, 2.7rem)",
                "marginBottom": "1rem",
                "background": "linear-gradient(135deg, #17202A 0%, #2C3E50 100%)",
                "color": "white",
                "fontFamily": "'Segoe UI', system-ui, -apple-system, sans-serif",
                "lineHeight": "1.4"
            }),
        # Subtitle with icons
        html.H5([
            "Unveiling Correlations in Global Health Metrics ",
        ],
            className="text-center mb-3 p-2 bg-light rounded shadow-sm",
            style={"fontSize": "clamp(1.6rem, 2vw, 1.8rem)", 'border': '1px solid #dee2e6', }),

        dbc.Col([

            dbc.Row([

                # Left Column: Filters
                dbc.Col([
                    html.H5("Filters", style={'textAlign': 'center'}),

                    # Year Selector
                    html.Label("Select Year:", className="mb-2 fw-medium"),
                    dcc.Dropdown(
                        id='year-dropdown-corr',
                        options=[{'label': 'All', 'value': 'All'}] +
                                [{'label': year, 'value': year} for year in sorted(corr_data['Year'].unique())],
                        value='All',
                        placeholder="Select year",
                        className="mb-4"
                    ),

                    # Country Selector
                    html.Label("Select Countries:", className="mb-2 fw-medium"),
                    dcc.Dropdown(
                        id='country-dropdown-corr',
                        options=[{'label': 'All', 'value': 'All'}] +
                                [{'label': country, 'value': country} for country in
                                 sorted(corr_data['Country'].unique())],
                        value='All',
                        placeholder="Select one or more countries"
                    ),

                ], width=3, style={
                    'padding': '20px',
                    'borderRadius': '12px',
                    'border': '1px solid #dee2e6',
                    'backgroundColor': '#f8f9fa',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
                    "marginBottom": "30px"
                }),

                # Right Column: Visualizations
                dbc.Col([
                    html.H5("Feature Correlation Heatmap", style={'textAlign': 'left', 'marginBottom': '10px'}),
                    html.Label("Select Features "),
                    html.Span("ⓘ", id="metric-tooltip",
                              style={"cursor": "pointer", "marginLeft": "5px", "fontSize": "18px",
                                     "color": "#0d6efd"}),
                    dbc.Tooltip("Select two or more features for the heatmap.", target="metric-tooltip",
                                placement="right", style=tooltip_style),
                    dcc.Dropdown(
                        id='heatmap-dropdown',
                        options=[{"label": "Select All", "value": "All"}] + [{'label': col, 'value': col} for col in
                                                                             corr_data.columns if
                                                                             col not in ['Country', 'Year', 'Age_Group',
                                                                                         'Gender']],
                        value=[corr_data.columns[2], corr_data.columns[3]],  # Default selection
                        multi=True,
                        placeholder="Select features for heatmap"
                    ),
                    dcc.Graph(id='heatmap'),

                    html.H5("Feature Scatterplot", style={'textAlign': 'left', 'marginBottom': '10px'}),
                    dcc.Dropdown(
                        id='scatter-dropdown-x',
                        options=[{'label': col, 'value': col} for col in corr_data.columns if
                                 col not in ['Country', 'Year', 'Age_Group', 'Gender']],
                        placeholder="Select X-axis feature"
                    ),
                    dcc.Dropdown(
                        id='scatter-dropdown-y',
                        options=[{'label': col, 'value': col} for col in corr_data.columns if
                                 col not in ['Country', 'Year', 'Age_Group', 'Gender']],
                        placeholder="Select Y-axis feature"
                    ),
                    dcc.Graph(id='scatterplot-corr'),

                ], width=9)
            ]),

            html.H5("Feature Sankey Diagram", style={'textAlign': 'left', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='sankey-dropdown',
                options=[{'label': col, 'value': col} for col in corr_data.columns if
                         col in ['PrevalenceRate', 'MortalityRate', 'IncidenceRate']],
                value="PrevalenceRate",
                placeholder="Select target feature"
            ),
            dcc.Graph(id="sankey-diagram", style={'height': '600px'}),

        ])
    ], fluid=True)


def register_callbacks_corr(app, cache):
    """
       Registers all callbacks for the correlation analysis page.

       Args:
           app (dash.Dash): The Dash application instance
           cache (Cache): Flask-Cache instance for memoizing computations

       Note:
           This function sets up the interactive functionality for:
           - Heatmap feature selection and visualization
           - Scatter plot feature selection and visualization
           - Sankey diagram updates
           - Filter applications
       """
    @cache.memoize()
    def sankey_data_prep(data):
        """
          Prepares data for the Sankey diagram by adding region information to the dataset.

          Args:
              data (pd.DataFrame): Input DataFrame containing country information

          Returns:
              pd.DataFrame: DataFrame with added 'Region' column mapping countries to their continental regions
          """
        def get_region(country_name):
            """
                   Maps a country name to its continental region using pycountry_convert.

                   Args:
                       country_name (str): Name of the country

                   Returns:
                       str: Continent name or np.nan if mapping fails
                   """
            try:
                country_code = pc.country_name_to_country_alpha2(country_name, cn_name_format="default")
                continent_code = pc.country_alpha2_to_continent_code(country_code)

                # separating Americas if needed:
                if continent_code == 'NA':
                    return 'North America'
                elif continent_code == 'SA':
                    return 'South America'
                else:
                    return pc.convert_continent_code_to_continent_name(continent_code)

            except KeyError:
                return np.nan  # handling cases where country code is not found

        def get_custom_region(country_name):
            """
                    Maps countries to regions using custom mapping for cases not covered by pycountry_convert.

                    Args:
                        country_name (str): Name of the country

                    Returns:
                        str: Region name from custom mapping or np.nan if not found
                    """
            for region, countries in custom_continent_map.items():
                if country_name in countries:
                    return region
            return np.nan  # Keep existing values unchanged

        data['Region'] = data['Country'].apply(get_region)
        # Only replace NaN values in the 'Region' column
        data["Region"] = data["Region"].fillna(data["Country"].map(get_custom_region))
        return data

    @cache.memoize()
    def create_sankey(trgt):
        """
           Creates a Sankey diagram showing relationships between risk factors, regions, and target health metric.

           Args:
               trgt (str): Target variable name ('PrevalenceRate', 'MortalityRate', or 'IncidenceRate')

           Returns:
               go.Figure: Plotly figure object containing the Sankey diagram
           """
        df = sankey_data_prep(data)
        # Calculate quartiles for each relevant column
        alcohol_quartiles = df['Alcohol_Value'].quantile([0.25, 0.5, 0.75])
        obesity_quartiles = df['Obesity_Prevalence_Rate'].quantile([0.25, 0.5, 0.75])
        diabetes_quartiles = df['Diabetes_Prevalence_Rate'].quantile([0.25, 0.5, 0.75])
        physical_quartiles = df['Activity_Prevalence_Rate'].quantile([0.25, 0.5, 0.75])
        trgt_quartiles = df[trgt].quantile([0.25, 0.5, 0.75])

        def categorize_alcohol(x):
            if x <= alcohol_quartiles[0.25]:
                return "Low Alcohol"
            elif x <= alcohol_quartiles[0.75]:
                return "Moderate Alcohol"
            else:
                return "High Alcohol"

        def categorize_obesity(x):
            if x <= obesity_quartiles[0.25]:
                return "Low Obesity"
            elif x <= obesity_quartiles[0.75]:
                return "Moderate Obesity"
            else:
                return "High Obesity"

        def categorize_diabetes(x):
            if x <= diabetes_quartiles[0.25]:
                return "Low Diabetes"
            elif x <= diabetes_quartiles[0.75]:
                return "Moderate Diabetes"
            else:
                return "High Diabetes"

        def categorize_physical(x):
            if x <= physical_quartiles[0.25]:
                return "Low Physical Activity"
            elif x <= physical_quartiles[0.75]:
                return "Moderate Physical Activity"
            else:
                return "High Physical Activity"

        def categorize_trgt(x):
            if x <= trgt_quartiles[0.25]:
                return f"Low {trgt}"
            elif x <= trgt_quartiles[0.75]:
                return f"Moderate {trgt}"
            else:
                return f"High {trgt}"

        # Apply categorization
        df["Alcohol Level"] = df["Alcohol_Value"].apply(categorize_alcohol)
        df["Obesity Level"] = df["Obesity_Prevalence_Rate"].apply(categorize_obesity)
        df["Diabetes Level"] = df["Diabetes_Prevalence_Rate"].apply(categorize_diabetes)
        df["Physical Activity Level"] = df["Activity_Prevalence_Rate"].apply(categorize_physical)
        df[f"{trgt} Level"] = df[trgt].apply(categorize_trgt)

        source_target_pairs_alc = df.groupby(["Alcohol Level", "Region"]).size().reset_index(name="Count")
        source_target_pairs_obesity = df.groupby(["Obesity Level", "Region"]).size().reset_index(name="Count")
        source_target_pairs_diabetes = df.groupby(["Diabetes Level", "Region"]).size().reset_index(name="Count")
        source_target_pairs_physical = df.groupby(["Physical Activity Level", "Region"]).size().reset_index(
            name="Count")
        source_target_pairs_trgt = df.groupby(["Region", f"{trgt} Level"]).size().reset_index(name="Count")

        all_nodes = pd.unique(pd.concat([
            source_target_pairs_alc[["Alcohol Level", "Region"]],
            source_target_pairs_obesity[["Obesity Level", "Region"]],
            source_target_pairs_diabetes[["Diabetes Level", "Region"]],
            source_target_pairs_physical[["Physical Activity Level", "Region"]],
            source_target_pairs_trgt[["Region", f"{trgt} Level"]]
        ]).values.ravel('K'))

        node_map = {name: i for i, name in enumerate(all_nodes)}

        source = source_target_pairs_alc["Alcohol Level"].map(node_map).tolist() + \
                 source_target_pairs_obesity["Obesity Level"].map(node_map).tolist() + \
                 source_target_pairs_diabetes["Diabetes Level"].map(node_map).tolist() + \
                 source_target_pairs_physical["Physical Activity Level"].map(node_map).tolist() + \
                 source_target_pairs_trgt["Region"].map(node_map).tolist()

        target = source_target_pairs_alc["Region"].map(node_map).tolist() + \
                 source_target_pairs_obesity["Region"].map(node_map).tolist() + \
                 source_target_pairs_diabetes["Region"].map(node_map).tolist() + \
                 source_target_pairs_physical["Region"].map(node_map).tolist() + \
                 source_target_pairs_trgt[f"{trgt} Level"].map(node_map).tolist()

        values = source_target_pairs_alc["Count"].tolist() + \
                 source_target_pairs_obesity["Count"].tolist() + \
                 source_target_pairs_diabetes["Count"].tolist() + \
                 source_target_pairs_physical["Count"].tolist() + \
                 source_target_pairs_trgt["Count"].tolist()

        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                label=all_nodes  # Use consolidated nodes
            ),
            link=dict(
                source=source,
                target=target,
                value=values
            )
        ))

        fig.update_layout(title_text="Risk Factor Influence on Heart Disease per Continent", font_size=12)
        return fig

    @cache.memoize()
    def filter_scatter_data(year, countries, x_feature, y_feature):
        """
           Filters the dataset based on selected year and countries for scatter plot visualization.

           Args:
               year (str or int): Selected year or 'All'
               countries (str): Selected country or 'All'
               x_feature (str): Feature name for x-axis
               y_feature (str): Feature name for y-axis

           Returns:
               pd.DataFrame: Filtered DataFrame containing only the selected data
           """
        filtered_df = corr_data.copy()
        if year != 'All':
            filtered_df = filtered_df[filtered_df['Year'] == year]
        if countries != 'All':
            filtered_df = filtered_df[filtered_df['Country'] == countries]
        return filtered_df

    @cache.memoize()
    def filter_heatmap_data(year, countries):
        """
          Filters the dataset based on selected year and countries for heatmap visualization.

          Args:
              year (str or int): Selected year or 'All'
              countries (str): Selected country or 'All'

          Returns:
              pd.DataFrame: Filtered DataFrame containing only the selected data
          """
        filtered_df = corr_data.copy()
        if year != 'All':
            filtered_df = filtered_df[filtered_df['Year'] == year]
        if countries != 'All':
            filtered_df = filtered_df[filtered_df['Country'] == countries]
        return filtered_df

    # callbacks for correlation page

    @app.callback(
        Output("heatmap-dropdown", "value"),
        Input("heatmap-dropdown", "value"),
        prevent_initial_call=True
    )
    def update_dropdown(selected_values):
        """
           Updates the heatmap feature selection dropdown values.

           Args:
               selected_values (list): List of currently selected feature values

           Returns:
               list: Updated list of selected values, returns all features if 'All' is selected
           """
        if selected_values:
            if "All" in selected_values:
                return [opt for opt in corr_data.columns if opt not in ['Gender', 'Age_Group', 'Country', 'Year']]
        return selected_values

    # Filter dataset and update heatmap
    @app.callback(
        Output('heatmap', 'figure'),
        Input('year-dropdown-corr', 'value'),
        Input('country-dropdown-corr', 'value'),
        Input('heatmap-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_heatmap(year, countries, selected_features):
        """
            Updates the correlation heatmap based on selected filters and features.

            Args:
                year (str or int): Selected year or 'All'
                countries (str): Selected country or 'All'
                selected_features (list): List of features to include in the heatmap

            Returns:
                go.Figure: Updated correlation heatmap figure
            """
        if len(selected_features) < 1:
            return go.Figure()

        # Use cached filtered data
        filtered_df = filter_heatmap_data(year, countries)

        # Compute correlation matrix
        correlation_matrix = filtered_df[selected_features].corr()
        nan_mask = correlation_matrix.isna()
        nan_correlations = nan_mask.sum().sum() - len(selected_features)

        fig = px.imshow(correlation_matrix,
                        labels=dict(color="Correlation"),
                        x=selected_features,
                        y=selected_features,
                        color_continuous_scale="RdBu_r",
                        zmin=-1, zmax=1)

        if nan_correlations > 0:
            fig.add_annotation(
                xref='paper', yref='paper',
                x=0.5, y=-0.1,
                text=f"Warning: {nan_correlations} correlation(s) could not be calculated due to insufficient variance",
                showarrow=False,
                font=dict(color='red'),
                align='center'
            )

        fig.update_layout(
            title="Feature Correlation Heatmap",
            height=550,
            margin=dict(l=0, r=0, t=50, b=0),
            annotations=[
                dict(
                    text="NaN indicates insufficient variance" if nan_correlations > 0 else "",
                    xref='paper',
                    yref='paper',
                    x=0.5,
                    y=-0.15,
                    showarrow=False,
                    font=dict(color='red')
                )
            ]
        )
        return fig

    # Update scatterplot based on filters
    @app.callback(
        Output('scatterplot-corr', 'figure'),
        Input('year-dropdown-corr', 'value'),
        Input('country-dropdown-corr', 'value'),
        Input('scatter-dropdown-x', 'value'),
        Input('scatter-dropdown-y', 'value')
    )
    def update_scatter(year, countries, x_feature, y_feature):
        """
           Updates the scatter plot based on selected filters and features.

           Args:
               year (str or int): Selected year or 'All'
               countries (str): Selected country or 'All'
               x_feature (str): Feature name for x-axis
               y_feature (str): Feature name for y-axis

           Returns:
               go.Figure: Updated scatter plot figure
           """
        if not x_feature or not y_feature:
            return go.Figure()

        # Use cached filtered data
        filtered_df = filter_scatter_data(year, countries, x_feature, y_feature)

        # If the user selects the same feature for both axes, create a temporary copy
        if x_feature == y_feature:
            filtered_df = filtered_df.copy()  # avoid SettingWithCopyWarning
            filtered_df[f"{y_feature}_y"] = filtered_df[y_feature]
            filtered_df[f"{x_feature}_x"] = filtered_df[x_feature]
            y_to_plot = f"{y_feature}_y"
            x_to_plot = f"{x_feature}_x"
        else:
            y_to_plot = y_feature
            x_to_plot = x_feature

        fig = px.scatter(filtered_df, x=x_to_plot, y=y_to_plot, color='Country',
                         title=f"{x_feature} vs {y_feature}", hover_data=['Country'], trendline="ols")
        fig.update_layout(height=500)
        return fig

    # callback to update sankey diagram with filter
    @app.callback(
        Output('sankey-diagram', 'figure'),
        Input('sankey-dropdown', 'value')
    )
    def update_sankey(target):
        """
           Updates the Sankey diagram based on selected target variable.

           Args:
               target (str): Selected target variable ('PrevalenceRate', 'MortalityRate', or 'IncidenceRate')

           Returns:
               go.Figure: Updated Sankey diagram figure
           """
        return create_sankey(target)


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
