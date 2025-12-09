import sqlite3

files = [
    "crm_dataset.sql",
    "erp_dataset.sql",
    "multivendor_ecom_dataset.sql",
    "social_media_analytics_dataset.sql",
]

print("Loading SQL files into analytics.db...")

conn = sqlite3.connect("analytics.db")
cursor = conn.cursor()

for file in files:
    print(f"Importing {file} ...")
    with open(file, "r", encoding="utf-8") as f:
        sql_script = f.read()
        cursor.executescript(sql_script)  # MUCH FASTER
    print(f"{file} imported.")

conn.commit()
conn.close()

print("\nAll SQL files imported successfully!")
