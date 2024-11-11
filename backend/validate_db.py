import sqlite3

def validate_database(db_path):
    # Connect to the SQLite database with a timeout to avoid locking issues
    conn = sqlite3.connect(db_path, timeout=10)  # You can increase the timeout if needed
    cursor = conn.cursor()

    # Check if the Szalloda table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Szalloda';")
    table = cursor.fetchone()
    if table:
        print("Szalloda table exists.")
        
        # Fetch and print column names for Szalloda table
        cursor.execute("PRAGMA table_info(Szalloda);")
        columns = cursor.fetchall()
        print("Columns in Szalloda table:")
        for column in columns:
            print(f"- {column[1]} (type: {column[2]})")
    else:
        print("Szalloda table does not exist in the database.")

    # Close the connection
    conn.close()
