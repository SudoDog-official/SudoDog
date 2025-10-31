import os
import psycopg2

# Get connection string from Vercel env vars
# You'll need to copy this from Vercel Settings → Env Variables
DATABASE_URL = "YOUR_POSTGRES_URL_HERE"

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Query recent events
cursor.execute("""
    SELECT 
        anonymous_id,
        event_type,
        timestamp,
        properties
    FROM telemetry_events
    ORDER BY created_at DESC
    LIMIT 10;
""")

print("\n📊 Recent Telemetry Events:\n")
for row in cursor.fetchall():
    print(f"ID: {row[0][:16]}... | Type: {row[1]} | Time: {row[2]}")
    if row[3]:
        print(f"   Properties: {row[3]}")
    print()

cursor.close()
conn.close()
