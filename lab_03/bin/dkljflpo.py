import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="example",
  database="stg"
)
mycursor = mydb.cursor()

mycursor.execute("DROP TABLE LOG_EVENTS")
mycursor.execute("CREATE TABLE LOG_EVENTS (DATE_TIME DATETIME, NAME VARCHAR(250), CITY VARCHAR(30), ZIPCODE VARCHAR(10), LOCALE VARCHAR(6), BANK_COUNTRY VARCHAR(2), IBAN VARCHAR(22), COUNTRY_CALLING_CODE VARCHAR(10), MSISDN VARCHAR(15), PHONE_NUMBER VARCHAR(22), STATUS VARCHAR(10), GENDER VARCHAR(1), STG_SOURCE VARCHAR(50));")
mycursor.execute("SHOW DATABASES")

print(mydb)