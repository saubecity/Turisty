from database.connection import get_db

with get_db() as conn:
    rows = conn.execute("""
        SELECT NameAttraction, Latitude, Longitude
        FROM Attraction
        WHERE Latitude IS NOT NULL
          AND Longitude IS NOT NULL
        LIMIT 5
    """).fetchall()

    for row in rows:
        print(dict(row))