import sqlite3

# create database
conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# create users table
cursor.execute("""
CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password BLOB NOT NULL
)
""")

conn.commit()
conn.close()

print("Database created successfully!")