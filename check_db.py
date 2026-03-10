import sqlite3

conn = sqlite3.connect('fapiao.db')
cursor = conn.cursor()

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='records'")
result = cursor.fetchone()
print("Table structure:")
print(result[0] if result else "No table found")

conn.close()
