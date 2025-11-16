import geopandas as gpd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def feature_engineering(df, lag_y = 4):
    # Example feature engineering: create lag features for given columns
    lag_features = ['beftotalt', 'rutstorl_kommun_sum', 'beftotalt_kommun_sum',
       'rutstorl_regso_sum', 'beftotalt_regso_sum', 'kids_population',
       'adult_population', 'senior_population', 'kids_population_kommun_sum',
       'adult_population_kommun_sum', 'senior_population_kommun_sum',
       'kids_population_regso_sum', 'adult_population_regso_sum',
       'senior_population_regso_sum']
    #target year is the current year column
    for feature in lag_features:
        for lag in range(2, lag_y + 2): 
            df[f'{feature}_lag_{lag}'] = df[feature].shift(lag)
    
    # Drop rows with NaN values created by lag features
    df = df.dropna().reset_index(drop=True)
    return df

# feature engineer for prediction dataset
def feature_engineering_prediction(df, lag_y = 4,  predict_years = 2024):
    lag_features = ['beftotalt', 'rutstorl_kommun_sum', 'beftotalt_kommun_sum',
       'rutstorl_regso_sum', 'beftotalt_regso_sum', 'kids_population',
       'adult_population', 'senior_population', 'kids_population_kommun_sum',
       'adult_population_kommun_sum', 'senior_population_kommun_sum',
       'kids_population_regso_sum', 'adult_population_regso_sum',
       'senior_population_regso_sum']
   
    for feature in lag_features:
        for lag in range(2, lag_y + 2): 
            df[f'{feature}_lag_{lag}'] = df[feature].shift(lag-2)
    
    df = df[df['year'] == predict_years]
    df = df.dropna().reset_index(drop=True)
    return df

def run_xgboost_forecast(df, target_column, feature_columns, n_estimators=100, learning_rate=0.1, evaluate=True):

    # Split the data into training and testing sets
    X = df[feature_columns]
    y = df[target_column]

    #split based on year if evaluate is true, where test set is the last year
    if evaluate:
        train_years = df['year'] < df['year'].max()
        test_years = df['year'] == df['year'].max()
        X_train, X_test = X[train_years], X[test_years]
        y_train, y_test = y[train_years], y[test_years]
    else:
        X_train, y_train = X, y

    # Initialize the XGBoost regressor
    model = XGBRegressor(n_estimators=n_estimators, learning_rate=learning_rate, random_state=42)

    # Fit the model to the training data
    model.fit(X_train, y_train)

    # Calculate the mean squared error
    if evaluate:
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Mean Squared Error: {mse}")

    return model

def percent_increase(gdf_predictions_aggregated, gdf_with_all):
    #get the increase in population per region compared to the original 2024 data
    gdf_2024 = gdf_with_all[gdf_with_all['year'] == 2024]
    gdf_2024_agg = gdf_2024.groupby('kommunnamn')[['kids_population', 'adult_population', 'senior_population']].sum().reset_index()
    gdf_comparison = gdf_2024_agg.merge(gdf_predictions_aggregated, on='kommunnamn', how='left')
    gdf_comparison['kids_population_increase_p'] = (gdf_comparison['kids_population_pred'] - gdf_comparison['kids_population']) / gdf_comparison['kids_population'] * 100
    gdf_comparison['adult_population_increase_p'] = (gdf_comparison['adult_population_pred'] - gdf_comparison['adult_population']) / gdf_comparison['adult_population'] * 100
    gdf_comparison['senior_population_increase_p'] = (gdf_comparison['senior_population_pred'] - gdf_comparison['senior_population']) / gdf_comparison['senior_population'] * 100
    return gdf_comparison

def main():
    #import gdf_with_all from geoparquet
    directory = "./data/geoparquet/"
    gdf_with_all = gpd.read_parquet(directory + "befolkning_1km_2015_2024_regso_kommun_aggregated.parquet")

    #feature engineering
    gdf_fe = feature_engineering(gdf_with_all, lag_y=4)

    # Define target and feature columns
    kids = 'kids_population'
    adult = 'adult_population'
    senior = 'senior_population'

    feature_cols = [col for col in gdf_fe.columns if 'lag' in col]

    # Run XGBoost forecast for kids population
    print("Training model for kids population...")
    kids_model = run_xgboost_forecast(gdf_fe, kids, feature_cols, n_estimators=200, learning_rate=0.05, evaluate=False)
    # Run XGBoost forecast for adult population
    print("Training model for adult population...")
    adult_model = run_xgboost_forecast(gdf_fe, adult, feature_cols, n_estimators=200, learning_rate=0.05, evaluate=False)
    # Run XGBoost forecast for senior population
    print("Training model for senior population...")
    senior_model = run_xgboost_forecast(gdf_fe, senior, feature_cols, n_estimators=200, learning_rate=0.05, evaluate=False)

    # feature engineer the original dataset for prediction year
    gdf_predict = feature_engineering_prediction(gdf_with_all, lag_y=4, predict_years=2024)

    # Define feature columns for prediction
    feature_cols_predict = [col for col in gdf_predict.columns if 'lag' in col]

    # Make predictions for kids, adults, and seniors
    gdf_predict['kids_population_pred'] = kids_model.predict(gdf_predict[feature_cols_predict])
    gdf_predict['adult_population_pred'] = adult_model.predict(gdf_predict[feature_cols_predict])
    gdf_predict['senior_population_pred'] = senior_model.predict(gdf_predict[feature_cols_predict])

    #aggregate predictions per region
    gdf_predictions_aggregated = gdf_predict.groupby('kommunnamn')[['beftotalt','rutstorl','kids_population_pred', 'adult_population_pred', 'senior_population_pred']].sum().reset_index()
    
    #calculate percent increase
    gdf_predictions_aggregated = percent_increase(gdf_predictions_aggregated, gdf_with_all)

    #export predictions to geoparquet
    gdf_predictions_aggregated.to_parquet(directory + "population_predictions_2024_kommun.parquet")
    print("Population predictions for 2024 saved to " + directory + "population_predictions_2024_kommun.parquet")


if __name__ == "__main__":
    main()