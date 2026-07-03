"""Update asesores credentials to numeric codes and new passwords"""
import psycopg2
from app.core.security import hash_password

conn = psycopg2.connect(host='localhost', port=5432, dbname='bd_core_mobile', user='postgres', password='postgres')
conn.autocommit = True
cur = conn.cursor()

pw = hash_password("Prymera2024")

updates = [
    ("EMP001", "0001"),
    ("EMP002", "0002"),
    ("EMP003", "0003"),
    ("ADMIN", "9999"),
]

for old_code, new_code in updates:
    cur.execute(
        "UPDATE asesores SET codigo_empleado = %s, password_hash = %s WHERE codigo_empleado = %s",
        (new_code, pw, old_code)
    )
    print(f"Updated {old_code} -> {new_code} | password: Prymera2024")

cur.close()
conn.close()

# Also update the seed.py for future fresh installs
with open(r"D:\backend\seed.py", "r", encoding="utf-8") as f:
    seed = f.read()

seed = seed.replace('"EMP001"', '"0001"')
seed = seed.replace('"EMP002"', '"0002"')
seed = seed.replace('"EMP003"', '"0003"')
seed = seed.replace('"ADMIN"', '"9999"')
seed = seed.replace('password: 123456', 'password: Prymera2024')
seed = seed.replace('password: "123456"', 'password: "Prymera2024"')

with open(r"D:\backend\seed.py", "w", encoding="utf-8") as f:
    f.write(seed)

print("\nseed.py updated too")
