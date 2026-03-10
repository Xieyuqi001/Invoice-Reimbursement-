import sqlite3

conn = sqlite3.connect('fapiao.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE records ADD COLUMN group_name VARCHAR(100) DEFAULT '丘陵课题组'")
    print("Added group_name column")
except Exception as e:
    print(f"group_name: {e}")

try:
    cursor.execute("ALTER TABLE records ADD COLUMN payment_type VARCHAR(20) DEFAULT '对公'")
    print("Added payment_type column")
except Exception as e:
    print(f"payment_type: {e}")

try:
    cursor.execute("ALTER TABLE records ADD COLUMN other_info TEXT")
    print("Added other_info column")
except Exception as e:
    print(f"other_info: {e}")

conn.commit()
conn.close()

print("Done!")
