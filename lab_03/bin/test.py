import glob
import os
import pandas as pd
import datetime
import time

# Start the timer
start_time = time.time()

# Initialize a counter for active records
active_records_count = 0
male_active_records_count = 0
female_active_records_count = 0
# Initialize a list to store valid phone numbers
valid_phone_numbers = []
# Initialize a list to store the valid file names
valid_files = []
# Initialize a variable to store the count of valid files
valid_files_count = 0
# Initialize a dictionary to store the count of records in each file
file_records_count = {}
# Min - Max zipcode 
min_zipcode = float('inf')
max_zipcode = float('-inf')

# Path
directory_path = r'D:\Workspace\Python_Basic\lab_03\input'
pattern = os.path.join(directory_path, 'DESCRIBE_LOG_EVENTS_????????_??????.txt')
files = glob.glob(pattern)

# Check case sensitive
case_sensitive_files = [file for file in files if os.path.basename(file).startswith('DESCRIBE_LOG_EVENTS_')]

for file in case_sensitive_files:
    # Skip folders and files with spaces in their names
    if not os.path.isfile(file) or ' ' in os.path.basename(file):
        continue

    # Extract the time part from the file name
    time_part = os.path.basename(file).split('_')[-1].split('.')[0]
    date_part = os.path.basename(file).split('_')[-2].split('.')[0]
    
    # Validate the date values
    try:
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])

        datetime.datetime(year, month, day)  # Check if it's a valid date
    except ValueError:
        continue

    # Validate the time values
    try:
        hour = int(time_part[:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])

        if hour > 23 or minute > 59 or second > 59:
            continue
    except ValueError:
        continue
    # Add the valid file name to the list
    filename = os.path.basename(file)
    valid_files.append(filename)


    # Read the file into a DataFrame
    df = pd.read_csv(file, delimiter='|')
    df.dropna(inplace=True,axis=0)

    # Count the number of records in the file
    file_records_count[filename] = len(df)

    # Filter the DataFrame based on the 'STATUS' column
    active_records = df[df['STATUS'] == 'active']

    # Increment the counter by the number of active records in the current file
    active_records_count += len(active_records)
    male_active_records_count += len(df[(df['STATUS'] == 'active') & (df['GENDER'] == 'm')])
    female_active_records_count += len(df[(df['STATUS'] == 'active') & (df['GENDER'] == 'f')])
    # Convert 'ZIPCODE' column to numeric data type
    df['ZIPCODE'] = pd.to_numeric(df['ZIPCODE'], errors='coerce')

    # Drop rows with NaN values in 'ZIPCODE' and remove the entire row
    df.dropna(subset=df.columns.difference(['ZIPCODE']), inplace=True)
    # Min Max zipcode
    min_zipcode = df['ZIPCODE'].min()
    max_zipcode = df['ZIPCODE'].max()


    # Increment the count of valid files
    valid_files_count += 1
 
# Retrieve phone numbers and format them as (xxx)xxx-xxxx
    phone_numbers = df['PHONE_NUMBER'].astype(str) 
    valid_phone_numbers += phone_numbers[phone_numbers.str.match(r'\(\d{3}\)\d{3}-\d{4}') & (phone_numbers.str.len() == 13)].tolist()



# Write the formatted phone numbers to a new file
output_file = os.path.join(directory_path, 'special_phonenumber.txt')
with open(output_file, 'w') as file:
    for phone_number in valid_phone_numbers:
        file.write(phone_number + '\n')




# Print the names of valid files
print("Valid files:")
for file in valid_files:
    print(os.path.basename(file))

print("Log:")
for file in valid_files:
    print("Log message: "+os.path.basename(file), ":", file_records_count[file], "records")
print("Files processed:", valid_files_count)
print("Total number of active records:", active_records_count)
print("Total number of male active records:", male_active_records_count)
print("Total number of female active records:", female_active_records_count)
print("Minimum Zip Code: %05d " % min_zipcode)
print("Maximum Zip Code: %05d " % max_zipcode)
# End the timer
end_time = time.time()
elapsed_time = end_time - start_time
print("Execution time:", elapsed_time, "seconds")
