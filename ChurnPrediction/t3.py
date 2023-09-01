import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load and preprocess data
train_data = pd.read_csv('train.csv')
test_data = pd.read_csv('test.csv', usecols=lambda column: column != 'index')

label_encoder = LabelEncoder()
train_data['international_plan'] = label_encoder.fit_transform(train_data['international_plan'])
train_data['voice_mail_plan'] = label_encoder.fit_transform(train_data['voice_mail_plan'])

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

# Hyperparameter tuning using RandomizedSearchCV
param_dist = {
    'n_estimators': np.arange(100, 401, 100),
    'max_depth': [None, 10, 20],
    'min_samples_split': np.arange(2, 11, 2),
    'min_samples_leaf': np.arange(1, 5),
    'max_features': ['sqrt', 'log2']  # Fixed max_features parameter
}

random_search = RandomizedSearchCV(RandomForestClassifier(random_state=42), param_distributions=param_dist, n_iter=20,
                                   cv=3, scoring='accuracy', n_jobs=-1)
random_search.fit(X_train, y_train)
best_model = random_search.best_estimator_

# Evaluate the best model on validation data
y_pred = best_model.predict(X_val)
accuracy = accuracy_score(y_val, y_pred)
print("Validation Accuracy:", accuracy)
print("Best Parameters:", random_search.best_params_)

# ... (previous code)

# Preprocess test data
test_data['international_plan'] = label_encoder.transform(test_data['international_plan'])
test_data['voice_mail_plan'] = label_encoder.transform(test_data['voice_mail_plan'])

# One-hot encode 'state' feature for test data
test_state_encoded = state_encoder.transform(test_data[['state']])
test_state_encoded_df = pd.DataFrame(test_state_encoded, columns=state_encoder.get_feature_names_out(['state']))
test_data = pd.concat([test_data, test_state_encoded_df], axis=1)

# Drop unnecessary columns from test data
X_test = test_data.drop(columns_to_drop, axis=1)  # Drop the same columns as in training
X_test_scaled = scaler.transform(X_test)

# Make predictions using the best model
test_predictions = best_model.predict(X_test_scaled)

# Create submission file
submission = pd.DataFrame({'index': test_data.index, 'churn': test_predictions})
submission.to_csv('submission.csv', index=False)
