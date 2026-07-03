"""Update cliente app user password"""
import psycopg2
from app.core.security import hash_password

conn = psycopg2.connect(host='localhost', port=5432, dbname='bd_core_mobile', user='postgres', password='postgres')
conn.autocommit = True
cur = conn.cursor()

pw = hash_password("Prymera2024")
cur.execute("UPDATE usuarios_cliente SET password_hash = %s WHERE username = '11111111'", (pw,))
print("Updated cliente app user (11111111) password to Prymera2024")
cur.close()
conn.close()
