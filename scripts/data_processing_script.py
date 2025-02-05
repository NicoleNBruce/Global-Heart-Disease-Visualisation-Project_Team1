import pandas as pd
import numpy as np
import pycountry
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, LabelEncoder
from sklearn.linear_model import LinearRegression
from numpy.polynomial.polynomial import Polynomial
import os


class DataProcessor:
    """
    A class to process and clean various health-related datasets.
    Handles data from multiple sources including obesity, physical activity, GDP,
    diabetes, alcohol consumption, and disease metrics.
    """

    def __init__(self):
        self.region_mapping = {
            "Aruba": "Caribbean small states", "Bermuda": "Caribbean small states",
            "Cayman Islands": "Caribbean small states", "Curacao": "Caribbean small states",
            "Turks & Cacaos Islands": "Caribbean small states",
            "British Virgin Islands": "Caribbean small states",
            "Virgin Islands (U.S.)": "Caribbean small states",
            "Montenegro": "Europe and Central Asia (excluding high income)",
            "Kosovo": "Europe and Central Asia (excluding high income)",
            "Monaco": "Europe and Central Asia", "Channel Islands": "Europe and Central Asia",
            "Faroe Islands": "Europe and Central Asia", "Gibraltar": "Europe and Central Asia",
            "Isle of Man": "Europe and Central Asia", "Liechtenstein": "Europe and Central Asia",
            "San Marino": "Europe and Central Asia", "American Samoa": "Pacific island small states",
            "Marshall Islands": "Pacific island small states",
            "Northern Mariana Islands": "Pacific island small states",
            "Palau": "Pacific island small states",
            "French Polynesia": "Pacific island small states",
            "New Caledonia": "Pacific island small states",
            "Guam": "Pacific island small states",
            "Macao SAR, China": "East Asia and Pacific",
            "Hong Kong SAR, China": "East Asia and Pacific",
            "West Bank and Gaza": "Middle East and North Africa",
            "South Sudan": "Sub-Saharan Africa",
            "Greenland": "High income"
        }

        self.country_code_dict = {
            'Bolivia (Plurinational State of)': 'BOL',
            'Democratic Republic of the Congo': 'COD',
            'Iran (Islamic Republic of)': 'IRN',
            'Micronesia (Federated States of)': 'FSM',
            'Palestine': 'PSE',
            'Republic of Korea': 'KOR',
            'Republic of Niue': 'NIU',
            'Taiwan (Province of China)': 'TWN',
            'The former Yugoslav Republic of Macedonia': 'MKD',
            'Turkey': 'TUR',
            'United States Virgin Islands': 'VIR',
            'Venezuela (Bolivarian Republic of)': 'VEN',
            'Bolivarian Republic of Venezuela': 'VEN',
            'Commonwealth of the Bahamas': 'BHS',
            'Czech Republic': 'CZE',
            "Democratic People's Republic of Korea": 'PRK',
            'Federated States of Micronesia': 'FSM',
            'Islamic Republic of Iran': 'IRN',
            'Kingdom of Eswatini': 'SWZ',
            'Plurinational State of Bolivia': 'BOL',
            'Principality of Monaco': 'MCO',
            'Republic of Cabo Verde': 'CPV',
            "Republic of Côte d'Ivoire": 'CIV',
            'Republic of Moldova': 'MDA',
            'Republic of Nauru': 'NRU',
            'Republic of Palau': 'PLW',
            'Republic of San Marino': 'SMR',
            'Republic of the Gambia': 'GMB',
            'Socialist Republic of Viet Nam': 'VNM',
            'United Kingdom of Great Britain and Northern Ireland': 'GBR',
            'United Republic of Tanzania': 'TZA',
            'United States of America': 'USA',
            'Republic of the Philippines': 'PHL',
            'Republic of the Union of Myanmar': 'MMR',
            'Republic of Maldives': 'MDV',
            'Republic of Indonesia': 'IDN',
            'Kingdom of Tonga': 'TON',
            'Republic of Vanuatu': 'VUT',
            "People's Republic of China": 'CHN',
            'Kingdom of Cambodia': 'KHM',
            'Independent State of Samoa': 'WSM',
            'Independent State of Papua New Guinea': 'PNG',
            'Republic of Kiribati': 'KIR',
            'Republic of Fiji': 'FJI',
            'Republic of the Marshall Islands': 'MHL',
            'Republic of Tajikistan': 'TJK',
            'Democratic Republic of Timor-Leste': 'TLS',
            'Republic of Kazakhstan': 'KAZ',
            'Republic of Bulgaria': 'BGR',
            'Kingdom of Thailand': 'THA',
            'Republic of Croatia': 'HRV',
            'Republic of Albania': 'ALB',
            'Kyrgyz Republic': 'KGZ',
            'Republic of Uzbekistan': 'UZB',
            'Republic of Azerbaijan': 'AZE',
            'Democratic Socialist Republic of Sri Lanka': 'LKA',
            'Republic of Armenia': 'ARM',
            'Republic of Lithuania': 'LTU',
            'Republic of Estonia': 'EST',
            'Republic of Belarus': 'BLR',
            'Republic of Latvia': 'LVA',
            'Republic of Slovenia': 'SVN',
            'Principality of Andorra': 'AND',
            'Kingdom of Belgium': 'BEL',
            'Slovak Republic': 'SVK',
            'Republic of Austria': 'AUT',
            'Republic of Finland': 'FIN',
            'Republic of Serbia': 'SRB',
            'Kingdom of Denmark': 'DNK',
            'Republic of Cyprus': 'CYP',
            'French Republic': 'FRA',
            'Republic of Poland': 'POL',
            'Republic of Singapore': 'SGP',
            'Swiss Confederation': 'CHE',
            'Kingdom of Spain': 'ESP',
            'Kingdom of Sweden': 'SWE',
            'Portuguese Republic': 'PRT',
            'Kingdom of Norway': 'NOR',
            'Kingdom of the Netherlands': 'NLD',
            'Grand Duchy of Luxembourg': 'LUX',
            'Republic of Malta': 'MLT',
            'Republic of Italy': 'ITA',
            'State of Israel': 'ISR',
            'Hellenic Republic': 'GRC',
            'Republic of Iceland': 'ISL',
            'Federal Republic of Germany': 'DEU',
            'Republic of Cuba': 'CUB',
            'Commonwealth of Dominica': 'DMA',
            'Argentine Republic': 'ARG',
            'Republic of Chile': 'CHL',
            'Eastern Republic of Uruguay': 'URY',
            'Republic of Peru': 'PER',
            'Republic of Ecuador': 'ECU',
            'Republic of Suriname': 'SUR',
            'Republic of Trinidad and Tobago': 'TTO',
            'Republic of Guatemala': 'GTM',
            'Republic of Costa Rica': 'CRI',
            'Republic of El Salvador': 'SLV',
            'Republic of Guyana': 'GUY',
            'Republic of Colombia': 'COL',
            'Republic of Haiti': 'HTI',
            'Hashemite Kingdom of Jordan': 'JOR',
            'Republic of Iraq': 'IRQ',
            'Kingdom of Bahrain': 'BHR',
            "People's Democratic Republic of Algeria": 'DZA',
            'Arab Republic of Egypt': 'EGY',
            'Republic of Paraguay': 'PRY',
            'Federative Republic of Brazil': 'BRA',
            'Republic of Panama': 'PAN',
            'United Mexican States': 'MEX',
            'Republic of Nicaragua': 'NIC',
            'Islamic Republic of Afghanistan': 'AFG',
            'Republic of Yemen': 'YEM',
            'Republic of Turkey': 'TUR',
            'Republic of Tunisia': 'TUN',
            'Republic of Honduras': 'HND',
            'State of Qatar': 'QAT',
            'Kingdom of Saudi Arabia': 'SAU',
            'State of Kuwait': 'KWT',
            'Sultanate of Oman': 'OMN',
            'Kingdom of Morocco': 'MAR',
            'State of Libya': 'LBY',
            'Lebanese Republic': 'LBN',
            'Union of the Comoros': 'COM',
            'Republic of Burundi': 'BDI',
            'Islamic Republic of Pakistan': 'PAK',
            'Federal Democratic Republic of Nepal': 'NPL',
            'Republic of India': 'IND',
            "People's Republic of Bangladesh": 'BGD',
            'Republic of Madagascar': 'MDG',
            'Republic of Guinea-Bissau': 'GNB',
            'Republic of Sudan': 'SDN',
            'State of Eritrea': 'ERI',
            'Kingdom of Bhutan': 'BTN',
            'Gabonese Republic': 'GAB',
            'Republic of Botswana': 'BWA',
            'Republic of South Africa': 'ZAF',
            'Republic of Chad': 'TCD',
            'Republic of Kenya': 'KEN',
            'Republic of Cameroon': 'CMR',
            'Republic of Benin': 'BEN',
            'Kingdom of Lesotho': 'LSO',
            'Republic of Ghana': 'GHA',
            'Republic of the Niger': 'NER',
            'Republic of Equatorial Guinea': 'GNQ',
            'Federal Democratic Republic of Ethiopia': 'ETH',
            'Democratic Republic of Sao Tome and Principe': 'STP',
            'Republic of Djibouti': 'DJI',
            'Republic of Zambia': 'ZMB',
            'Republic of Liberia': 'LBR',
            'Republic of the Congo': 'COG',
            'Republic of Mali': 'MLI',
            'Islamic Republic of Mauritania': 'MRT',
            'Republic of Angola': 'AGO',
            'Republic of Mauritius': 'MUS',
            'Republic of Rwanda': 'RWA',
            'Republic of Uganda': 'UGA',
            'Federal Republic of Somalia': 'SOM',
            'Republic of Mozambique': 'MOZ',
            'Republic of Malawi': 'MWI',
            'Republic of Seychelles': 'SYC',
            'Republic of Namibia': 'NAM',
            'Togolese Republic': 'TGO',
            'Republic of Zimbabwe': 'ZWE',
            'Republic of Guinea': 'GIN',
            'Republic of Senegal': 'SEN',
            'Federal Republic of Nigeria': 'NGA',
            'Republic of Sierra Leone': 'SLE',
            'Republic of South Sudan': 'SSD'
        }

    # FUNCTIONS FOR GDP, INSUFFICIENT ACTIVITY AND  OBESITY DATA
    def read_file(self, file, columns_to_keep, new_column_names):
        """
         Read and process an Excel file with standardized formatting.
         """
        df = pd.read_excel(file)
        df.columns = df.iloc[1]
        df = df.drop([0, 1], axis=0).reset_index(drop=True)
        df = df[columns_to_keep]
        df.columns = new_column_names
        return df

    def clean_and_transform(self, df, year_column, rate_column):
        """
        Clean and transform data by converting types and removing duplicates.
        """
        df[year_column] = df[year_column].astype(int)
        df[rate_column] = df[rate_column].astype(float)

        original_len = len(df)
        df = df.drop_duplicates(keep='first')
        rows_removed = original_len - len(df)
        print(f"Rows removed: {rows_removed}")

        return df

    def process_activity_obesity_gdp(self):
        """
              Process and merge physical activity, obesity, and GDP datasets.
              Handles data cleaning, merging, and imputation for these related metrics.
              """
        activity_file = "data/insufficient_physical_activity_data.xlsx"
        obesity_file = "data/obesity_data.xlsx"
        gdp_file = "data/gdp-per-capita-worldbank.csv"

        columns_to_keep = ['Location', 'SpatialDimValueCode', 'Period', 'FactValueNumeric']
        new_column_names = ['Country', 'Code', 'Year', 'Prevalence_Rate']

        activity_prevalence = self.read_file(activity_file, columns_to_keep, new_column_names)
        obesity_prevalence = self.read_file(obesity_file, columns_to_keep, new_column_names)

        activity_prevalence = self.clean_and_transform(activity_prevalence, 'Year', 'Prevalence_Rate')
        obesity_prevalence = self.clean_and_transform(obesity_prevalence, 'Year', 'Prevalence_Rate')

        gdp_data = pd.read_csv(gdp_file)
        gdp_data.rename(columns={
            'Entity': 'Country',
            'GDP per capita, PPP (constant 2017 international $)': 'GDP'
        }, inplace=True)
        gdp_data = gdp_data.dropna(subset=['Code'])

        final_df = self._merge_and_impute_activity_obesity(activity_prevalence, obesity_prevalence, gdp_data)
        return final_df

    def _merge_and_impute_activity_obesity(self, df1, df2, df3):
        """Merge and impute activity, obesity and GDP data"""
        # Rename columns for clarity
        df1.rename(columns={'Prevalence_Rate': 'Activity_Prevalence_Rate'}, inplace=True)
        df2.rename(columns={'Prevalence_Rate': 'Obesity_Prevalence_Rate'}, inplace=True)

        # Merge DataFrames
        merged_df = pd.merge(df1, df2, on=['Country', 'Code', 'Year'], how='outer')
        merged_df = pd.merge(merged_df, df3, on=['Country', 'Code', 'Year'], how='outer')
        merged_df = merged_df[merged_df['Country'] != 'World']

        # Apply KNN imputation
        knn_imputer = KNNImputer(n_neighbors=5)
        columns_to_impute = ['Activity_Prevalence_Rate', 'Obesity_Prevalence_Rate', 'GDP']
        merged_df[columns_to_impute] = knn_imputer.fit_transform(merged_df[columns_to_impute])

        return merged_df

    # FUNCTIONS FOR DIABETES AND ALCOHOL DATASETS
    def _diabetes_column_processing(self, df):
        """
        Process diabetes-specific columns and encode categorical variables.
        Removes unnecessary columns and standardizes data format.
        """
        df = df.rename(columns={
            'Country/Region/World': 'Location',
            'ISO': 'Code',
            'Sex': 'Gender'
        })
        df["Gender"] = df["Gender"].map({"Men": 0, "Women": 1})
        columns_to_drop = [
            'Age',
            'Prevalence of diabetes (18+ years) lower 95% uncertainty interval',
            'Prevalence of diabetes (18+ years) upper 95% uncertainty interval',
            'Proportion of people with diabetes who were treated (30+ years)',
            'Proportion of people with diabetes who were treated (30+ years) lower 95% uncertainty interval',
            'Proportion of people with diabetes who were treated (30+ years) upper 95% uncertainty interval'
        ]
        df = df.drop(columns_to_drop, axis=1)
        return df

    def _adding_missing_years(self, df):
        """
        Add missing years to dataset with placeholder values.
        Fills gaps in time series data from 1960 to 1990.
        """
        years_1980_to_1989 = list(range(1960, 1990))
        countries = df['Location'].unique()
        new_rows = []

        for country in countries:
            for year in years_1980_to_1989:
                new_row = {
                    'Location': country,
                    'Year': year,
                    'Code': df[df['Location'] == country]['Code'].iloc[0]
                }

                for col in df.columns:
                    if col not in ['Location', 'Year', 'Code']:
                        new_row[col] = float('nan')

                new_rows.append(new_row)

        new_data = pd.DataFrame(new_rows)
        df = pd.concat([df, new_data], ignore_index=True)
        df = df.sort_values(by=['Location', 'Year']).reset_index(drop=True)
        return df

    def _impute_diabetes_data(self, df):
        """
        Impute missing diabetes prevalence data using polynomial fitting.
        Fits a second-degree polynomial to existing data points.
        """
        known_data = df[df["Prevalence of diabetes (18+ years)"].notnull()]
        known_years = known_data["Year"]
        known_prevalence = known_data["Prevalence of diabetes (18+ years)"]

        poly = Polynomial.fit(known_years, known_prevalence, deg=2)
        df["Prevalence of diabetes (18+ years)"] = poly(df["Year"])

        return df

    def _convert_year_to_int(self, df, column_name='Year'):
        """
        Convert year column to integer type.
        """
        df[column_name] = df[column_name].astype(int)
        return df

    def _impute_alcohol_data(self, alcohol_data):
        """Impute missing alcohol data using KNN"""
        # Create numerical representations for categorical columns
        location_mapping = {loc: i for i, loc in enumerate(alcohol_data['Location'].unique())}
        code_mapping = {code: i for i, code in enumerate(alcohol_data['Code'].unique())}

        alcohol_data['Location_Num'] = alcohol_data['Location'].map(location_mapping)
        alcohol_data['Code_Num'] = alcohol_data['Code'].map(code_mapping)

        # Prepare data for imputation
        features = ['Location_Num', 'Code_Num', 'Year', 'Alcohol_Value']
        data_for_imputation = alcohol_data[features]

        # Scale the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data_for_imputation)

        # Apply KNN imputation
        imputer = KNNImputer(n_neighbors=5)
        imputed_data = imputer.fit_transform(scaled_data)

        # Transform back to original scale
        imputed_data_original_scale = scaler.inverse_transform(imputed_data)
        alcohol_data['Alcohol_Value'] = imputed_data_original_scale[:, 3]

        # Clean up temporary columns
        alcohol_data.drop(['Location_Num', 'Code_Num'], axis=1, inplace=True)

        return alcohol_data

    def impute_with_polynomial(self, df, year_col, target_col, degree=2):
        """
        Impute missing values using polynomial regression on time series.
        """
        known_data = df[df[target_col].notnull()]
        known_years = known_data[year_col]
        known_values = known_data[target_col]

        missing_data = df[df[target_col].isnull()]
        missing_years = missing_data[year_col]

        # Fit a polynomial to the known data
        poly = Polynomial.fit(known_years, known_values, deg=degree)

        # Predict missing values
        predicted_values = poly(missing_years)

        # Fill in the missing values
        df.loc[df[target_col].isnull(), target_col] = predicted_values
        return df

    def process_diabetes_alcohol(self, diabetes_data, alcohol_data):
        """
        Process and merge diabetes and alcohol consumption datasets.
        Includes data cleaning, imputation, and regional value filling.
        """
        diabetes_processed = self._diabetes_column_processing(diabetes_data)
        diabetes_processed = self._adding_missing_years(diabetes_processed)
        diabetes_processed = self._impute_diabetes_data(diabetes_processed)

        # Process alcohol data
        alcohol_processed = alcohol_data.melt(id_vars=['Location', 'Code'], var_name='Year', value_name='Alcohol_Value')
        alcohol_processed = self._convert_year_to_int(alcohol_processed)
        alcohol_processed = self._remove_wrong_countries(alcohol_processed)
        alcohol_processed = self._fill_missing_values_with_regional(alcohol_processed,
                                                                    self.region_mapping)
        alcohol_processed = self._impute_alcohol_data(alcohol_processed)
        merged_data = diabetes_processed.merge(alcohol_processed, on=['Location', 'Year', 'Code'], how='outer')
        return merged_data

    def _remove_wrong_countries(self, df, column_name='Location'):
        """Remove non-country entries from the dataset"""
        wrong_countries = [
            'The Arab World', 'Central Europe and the Baltics', 'Channel Islands',
            'Caribbean small states', 'East Asia and Pacific (excluding high income)',
            'Early-demographic dividend', 'East Asia and Pacific',
            'Europe and Central Asia (excluding high income)', 'Europe and Central Asia',
            'Euro area', 'European Union', 'Fragile and conflict-affected situations',
            'High income', 'Heavily indebted poor countries (HIPC)', 'IBRD only',
            'IBRD and IDA', 'IDA total', 'IDA blend', 'IDA only', 'Not classified',
            'Latin America and the Caribbean (excluding high income)',
            'Latin America and the Caribbean', 'Least developed countries: UN classification',
            'Low income', 'Lower middle income', 'Low and middle income',
            'Late-demographic dividend', 'Middle East and North Africa',
            'Middle income', 'Middle East and North Africa (excluding high income)',
            'North America', 'OECD members', 'Other small states', 'Pre-demographic dividend',
            'Pacific island small states', 'Post-demographic dividend', 'South Asia',
            'Sub-Saharan Africa (excluding high income)', 'Sub-Saharan Africa',
            'Small states', 'East Asia and Pacific (IBRD and IDA)',
            'Europe and Central Asia (IBRD and IDA)', 'Latin America and the Caribbean (IBRD and IDA)',
            'Middle East and North Africa (IBRD and IDA)', 'South Asia (IBRD and IDA)',
            'Sub-Saharan Africa (IBRD and IDA)', 'Upper middle income', 'World'
        ]
        df = df[~df[column_name].isin(wrong_countries)]
        df.reset_index(drop=True, inplace=True)
        return df

    def _fill_missing_values_with_regional(self, df, region_mapping, value_column='Alcohol_Value',
                                           location_column='Location', year_column='Year'):
        """Fill missing values using regional data"""
        df_filled = df.copy()

        for country, region in region_mapping.items():
            if country in df_filled[location_column].values:
                country_data = df_filled[df_filled[location_column] == country]
                missing_years = country_data[country_data[value_column].isnull()][year_column].unique()

                if len(missing_years) > 0:
                    regional_data = df_filled[df_filled[location_column] == region]
                    regional_values = \
                        regional_data[regional_data[year_column].isin(missing_years)].set_index(year_column)[
                            value_column]

                    for year in missing_years:
                        df_filled.loc[
                            (df_filled[location_column] == country) &
                            (df_filled[year_column] == year),
                            value_column
                        ] = regional_values.get(year)

        return df_filled

    # FUNCTIONS FOR HDB PREVALENCE, INCIDENCE AND MORTALITY RATE DATA
    def encode_categorical_columns(self, df, columns):
        encoder = LabelEncoder()
        for col in columns:
            df[col] = encoder.fit_transform(df[col].astype(str))
        return df

    def _impute_with_polynomial_fit(self, df, target_column, predictor_columns, degree=2):
        """Imputes missing values in the target column using polynomial regression."""

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected a DataFrame, but got {type(df)} instead.")

        if target_column not in df.columns:
            raise ValueError(f"Column '{target_column}' not found in DataFrame.")

        if df[target_column].isnull().sum() == 0:
            print(f"No missing values in '{target_column}'. Skipping imputation.")
            return df  # No need to modify anything

        if any(col not in df.columns for col in predictor_columns):
            raise ValueError(f"Predictor columns {predictor_columns} not found in DataFrame.")

        # Separate rows with missing and non-missing values
        missing_mask = df[target_column].isnull()
        df_valid = df.dropna(subset=predictor_columns)

        if df_valid.empty:
            print(f"Skipping imputation for '{target_column}' due to missing predictors.")
            return df

        # Train polynomial regression model
        X_train = df_valid.loc[~missing_mask, predictor_columns]
        y_train = df_valid.loc[~missing_mask, target_column]

        poly = PolynomialFeatures(degree=degree)
        X_train_poly = poly.fit_transform(X_train)

        model = LinearRegression()
        model.fit(X_train_poly, y_train)

        # Predict missing values
        X_missing_poly = poly.transform(df.loc[missing_mask, predictor_columns])
        df.loc[missing_mask, target_column] = np.maximum(model.predict(X_missing_poly), 0)  # No negatives

        return df

    def get_country_code(self, country_name):
        """Returns the ISO Alpha-3 country code given a country name, using a dictionary first and falling back to pycountry."""
        # Normalize the country name format
        country_name_normalized = country_name.strip().title()

        # Check if the country name exists in the predefined dictionary
        if country_name_normalized in self.country_code_dict:
            return self.country_code_dict[country_name_normalized]

        # Fallback to pycountry if not found in the dictionary
        try:
            country = pycountry.countries.lookup(country_name_normalized)
            return country.alpha_3
        except LookupError:
            return None

    def process_disease_metrics(self, incidence_data, mortality_data, prevalence_data):
        """
           Process disease metrics including incidence, mortality, and prevalence.
           Standardizes column names and merges multiple disease metrics datasets.
           """
        dfs = {
            'incidence': (incidence_data, 'IncidenceRate'),
            'mortality': (mortality_data, 'MortalityRate'),
            'prevalence': (prevalence_data, 'PrevalenceRate')
        }

        processed_dfs = []
        for name, (df, rate_col) in dfs.items():
            processed_df = df.rename(columns={
                'location_name': 'Country',
                'sex_name': 'Gender',
                'age_name': 'Age_Group',
                'year': 'Year',
                'val': rate_col
            })
            processed_df = processed_df[['Country', 'Gender', 'Year', 'Age_Group', rate_col]]
            processed_dfs.append(processed_df)

        # Merge datasets
        df_combined = pd.merge(processed_dfs[0], processed_dfs[1],
                               on=['Country', 'Year', 'Gender', 'Age_Group'],
                               how='outer')
        df_combined = pd.merge(df_combined, processed_dfs[2],
                               on=['Country', 'Year', 'Gender', 'Age_Group'],
                               how='outer')

        df_combined = self.encode_categorical_columns(df_combined, ['Gender', 'Age_Group'])

        # Impute missing values
        for rate in ['IncidenceRate', 'PrevalenceRate', 'MortalityRate']:
            df_combined = self._impute_with_polynomial_fit(df_combined, rate, ['Year'])

        # Add country codes
        df_combined['Country'] = df_combined['Country'].astype(str).str.strip()
        df_combined['Country_Code'] = df_combined['Country'].apply(self.get_country_code)
        return df_combined

    # FUNCTIONS FOR OVERWEIGHT AND WORLD HEALTH DATASETS

    def _clean_overweight_data(self, df):
        """Clean and preprocess the overweight dataset"""
        # Select and rename relevant columns
        df.columns = df.iloc[1]
        df = df.drop([0, 1], axis=0).reset_index(drop=True)
        df = df[['SpatialDimValueCode', 'Location', 'Period', 'FactValueNumeric']]
        df = df.rename(columns={
            'SpatialDimValueCode': 'Country_code',
            'Location': 'Country',
            'Period': 'Year',
            'FactValueNumeric': 'Overweight_Prevalence'
        })
        return df

    def _clean_world_health_data(self, df):
        """Clean and preprocess the world health dataset"""
        # Drop specific years with incomplete data
        years_to_drop = [1999, 2022, 2023]
        df = df[~df['year'].isin(years_to_drop)]

        # Remove non-country territories and regions
        countries_to_remove = [
            "American Samoa", "Aruba", "Bermuda", "British Virgin Islands",
            "Cayman Islands", "Channel Islands", "Curacao", "Faroe Islands",
            "French Polynesia", "Gibraltar", "Greenland", "Guam",
            "Hong Kong SAR, China", "Isle of Man", "Korea, Dem. People's Rep.",
            "Kosovo", "Liechtenstein", "Macao SAR, China", "New Caledonia",
            "Northern Mariana Islands", "Not classified", "Puerto Rico",
            "Sint Maarten (Dutch part)", "Somalia", "St. Martin (French part)",
            "Turks and Caicos Islands", "Virgin Islands (U.S.)", "West Bank and Gaza"
        ]
        df = df[~df['country'].isin(countries_to_remove)]

        # Get valid ISO country codes
        valid_country_codes = {country.alpha_3 for country in pycountry.countries}
        df = df[df['country_code'].isin(valid_country_codes)]

        # Handle missing values
        df['health_exp'] = df.groupby('country_code')['health_exp'].ffill()
        df['health_exp'] = df.groupby('country_code')['health_exp'].bfill()
        df['life_expect'] = df.groupby('country_code')['life_expect'].ffill()
        df['life_expect'] = df.groupby('country_code')['life_expect'].bfill()

        # Select and rename columns
        df = df.iloc[:, :5]
        df = df.rename(columns={
            'country_code': 'Country_code',
            'country': 'Country',
            'year': 'Year',
            'health_exp': 'Health_Expenditure',
            'life_expect': 'Life_Expectancy'
        })

        return df

    def _process_supplemental_life_expectancy(self, df):
        """Process supplemental life expectancy data from WHO"""
        # Select relevant columns and filter for total population
        df = df[['SpatialDimValueCode', 'Dim1ValueCode', 'FactValueNumeric', 'Period']]
        df = df[df['Dim1ValueCode'] == 'SEX_BTSX']
        df = df.drop(columns=['Dim1ValueCode'])

        # Rename columns
        df = df.rename(columns={
            'SpatialDimValueCode': 'Country_code',
            'Period': 'Year',
            'FactValueNumeric': 'Imputed_Life_Expectancy'
        })

        return df

    def _merge_and_clean_datasets(self, overweight_df, world_df, life_expectancy_df):
        """Merge all datasets and perform final cleaning"""
        # Initial merge of overweight and world health data
        overweight_df['Year'] = overweight_df['Year'].astype(int)
        merged_df = pd.merge(
            overweight_df,
            world_df,
            on=['Country_code', 'Country', 'Year'],
            how='left'
        )

        # Convert year to numeric
        merged_df['Year'] = merged_df['Year'].astype(int)
        life_expectancy_df['Year'] = life_expectancy_df['Year']

        # Fill missing life expectancy values with supplemental data
        for index, row in life_expectancy_df.iterrows():
            mask = (
                    (merged_df['Country_code'] == row['Country_code']) &
                    (merged_df['Year'] == row['Year']) &
                    (merged_df['Life_Expectancy'].isna())
            )
            merged_df.loc[mask, 'Life_Expectancy'] = row['Imputed_Life_Expectancy']

        # Final interpolation for remaining missing values
        merged_df['Life_Expectancy'] = merged_df['Life_Expectancy'].interpolate(
            method='linear')
        merged_df['Health_Expenditure'] = merged_df['Health_Expenditure'].interpolate(
            method='linear')

        return merged_df

    def process_overweight_health(self, overweight_data, world_health_data, life_expectancy_data):
        """
        Process and merge overweight, health, and life expectancy datasets.
        """
        cleaned_overweight = self._clean_overweight_data(overweight_data)
        cleaned_world_health = self._clean_world_health_data(world_health_data)
        processed_life_expectancy = self._process_supplemental_life_expectancy(life_expectancy_data)

        return self._merge_and_clean_datasets(cleaned_overweight,
                                              cleaned_world_health,
                                              processed_life_expectancy)


def main():
    # Create a new directory named 'datasets'
    os.mkdir('datasets')

    """Main function to run all data processing"""
    # Initialize processor
    processor = DataProcessor()

    try:
        # 1. Process Activity, Obesity, and GDP data
        print("Processing Activity, Obesity, and GDP data...")
        activity_obesity_gdp_df = processor.process_activity_obesity_gdp()

        activity_obesity_gdp_df.to_csv('datasets/processed_activity_obesity_gdp.csv', index=False)
        print("Activity, Obesity, and GDP data processing completed.")

        # 2. Process Diabetes and Alcohol data
        print("\nProcessing Diabetes and Alcohol data...")
        diabetes_data = pd.read_csv('data/diabetes_data.csv')
        alcohol_data = pd.read_excel('data/alcohol_consumption.xlsx')

        diabetes_alcohol = processor.process_diabetes_alcohol(diabetes_data, alcohol_data)
        diabetes_alcohol_df = processor.impute_with_polynomial(diabetes_alcohol, year_col="Year",
                                                               target_col="Alcohol_Value", degree=2)
        diabetes_alcohol_df = processor.impute_with_polynomial(diabetes_alcohol, year_col="Year",
                                                               target_col="Prevalence of diabetes (18+ years)",
                                                               degree=2)

        diabetes_alcohol_df.to_csv('datasets/processed_diabetes_alcohol.csv', index=False)
        print("Diabetes and Alcohol data processing completed.")

        # 3. Process Disease Metrics data
        print("\nProcessing Disease Metrics data...")
        incidence_data = pd.read_csv('data/GBD_INCIDENCE.csv')
        mortality_data = pd.read_csv('data/GBD_MORTALITY-DEATHS.csv')
        prevalence_data = pd.read_csv('data/GBD_PREVALENCE.csv')
        disease_metrics_df = processor.process_disease_metrics(
            incidence_data, mortality_data, prevalence_data)

        disease_metrics_df.to_csv('datasets/processed_disease_metrics.csv', index=False)
        print("Disease Metrics data processing completed.")

        # 4. Process Overweight and World Health data
        print("\nProcessing Overweight and World Health data...")
        overweight_data = pd.read_excel('data/overweight.xlsx')
        world_health_data = pd.read_csv('data/world_health_data.csv')
        life_expectancy_data = pd.read_csv('data/life_expectancy.csv')

        health_data_df = processor.process_overweight_health(
            overweight_data, world_health_data, life_expectancy_data)

        health_data_df.to_csv('datasets/processed_health_data.csv', index=False)
        print("Overweight and World Health data processing completed.")

        print("\nAll data processing completed successfully!")

    except Exception as e:
        print(f"An error occurred during processing: {str(e)}")
        raise


if __name__ == "__main__":
    main()

