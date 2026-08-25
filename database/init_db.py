from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
db_url = os.getenv("DATABASE_URL")

with open('database/schema.sql') as f:
    sql = f.read()

conn = psycopg2.connect(db_url)
try:
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
    print("Tabelas criadas com sucesso!")
finally:
    conn.close()