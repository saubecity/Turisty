from database.connection import get_db

with get_db() as conn:
    cur = conn.execute("""
        SELECT COUNT(*)
        FROM Attraction
        WHERE Latitude IS NOT NULL
          AND Longitude IS NOT NULL
    """)

    print("Attractions avec coordonnées :", cur.fetchone()[0])