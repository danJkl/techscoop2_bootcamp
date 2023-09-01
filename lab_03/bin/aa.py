import os
import glob
import pandas as pd
import mariadb
import datetime
import time

# Start the timer
start_time = time.time()


# Path
directory_path = r'D:\Workspace\Python_Basic\lab_03\input'
pattern = os.path.join(directory_path, 'DESCRIBE_LOG_EVENTS_????????_??????.txt')
files = glob.glob(pattern)
valid_files = []
file_records_count = {}
valid_files_count = 0


# Check case sensitive
case_sensitive_files = [file for file in files if os.path.basename(file).startswith('DESCRIBE_LOG_EVENTS_')]

# Create an empty DataFrame to store the combined data
combined_data = pd.DataFrame()

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

# Read the file as a DataFrame
    df = pd.read_csv(file, delimiter='|', header=0, dtype=str)
    df['ZIPCODE'] = pd.to_numeric(df['ZIPCODE'], errors='coerce')
    df.dropna(subset=df.columns.difference(['ZIPCODE']), inplace=True)
    df.dropna(inplace=True,axis=0)
#count
    filename = os.path.basename(file)
    valid_files.append(filename)
    file_records_count[filename] = len(df)
    valid_files_count += 1

    # Exclude the header and tail of the file
    # df = df.iloc[0:-1]

    # Add 'stg_source' column with the file name
    df['stg_source'] = os.path.basename(file)

    # print(df)

    # Append the data to the combined DataFrame
    combined_data = combined_data._append(df, ignore_index=True)

# Save the combined data as a CSV file
combined_data.to_csv('combined_data.csv', index=False, header=True)

# MariaDB Connection
conn = mariadb.connect(
    user="root",
    password="example",
    host="127.0.0.1",
    port=3306,
    autocommit=True,
    local_infile=1,
    database="stg"
)
mycursor = conn.cursor()
#### Create DB
# mycursor.execute("DROP TABLE LOG_EVENTS")
# mycursor.execute("CREATE TABLE LOG_EVENTS (DATE_TIME DATETIME, NAME VARCHAR(250), CITY VARCHAR(30), ZIPCODE VARCHAR(10), LOCALE VARCHAR(6), BBAN VARCHAR(20), BANK_COUNTRY VARCHAR(2), IBAN VARCHAR(22), COUNTRY_CALLING_CODE VARCHAR(10), MSISDN VARCHAR(15), PHONE_NUMBER VARCHAR(22), STATUS VARCHAR(10), GENDER VARCHAR(1), STG_SOURCE VARCHAR(50));")
mycursor.execute("TRUNCATE TABLE LOG_EVENTS;")

#### Create Table
# mycursor.execute("CREATE TABLE stg.SPECIAL_NUMBER AS SELECT Phone_number, MIN(STG_Source) AS STG_Source FROM LOG_EVENTS WHERE Phone_number REGEXP '^\\([0-9]{3}\\)[0-9]{3}-[0-9]{4}$' GROUP BY Phone_number ORDER BY STG_Source ASC;")
#### INSERT 5min
# mycursor.execute("INSERT INTO stg.SPECIAL_NUMBER (Phone_number, STG_Source) SELECT temp.Phone_number, temp.STG_Source FROM (SELECT Phone_number, MIN(STG_Source) AS STG_Source FROM LOG_EVENTS GROUP BY Phone_number AS temp LEFT JOIN stg.SPECIAL_NUMBER ON temp.Phone_number = stg.SPECIAL_NUMBER.Phone_number WHERE temp.Phone_number REGEXP '^\\([0-9]{3}\\)[0-9]{3}-[0-9]{4}$' AND stg.SPECIAL_NUMBER.Phone_number IS NULL;")

# Ingest CSV data into MariaDB table
query = "LOAD DATA LOCAL INFILE 'combined_data.csv' INTO TABLE LOG_EVENTS FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\r\\n' IGNORE 1 LINES"
mycursor.execute(query)


print("Input files:")
for file in valid_files:
    print(os.path.basename(file))

print("Log:")
for file in valid_files:
    print(os.path.basename(file), ":","Processed ", file_records_count[file], "records")


print("Files processed:", valid_files_count)

print("Insert special number: ",mycursor.rowcount)
# Close the database connection
mycursor.close()
conn.close()
end_time = time.time()
elapsed_time = end_time - start_time
print("Execution time:", elapsed_time, "seconds")