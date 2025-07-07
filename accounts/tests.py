import psycopg2

conn = psycopg2.connect(
    dbname="travelshare_db",
    user="transport",
    password="PeruPara",
    host="localhost",
    port="5432"
)

print("Connection successful")
