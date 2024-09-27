import os
import sqlite3
import pandas as pd
import json

def init_db():
    # Get the base directory of 'backend'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Define paths
    db_path = os.path.join(base_dir, 'database', 'dropdown_data.db')
    encoded_data_path = os.path.join(base_dir, 'api', 'MachineLearning', 'models', 'encoded_training_data.csv')
    category_mapping_path = os.path.join(base_dir, 'api', 'MachineLearning', 'models', 'category_mapping.json')

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS flight_routes')
    cursor.execute('DROP TABLE IF EXISTS airlines')
    cursor.execute('DROP TABLE IF EXISTS cities')
    cursor.execute('DROP TABLE IF EXISTS stops_category')
    cursor.execute('DROP TABLE IF EXISTS class_category')

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS airlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stops_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS class_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flight_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            airline INTEGER NOT NULL,
            from_city INTEGER NOT NULL,
            to_city INTEGER NOT NULL,
            stops_category INTEGER NOT NULL,
            class_category INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            dep_daytime_category INTEGER,
            arr_daytime_category INTEGER,
            month INTEGER,
            stops INTEGER NOT NULL,
            FOREIGN KEY (airline) REFERENCES airlines(id),
            FOREIGN KEY (from_city) REFERENCES cities(id),
            FOREIGN KEY (to_city) REFERENCES cities(id),
            FOREIGN KEY (class_category) REFERENCES class_category(id),
            FOREIGN KEY (stops_category) REFERENCES stops_category(id)
        )
    ''')

    # Load the category mapping file as a dictionary
    if os.path.exists(category_mapping_path):
        with open(category_mapping_path, 'r') as f:
            category_mapping = json.load(f)
    else:
        print(f"Category mapping file not found at path: {category_mapping_path}")
        return

    # Populate the airlines table with actual names
    airlines = category_mapping['airline']
    cursor.executemany('INSERT OR IGNORE INTO airlines (name) VALUES (?)', [(name,) for name in airlines])

    # Populate the cities table with actual names
    cities = list(set(category_mapping['from'] + category_mapping['to']))
    cursor.executemany('INSERT OR IGNORE INTO cities (name) VALUES (?)', [(name,) for name in cities])

    # Populate the stops_category table
    stops = category_mapping['stops_category']
    cursor.executemany('INSERT OR IGNORE INTO stops_category (name) VALUES (?)', [(name,) for name in stops])

    # Populate the class_category table
    class_category = category_mapping['class_category']
    cursor.executemany('INSERT OR IGNORE INTO class_category (name) VALUES (?)', [(name,) for name in class_category])

    conn.commit()
    print("Dropdown tables populated successfully!")

    # Load the encoded CSV file
    if os.path.exists(encoded_data_path):
        encoded_data = pd.read_csv(encoded_data_path)
        print(f"Encoded data loaded successfully from {encoded_data_path}")

        # Insert the flight routes into the database using the IDs
        for index, row in encoded_data.iterrows():
            try:
                # Decode values back to original category names using category_mapping
                airline_name = category_mapping['airline'][int(row['airline'])]
                from_city_name = category_mapping['from'][int(row['from'])]
                to_city_name = category_mapping['to'][int(row['to'])]
                stops_category_name = category_mapping['stops_category'][int(row['stops_category'])]
                class_category_name = category_mapping['class_category'][int(row['class_category'])]

                # Get IDs for airline, from_city, to_city, stops_category, class_category
                cursor.execute('SELECT id FROM airlines WHERE name = ?', (airline_name,))
                airline_result = cursor.fetchone()
                if airline_result:
                    airline_id = airline_result[0]
                else:
                    print(f"Airline '{airline_name}' not found in 'airlines' table.")
                    continue  

                cursor.execute('SELECT id FROM cities WHERE name = ?', (from_city_name,))
                from_city_result = cursor.fetchone()
                if from_city_result:
                    from_city_id = from_city_result[0]
                else:
                    print(f"From city '{from_city_name}' not found in 'cities' table.")
                    continue  

                cursor.execute('SELECT id FROM cities WHERE name = ?', (to_city_name,))
                to_city_result = cursor.fetchone()
                if to_city_result:
                    to_city_id = to_city_result[0]
                else:
                    print(f"To city '{to_city_name}' not found in 'cities' table.")
                    continue 

                cursor.execute('SELECT id FROM stops_category WHERE name = ?', (stops_category_name,))
                stops_category_result = cursor.fetchone()
                if stops_category_result:
                    stops_category_id = stops_category_result[0]
                else:
                    print(f"Stops category '{stops_category_name}' not found in 'stops_category' table.")
                    continue  

                cursor.execute('SELECT id FROM class_category WHERE name = ?', (class_category_name,))
                class_category_result = cursor.fetchone()
                if class_category_result:
                    class_category_id = class_category_result[0]
                else:
                    print(f"Class category '{class_category_name}' not found in 'class_category' table.")
                    continue  

                # Insert into flight_routes
                cursor.execute('''
                    INSERT INTO flight_routes (
                        airline, from_city, to_city, stops_category, class_category,
                        duration, dep_daytime_category, arr_daytime_category, month, stops
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    airline_id,
                    from_city_id,
                    to_city_id,
                    stops_category_id,
                    class_category_id,
                    int(row['duration_in_min']),
                    int(row['dep_daytime_category']),
                    int(row['arr_daytime_category']),
                    int(row['month']),
                    int(row['stops'])
                ))
            except Exception as e:
                print(f"Error inserting row {index}: {e}")

        conn.commit()
        print("Flight routes inserted successfully!")
    else:
        print(f"Encoded CSV file not found at path: {encoded_data_path}")

    conn.close()
    print("Database initialized and data inserted successfully!")

if __name__ == "__main__":
    init_db()
