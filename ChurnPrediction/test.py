import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load the training and test datasets
train_data = pd.read_csv('train.csv')
test_data = pd.read_csv('test.csv')

# Separate features and target variable in the training dataset
X_train = train_data.drop(columns=['churn'])
y_train = train_data['churn']

# Separate features in the test dataset
X_test = test_data.drop(columns=['id']) 

# Perform data preprocessing
# For simplicity, we'll ignore 'state' and 'area_code' features in this example
# You can extend preprocessing as needed based on your analysis

# Drop 'state' and 'area_code' features
X_train = X_train.drop(columns=['state', 'area_code'])
X_test = X_test.drop(columns=['state', 'area_code'])

# Convert categorical features to binary (yes=1, no=0)
X_train['international_plan'] = (X_train['international_plan'] == 'yes').astype(int)
X_train['voice_mail_plan'] = (X_train['voice_mail_plan'] == 'yes').astype(int)

X_test['international_plan'] = (X_test['international_plan'] == 'yes').astype(int)
X_test['voice_mail_plan'] = (X_test['voice_mail_plan'] == 'yes').astype(int)

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train a logistic regression model
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test_scaled)

# Prepare the submission file
submission = pd.DataFrame({'id': test_data.index + 1, 'churn': y_pred})
submission.to_csv('submission2.csv', index=False)

