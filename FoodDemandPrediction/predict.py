import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import OneHotEncoder

# Load the data
train_data = pd.read_csv('train.csv')
fulfillment_center_data = pd.read_csv('fulfilment_center_info.csv')
meal_info_data = pd.read_csv('meal_info.csv')

# Merge data
merged_data = pd.merge(train_data, fulfillment_center_data, on='center_id')
merged_data = pd.merge(merged_data, meal_info_data, on='meal_id')

# Feature engineering
merged_data['week'] = pd.to_datetime(merged_data['week'])
merged_data['day_of_week'] = merged_data['week'].dt.dayofweek
merged_data['month'] = merged_data['week'].dt.month

# Encode categorical variables
encoder = OneHotEncoder()
encoded_features = encoder.fit_transform(merged_data[['center_type', 'category', 'cuisine']]).toarray()
encoded_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(['center_type', 'category', 'cuisine']))

# Combine encoded features with original data
merged_data = pd.concat([merged_data, encoded_df], axis=1)          

# Define features and target variable
features = ['center_id', 'meal_id', 'checkout_price', 'base_price', 'emailer_for_promotion',
            'homepage_featured', 'op_area', 'day_of_week', 'month'] + list(encoded_df.columns)
target = 'num_orders'

# Split data into training and validation sets
train_X, val_X, train_y, val_y = train_test_split(merged_data[features], merged_data[target], test_size=0.2, random_state=42)

# Train a Random Forest regressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(train_X, train_y)

# Make predictions on validation set
predictions = model.predict(val_X)

# Evaluate the model
mae = mean_absolute_error(val_y, predictions)
print('Mean Absolute Error:', mae)

# Forecasting for next 10 weeks

# Create a DataFrame for forecasting_features
forecasting_data = pd.read_csv('forecasting_data.csv')  # Replace with the appropriate file name
forecasting_data['week'] = pd.to_datetime(forecasting_data['week'])
forecasting_data['day_of_week'] = forecasting_data['week'].dt.dayofweek
forecasting_data['month'] = forecasting_data['week'].dt.month
forecasting_encoded = encoder.transform(forecasting_data[['center_type', 'category', 'cuisine']]).toarray()
forecasting_encoded_df = pd.DataFrame(forecasting_encoded, columns=encoder.get_feature_names_out(['center_type', 'category', 'cuisine']))
forecasting_features = pd.concat([forecasting_data, forecasting_encoded_df], axis=1)


# Make predictions for the next 10 weeks
forecasted_orders = model.predict(forecasting_features)

# Print forecasted orders for the next 10 weeks
print('Forecasted Orders for Next 10 Weeks:', forecasted_orders)
