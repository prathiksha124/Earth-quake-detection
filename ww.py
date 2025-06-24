# Example training code (save as train_model.py)
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import joblib
import pandas as pd

df = pd.read_csv('accdata_with_magnitude.csv')
X = df[['X', 'Y', 'Z']].values
y = df['Magnitude'].values

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)



model = RandomForestRegressor(n_estimators=300, max_depth=15)
model.fit(X_scaled, y)

# Save model and scaler
joblib.dump(model, 'earthquake_model.pkl')
joblib.dump(scaler, 'scaler.pkl')