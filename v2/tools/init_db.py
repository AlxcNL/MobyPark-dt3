import sqlite3
import os
import sys

DB_PATH = "./data/mobypark.db"
db_exists = os.path.exists(DB_PATH)

if not db_exists:
    print(f"Database not found at {DB_PATH}. Creating new database...")

    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Read and execute the init.sql script
    with open("./tools/init.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(sql)
    conn.commit()
    conn.close()

    print("Database schema initialized.")

    # Run the import migrations for the new database
    print("\nRunning data imports...")
    sys.path.insert(0, "./tools/import_jsons")

    try:
        import main as import_main
        import_main.main()
        print("\nDatabase fully initialized with data migrations.")
    except Exception as e:
        print(f"Warning: Failed to run data imports: {e}")
        print("Database schema created, but data imports failed.")
else:
    print(f"Database already exists at {DB_PATH}. Skipping initialization.")