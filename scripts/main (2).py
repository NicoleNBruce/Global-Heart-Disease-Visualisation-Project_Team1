import pandas as pd
from sklearn.impute import KNNImputer

# Load datasets
print("Loading datasets...")
weight_health_exp_df = pd.read_csv('datasets/processed_health_data.csv')
diabetes_alcohol_df = pd.read_csv('datasets/processed_diabetes_alcohol.csv')
gdp_obesity_physical_df = pd.read_csv('datasets/processed_activity_obesity_gdp.csv')
heart_disease_df = pd.read_csv('datasets/processed_disease_metrics.csv')
print("Datasets loaded successfully.\n")

# Rename columns for consistency
weight_health_exp_df.rename(columns={'Country_code': 'Country_Code'}, inplace=True)
diabetes_alcohol_df.rename(columns={
    'Code': 'Country_Code',
    'Location': 'Country',
    'Prevalence of diabetes (18+ years)': 'Diabetes_Prevalence_Rate'
}, inplace=True)
gdp_obesity_physical_df.rename(columns={'Code': 'Country_Code'}, inplace=True)
heart_disease_df.rename(columns={
    'Sex': 'Gender',
    'Country Code': 'Country_Code',
    'age_name': 'Age_Group'
}, inplace=True)
print("Columns renamed successfully.\n")

# Map gender binary values to descriptive strings
print("Mapping gender values...")
diabetes_alcohol_df['Gender'] = diabetes_alcohol_df['Gender'].map({0: 'Male', 1: 'Female'})
print("Gender values mapped successfully.\n")

# Merge datasets
print("Merging datasets...")
merged_df = pd.merge(heart_disease_df, diabetes_alcohol_df, on=['Country_Code', 'Country', 'Year', 'Gender'], how='outer')
merged_df = pd.merge(merged_df, gdp_obesity_physical_df, on=['Country_Code', 'Country', 'Year'], how='outer')
merged_df = pd.merge(merged_df, weight_health_exp_df, on=['Country_Code', 'Country', 'Year'], how='outer')
print("Datasets merged successfully.\n")

# Function to apply KNN imputation
def impute_with_knn(df, target_col, n_neighbors=5):
    """
    Impute missing values in a column using KNN imputation.

    Parameters:
    - df (DataFrame): The input DataFrame.
    - target_col (str): The name of the column to impute.
    - n_neighbors (int): Number of neighbors to use for imputation.

    Returns:
    - DataFrame: A DataFrame with the missing values imputed.
    """
    print(f"Imputing missing values for '{target_col}'...")
    original_index = df.index
    feature_cols = df.columns.difference(['Country', 'Country_Code', 'Age_Group', 'Gender', target_col])
    impute_cols = feature_cols.append(pd.Index([target_col]))

    impute_data = df[impute_cols].copy()
    imputer = KNNImputer(n_neighbors=n_neighbors)
    imputed_array = imputer.fit_transform(impute_data)

    imputed_df = pd.DataFrame(imputed_array, columns=impute_cols)
    imputed_df.index = original_index

    df[target_col] = imputed_df[target_col]
    print(f"Missing values for '{target_col}' imputed successfully.\n")
    return df

# List of columns to impute
columns_to_impute = [
    'Alcohol_Value', 'IncidenceRate', 'PrevalenceRate', 'MortalityRate',
    'Diabetes_Prevalence_Rate', 'Activity_Prevalence_Rate',
    'Obesity_Prevalence_Rate', 'GDP', 'Health_Expenditure (% of GDP)',
    'Life_Expectancy'
]

# Apply imputation
for col in columns_to_impute:
    merged_df = impute_with_knn(merged_df, target_col=col)

# Set negative GDP values to NaN
print("Checking for invalid GDP values...")
merged_df.loc[merged_df['GDP'] < 0, 'GDP'] = None
print("Invalid GDP values handled successfully.\n")

# Drop unnecessary column
if 'BMI' in merged_df.columns:
    print("Dropping 'BMI' column...")
    merged_df.drop('BMI', axis=1, inplace=True)
    print("'BMI' column dropped successfully.\n")

# Save cleaned data to CSV
print("Saving cleaned data to CSV...")
merged_df.to_csv('cleaned_final_data.csv', index=False)
print("Data saved successfully as 'cleaned_final_data.csv'.\n")

print("Data merging and imputation process completed successfully!")
