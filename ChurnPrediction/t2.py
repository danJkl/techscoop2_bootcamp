import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

# Load and preprocess data
train_data = pd.read_csv('train.csv')
test_data = pd.read_csv('test.csv', usecols=lambda column: column != 'index')  # Ignore the 'index' column

label_encoder = LabelEncoder()
train_data['international_plan'] = label_encoder.fit_transform(train_data['international_plan'])
train_data['voice_mail_plan'] = label_encoder.fit_transform(train_data['voice_mail_plan'])

# Perform one-hot encoding for the 'state' column
state_encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
state_encoded = state_encoder.fit_transform(train_data[['state']])
state_encoded_df = pd.DataFrame(state_encoded, columns=state_encoder.get_feature_names_out(['state']))
train_data = pd.concat([train_data, state_encoded_df], axis=1)

# Drop unnecessary columns
columns_to_drop = ['churn', 'state', 'area_code']
X = train_data.drop(columns_to_drop, axis=1)
y = train_data['churn']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_val, y_train, y_val = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_val)
accuracy = accuracy_score(y_val, y_pred)
print("Validation Accuracy:", accuracy)

# Preprocess test data
test_data['international_plan'] = label_encoder.transform(test_data['international_plan'])
test_data['voice_mail_plan'] = label_encoder.transform(test_data['voice_mail_plan'])

# Perform one-hot encoding for the 'state' column in test data
test_state_encoded = state_encoder.transform(test_data[['state']])
test_state_encoded_df = pd.DataFrame(test_state_encoded, columns=state_encoder.get_feature_names_out(['state']))
test_data = pd.concat([test_data, test_state_encoded_df], axis=1)

# Drop unnecessary columns from test data
columns_to_drop = ['state', 'area_code']
X_test = test_data.drop(columns_to_drop, axis=1)

# Make sure the column order matches the training data
X_test = X_test.reindex(columns=X.columns, fill_value=0)

X_test_scaled = scaler.transform(X_test)

# Make predictions
test_predictions = model.predict(X_test_scaled)

# Create submission file
submission = pd.DataFrame({'id': test_data.index + 1, 'churn': test_predictions})  # Add 1 to test_data.index
submission.to_csv('submission.csv', index=False)
