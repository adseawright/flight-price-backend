from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sqlite3
from MachineLearning.predict import predict_price

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load the mappings for categories like airline names from a JSON file
with open('MachineLearning/models/category_mapping.json', 'r') as f:
    category_mapping = json.load(f)

# Helper function to connect to the SQLite database (used for retrieving flight data)
def connect_db():
    return sqlite3.connect('../database/dropdown_data.db') 

################################################################################
# API route - dropdown-data - to get airline data for dropdowns in the frontend
################################################################################
@app.route('/dropdown-data', methods=['GET'])
def get_dropdown_data():
    data = {
        'airlines': [{'label': airline, 'value': airline} for airline in sorted(category_mapping['airline'])],  # Sorted alphabetically
    }
    return jsonify(data)

#######################################################################################
# API route - departure-cities - fetches departure cities based on the selected airline
#######################################################################################
@app.route('/departure-cities', methods=['GET'])
def get_departure_cities():
    airline_name = request.args.get('airline')

    if airline_name:
        conn = connect_db()
        cursor = conn.cursor()

        # Get the ID for the selected airline
        cursor.execute('SELECT id FROM airlines WHERE name = ?', (airline_name,))
        airline_result = cursor.fetchone()
        if not airline_result:
            conn.close()
            return jsonify({'cities': []})   # No cities found for the airline

        airline_id = airline_result[0]

         # Fetch the available departure cities for this airline
        cursor.execute('''
            SELECT DISTINCT cities.name
            FROM flight_routes
            JOIN cities ON flight_routes.from_city = cities.id
            WHERE flight_routes.airline = ?
            ORDER BY cities.name ASC
        ''', (airline_id,))

        cities = [{'label': row[0], 'value': row[0]} for row in cursor.fetchall()]
        conn.close()

        return jsonify({'cities': cities})
    else:
        return jsonify({'error': 'Invalid airline'}), 400
###################################################################################################
# API route - destination-cities - fetches destination cities based on airline and departure city
###################################################################################################

@app.route('/destination-cities', methods=['GET'])
def get_destination_cities():
    airline_name = request.args.get('airline')
    from_city_name = request.args.get('from_city')

    if airline_name and from_city_name:
        conn = connect_db()
        cursor = conn.cursor()

        # Get airline ID
        cursor.execute('SELECT id FROM airlines WHERE name = ?', (airline_name,))
        airline_result = cursor.fetchone()
        if not airline_result:
            conn.close()
            return jsonify({'destinations': []})  # Airline not found

        airline_id = airline_result[0]

        # Get from_city ID
        cursor.execute('SELECT id FROM cities WHERE name = ?', (from_city_name,))
        from_city_result = cursor.fetchone()
        if not from_city_result:
            conn.close()
            return jsonify({'destinations': []})  # From city not found

        from_city_id = from_city_result[0]

        # Get destination cities
        cursor.execute('''
            SELECT DISTINCT cities.name
            FROM flight_routes
            JOIN cities ON flight_routes.to_city = cities.id
            WHERE flight_routes.airline = ? AND flight_routes.from_city = ?
            ORDER BY cities.name ASC
        ''', (airline_id, from_city_id))

        destinations = [{'label': row[0], 'value': row[0]} for row in cursor.fetchall()]
        conn.close()

        return jsonify({'destinations': destinations})
    else:
        return jsonify({'error': 'Invalid airline or departure city'}), 400

#######################################################################################################
# API Route - available-stops-count - for fetching available stops counts based on previous selections
#######################################################################################################

@app.route('/available-stops-count', methods=['GET'])
def get_available_stops_count():
    airline_name = request.args.get('airline')
    from_city_name = request.args.get('from_city')
    to_city_name = request.args.get('to_city')

    if airline_name and from_city_name and to_city_name:
        conn = connect_db()
        cursor = conn.cursor()

         # Get the IDs for airline and cities
        cursor.execute('SELECT id FROM airlines WHERE name = ?', (airline_name,))
        airline_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (from_city_name,))
        from_city_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (to_city_name,))
        to_city_result = cursor.fetchone()

        if not airline_result or not from_city_result or not to_city_result:
            conn.close()
            return jsonify({'stops_counts': []})  # Entities not found

        airline_id = airline_result[0]
        from_city_id = from_city_result[0]
        to_city_id = to_city_result[0]

        # Get available numbers of stops 
        cursor.execute('''
            SELECT DISTINCT stops
            FROM flight_routes
            WHERE airline = ? AND from_city = ? AND to_city = ?
            ORDER BY stops ASC
        ''', (airline_id, from_city_id, to_city_id))

        stops_counts = [{'label': str(row[0]), 'value': row[0]} for row in cursor.fetchall()]
        conn.close()

        return jsonify({'stops_counts': stops_counts})
    else:
        return jsonify({'error': 'Invalid selection'}), 400

###################################################################################################
# API route - available-durations - to get available flight durations based on selections
###################################################################################################
@app.route('/available-durations', methods=['GET'])
def get_available_durations():
    airline_name = request.args.get('airline')
    from_city_name = request.args.get('from_city')
    to_city_name = request.args.get('to_city')
    stops_count = request.args.get('stops')

    if airline_name and from_city_name and to_city_name and stops_count is not None:
        conn = connect_db()
        cursor = conn.cursor()

        # Get IDs for airline and cities
        cursor.execute('SELECT id FROM airlines WHERE name = ?', (airline_name,))
        airline_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (from_city_name,))
        from_city_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (to_city_name,))
        to_city_result = cursor.fetchone()

        if not airline_result or not from_city_result or not to_city_result:
            conn.close()
            return jsonify({'durations': []})  # Entities not found

        airline_id = airline_result[0]
        from_city_id = from_city_result[0]
        to_city_id = to_city_result[0]

        # Get available durations for the selected route
        cursor.execute('''
            SELECT DISTINCT duration
            FROM flight_routes
            WHERE airline = ? AND from_city = ? AND to_city = ? AND stops = ?
            ORDER BY duration ASC
        ''', (airline_id, from_city_id, to_city_id, stops_count))

        durations = [{'label': str(row[0]), 'value': row[0]} for row in cursor.fetchall()]
        conn.close()

        return jsonify({'durations': durations})
    else:
        return jsonify({'error': 'Invalid selection'}), 400

###########################################################################################
# API route - available-classes - to get available flight classes based on selections
###########################################################################################

@app.route('/available-classes', methods=['GET'])
def get_available_classes():
    airline_name = request.args.get('airline')
    from_city_name = request.args.get('from_city')
    to_city_name = request.args.get('to_city')
    stops_count = request.args.get('stops')
    duration = request.args.get('duration')

    if airline_name and from_city_name and to_city_name and stops_count and duration:
        conn = connect_db()
        cursor = conn.cursor()

        # Get IDs for airline, cities, and stops
        cursor.execute('SELECT id FROM airlines WHERE name = ?', (airline_name,))
        airline_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (from_city_name,))
        from_city_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (to_city_name,))
        to_city_result = cursor.fetchone()

        if not airline_result or not from_city_result or not to_city_result:
            conn.close()
            return jsonify({'class_categories': []})  # No classes found

        airline_id = airline_result[0]
        from_city_id = from_city_result[0]
        to_city_id = to_city_result[0]

        # Get flight classes
        cursor.execute('''
            SELECT DISTINCT class_category.name
            FROM flight_routes
            JOIN class_category ON flight_routes.class_category = class_category.id
            WHERE flight_routes.airline = ? AND flight_routes.from_city = ? AND flight_routes.to_city = ? AND flight_routes.stops = ? AND flight_routes.duration = ?
            ORDER BY class_category.name ASC
        ''', (airline_id, from_city_id, to_city_id, stops_count, duration))

        class_categories = [{'label': row[0], 'value': row[0]} for row in cursor.fetchall()]
        conn.close()

        return jsonify({'class_categories': class_categories})
    else:
        return jsonify({'error': 'Invalid selection'}), 400

#################################################################################################
# API route - available-dep-daytimes - to get available departure daytimes based on selections
#################################################################################################

@app.route('/available-dep-daytimes', methods=['GET'])
def get_available_dep_daytimes():
    airline_name = request.args.get('airline')
    from_city_name = request.args.get('from_city')
    to_city_name = request.args.get('to_city')
    stops_count = request.args.get('stops')
    duration = request.args.get('duration')
    class_category_name = request.args.get('class_category')

    if airline_name and from_city_name and to_city_name and stops_count and duration and class_category_name:
        conn = connect_db()
        cursor = conn.cursor()

        # Get IDs
        cursor.execute('SELECT id FROM airlines WHERE name = ?', (airline_name,))
        airline_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (from_city_name,))
        from_city_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (to_city_name,))
        to_city_result = cursor.fetchone()
        cursor.execute('SELECT id FROM class_category WHERE name = ?', (class_category_name,))
        class_category_result = cursor.fetchone()

        if not airline_result or not from_city_result or not to_city_result or not class_category_result:
            conn.close()
            return jsonify({'dep_daytime_categories': []})  # Categories not found

        airline_id = airline_result[0]
        from_city_id = from_city_result[0]
        to_city_id = to_city_result[0]
        class_category_id = class_category_result[0]

        # Convert stops_count and duration to integers
        stops_count = int(stops_count)
        duration = int(float(duration))

        # Get departure daytimes
        cursor.execute('''
            SELECT DISTINCT dep_daytime_category
            FROM flight_routes
            WHERE airline = ? AND from_city = ? AND to_city = ? AND stops = ? AND duration = ? AND class_category = ?
            ORDER BY dep_daytime_category ASC
        ''', (airline_id, from_city_id, to_city_id, stops_count, duration, class_category_id))

        results = cursor.fetchall()

        # Assuming dep_daytime_category is stored as integers 0 (Day) and 1 (Night)
        dep_daytimes = [{'label': 'Day' if row[0] == 0 else 'Night', 'value': row[0]} for row in results]
        conn.close()

        return jsonify({'dep_daytime_categories': dep_daytimes})
    else:
        return jsonify({'error': 'Invalid selection'}), 400

#########################################################################################
# API Route - available-arr-daytimes - for fetching available arrival daytimes
#########################################################################################

@app.route('/available-arr-daytimes', methods=['GET'])
def get_available_arr_daytimes():
    airline_name = request.args.get('airline')
    from_city_name = request.args.get('from_city')
    to_city_name = request.args.get('to_city')
    stops_count = request.args.get('stops')
    duration = request.args.get('duration')
    class_category_name = request.args.get('class_category')

    if airline_name and from_city_name and to_city_name and stops_count and duration and class_category_name:
        conn = connect_db()
        cursor = conn.cursor()

        # Get IDs
        cursor.execute('SELECT id FROM airlines WHERE name = ?', (airline_name,))
        airline_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (from_city_name,))
        from_city_result = cursor.fetchone()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (to_city_name,))
        to_city_result = cursor.fetchone()
        cursor.execute('SELECT id FROM class_category WHERE name = ?', (class_category_name,))
        class_category_result = cursor.fetchone()

        if not airline_result or not from_city_result or not to_city_result or not class_category_result:
            conn.close()
            return jsonify({'arr_daytime_categories': []})  # Entities not found

        airline_id = airline_result[0]
        from_city_id = from_city_result[0]
        to_city_id = to_city_result[0]
        class_category_id = class_category_result[0]

        # Convert stops_count and duration to integers
        stops_count = int(stops_count)
        duration = int(float(duration))

        # Get arrival daytimes
        cursor.execute('''
            SELECT DISTINCT arr_daytime_category
            FROM flight_routes
            WHERE airline = ? AND from_city = ? AND to_city = ? AND stops = ? AND duration = ? AND class_category = ?
            ORDER BY arr_daytime_category ASC
        ''', (airline_id, from_city_id, to_city_id, stops_count, duration, class_category_id))

        results = cursor.fetchall()

        # Assuming arr_daytime_category is stored as integers 0 (Day) and 1 (Night)
        arr_daytimes = [{'label': 'Day' if row[0] == 0 else 'Night', 'value': row[0]} for row in results]
        conn.close()

        return jsonify({'arr_daytime_categories': arr_daytimes})
    else:
        return jsonify({'error': 'Invalid selection'}), 400

###############################################################################
# API Route - predict - handles the flight price predictions
###############################################################################

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        print(f"Received data: {data}")  # Debugging log

        # Ensure all required fields are present
        required_fields = [
            'airline', 'from', 'to', 'class_category', 'stops_category',
            'arr_daytime_category', 'dep_daytime_category', 'duration_in_min',
            'stops', 'dep_date'
        ]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Extract day and month from dep_date
        dep_date = data['dep_date']
        dep_day = int(dep_date.split('-')[2])
        dep_month = int(dep_date.split('-')[1])
        data['day'] = dep_day
        data['month'] = dep_month

        # Construct the 'route' field by combining 'from' and 'to'
        data['route'] = f"{data['from']}-{data['to']}"

        # Call the predict function from predict.py
        predicted_price = predict_price(data)

        # Check if the prediction was successful
        if predicted_price is not None:
            return jsonify({'predicted_price': f"{predicted_price:.2f} INR"}), 200
        else:
            return jsonify({'error': 'Prediction failed'}), 500
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print("Starting the Flask server...")
    app.run(debug=True)
