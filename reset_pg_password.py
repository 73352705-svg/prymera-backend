"""Reset PostgreSQL password for user 'postgres' to 'postgres'"""
import psycopg2

try:
    conn = psycopg2.connect(host='localhost', port=5432, dbname='postgres', user='postgres')
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("ALTER USER postgres WITH PASSWORD 'postgres'")
    print("Password reset to: postgres")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
