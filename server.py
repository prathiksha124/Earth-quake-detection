import firebase_admin
from firebase_admin import credentials, db
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import time

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")  # Download from Firebase Console
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://earthquake-detection-6646b-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Load or train model
try:
    model = joblib.load('earthquake_model.pkl')
    print("Loaded pre-trained model")
except:
    print("Training new model...")
    # Load your dataset here (replace with your actual dataset)
    # Dataset should have columns: x, y, z, magnitude (target)
    data = pd.read_csv('accdata_with_magnitude.csv')
    X = data[['X', 'Y', 'Z']]
    y = data['Magnitude']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    print(f"Model RMSE: {np.sqrt(mean_squared_error(y_test, preds))}")
    joblib.dump(model, 'earthquake_model.pkl')

def fetch_recent_data():
    """Fetch recent sensor data from Firebase"""
    ref = db.reference('sensor_data')
    data = ref.order_by_key().limit_to_last(10).get()
    return pd.DataFrame.from_dict(data, orient='index')

def predict_magnitude(data):
    """Predict magnitude from sensor data"""
    features = data[['x', 'y', 'z']].values
    return model.predict(features).mean()  # Return average prediction

def monitor_firebase():
    """Monitor Firebase for earthquake triggers"""
    ref = db.reference('ml_trigger')
    
    def callback(event):
        if event.data == True:
            print("Earthquake detected! Processing...")
            # Fetch recent data
            sensor_data = fetch_recent_data()
            # Predict magnitude
            predicted_mag = predict_magnitude(sensor_data)
            print(f"Predicted magnitude: {predicted_mag:.2f}")
            
            # Store prediction
            db.reference('predictions').push({
                'timestamp': int(time.time() * 1000),
                'predicted_magnitude': float(predicted_mag),
                'sensor_data': sensor_data.to_dict(orient='records')
            })
            
            # Reset trigger
            ref.set(False)
    
    ref.listen(callback)

if __name__ == "__main__":
    print("Starting earthquake prediction service...")
    monitor_firebase()