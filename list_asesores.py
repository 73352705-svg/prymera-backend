"""List all asesores from the database"""
import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, dbname='bd_core_mobile', user='postgres', password='postgres')
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

# Find asesor-like tables
for t in tables:
    if 'asesor' in t.lower():
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{t}'")
        cols = [r[0] for r in cur.fetchall()]
        print(f"\nTable '{t}' columns: {cols}")
        cur.execute(f"SELECT * FROM {t} LIMIT 5")
        for r in cur.fetchall():
            print(f"  {r}")

cur.close()
conn.close()
