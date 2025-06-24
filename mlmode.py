import pyrebase
from flask import Flask
import numpy as np
import joblib
from datetime import datetime
import time

app = Flask(__name__)

# Load trained model and scaler
model = joblib.load('earthquake_model.pkl')
scaler = joblib.load('scaler.pkl')

# Firebase configuration
config = {
    "apiKey": "AIzaSyCFrFpvlizFPX4VJ5HD35aqNQ_C6XFT5sY",
    "authDomain": "earthquake-detection-6646b.firebaseapp.com",
    "databaseURL": "https://earthquake-detection-6646b-default-rtdb.asia-southeast1.firebasedatabase.app",
    "storageBucket": "earthquake-detection-6646b.firebasestorage.app",
    "serviceAccount": "path/to/serviceAccountKey.json"  # Make sure this file is in your project directory
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

def predict_magnitude(x, y, z):
    """Predict earthquake magnitude using the trained model"""
    input_data = np.array([[x, y, z]])
    scaled_data = scaler.transform(input_data)
    return float(model.predict(scaled_data)[0])

def stream_handler(message):
    """Handle incoming sensor data from Firebase"""
    if message["event"] == "put":
        data = message["data"]
        if data:
            try:
                x = float(data.get("x", 0))
                y = float(data.get("y", 0))
                z = float(data.get("z", 0))
                
                # Get prediction
                magnitude = predict_magnitude(x, y, z)
                
                # Prepare prediction data
                prediction_data = {
                    "x": x,
                    "y": y,
                    "z": z,
                    "magnitude": magnitude,
                    "timestamp": int(time.time())
                }
                
                # Send to Firebase
                db.child("predictions").push(prediction_data)
                print(f"Prediction sent: {magnitude:.2f} magnitude")
                
            except Exception as e:
                print(f"Error processing data: {str(e)}")

def test_firebase_connection():
    """Test Firebase connection and write permissions"""
    try:
        test_data = {
            "x": 1.23,
            "y": 4.56,
            "z": 7.89,
            "timestamp": int(time.time())
        }
        
        db.child("connection_test").push(test_data)
        print("Firebase connection test successful!")
        return True
    except Exception as e:
        print(f"Firebase connection failed: {str(e)}")
        return False

if __name__ == '__main__':
    # Test Firebase connection first
    if test_firebase_connection():
        # Start listening to sensor data
        print("Starting to listen for sensor data...")
        db.child("sensor_readings").stream(stream_handler)
        
        # Run Flask app (optional, for API endpoints)
        app.run(host='0.0.0.0', port=5000, threaded=True)
    else:
        print("Failed to establish Firebase connection. Exiting.")