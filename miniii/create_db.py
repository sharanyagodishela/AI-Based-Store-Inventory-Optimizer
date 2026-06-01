import sqlite3

# Connect to SAME database used in app.py
conn = sqlite3.connect("store.db")

cursor = conn.cursor()

# -----------------------
# CREATE USER TABLE
# -----------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# -----------------------
# CREATE PRODUCT TABLE
# -----------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stock INTEGER NOT NULL,
    price REAL NOT NULL,
    sales INTEGER DEFAULT 0
)
""")

print("Database and tables created successfully!")

conn.commit()
conn.close()