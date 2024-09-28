import joblib
import pandas as pd
import os

# Loads the complete pipeline (model)
pipeline = joblib.load(os.path.join(os.path.dirname(__file__), 'models', 'modelo_final.pkl'))


def predict_price(data):
    try:
        # Extracts the necessary fields from the input data
        airline = data['airline']
        from_location = data['from']
        to_location = data['to']
        route = data['route']
        class_category = data['class_category']
        stops_category = data['stops_category']
        arr_daytime_category = data['arr_daytime_category']
        dep_daytime_category = data['dep_daytime_category']
        duration = float(data['duration_in_min'])
        stops = int(data['stops'])
        dep_day = int(data['day'])
        dep_month = int(data['month'])

        # Creates a DataFrame with the same columns used during training
        input_df = pd.DataFrame({
            'airline': [airline],
            'from': [from_location],
            'to': [to_location],
            'route': [route],
            'class_category': [class_category],
            'stops_category': [stops_category],
            'arr_daytime_category': [arr_daytime_category],
            'dep_daytime_category': [dep_daytime_category],
            'duration_in_min': [duration],
            'stops': [stops],
            'day': [dep_day],
            'month': [dep_month]
        })

        # Performs prediction using the complete pipeline
        predicted_price = pipeline.predict(input_df)

        return predicted_price[0]

    except Exception as e:
        print(f"Error during prediction: {e}")
        return None
