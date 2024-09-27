import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import pytest
import calendar

# Function to dynamically load the trained model from the file system
def carregar_modelo():
    # Dynamically building the path to the saved model
    base_dir = os.path.join('..', 'api', 'MachineLearning', 'models')
    model_path = os.path.join(base_dir, 'modelo_final.pkl')
    
    # Load and return the model
    modelo = joblib.load(model_path)
    return modelo

# Test 1: Ensure the model is making predictions correctly
def test_predicoes():
    # Load the model
    modelo = carregar_modelo()

    # Sample data for prediction
    teste = pd.DataFrame([{
        'airline': 'Indigo', 'from': 'Delhi', 'to': 'Mumbai', 'route': 'DEL-MUM', 
        'class_category': 'Economy', 'stops_category': 'Non-stop', 
        'arr_daytime_category': 'Daytime Arrival', 'dep_daytime_category': 'Daytime Departure',
        'duration_in_min': 180, 'stops': 0, 'day': 15, 'month': 12
    }])

    # Get predictions from the model
    predicted_prices = modelo.predict(teste)
    
    # Check if the predictions are valid and match the input data size
    assert predicted_prices is not None  # Make sure there's a prediction
    assert len(predicted_prices) == len(teste)  # Ensure the number of predictions matches the input rows

# Test 2: Check if the RMSE (Root Mean Squared Error) of the model is within an acceptable range
def test_rmse_aceitavel():
    # Load the model
    modelo = carregar_modelo()

    # Dynamically create test data for a month
    trip_year = 2025  # Year for the test
    trip_month = 2
    num_days_in_month = calendar.monthrange(trip_year, trip_month)[1]  # Get the number of days in month

    # Build the test dataset for each day in the month
    X_test = pd.DataFrame([
        {
            'airline': 'Indigo', 'from': 'Delhi', 'to': 'Mumbai', 'route': 'DEL-MUM',
            'class_category': 'Economy', 'stops_category': 'Non-stop',
            'arr_daytime_category': 'Daytime Arrival', 'dep_daytime_category': 'Daytime Departure',
            'duration_in_min': 180, 'stops': 0, 'day': day, 'month': trip_month
        } for day in range(1, num_days_in_month + 1)
    ])
    
    # Define the expected target values (replace with actual expected prices)
    y_test = np.full(num_days_in_month, 8000)  # Set the expected price for every day in the month

    # Get predictions from the model
    y_pred = modelo.predict(X_test)

    # Calculate RMSE (how far off the predictions are from the expected values)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Assert that the RMSE is within the acceptable range
    assert rmse < 4000  # Setting the acceptable error threshold 
