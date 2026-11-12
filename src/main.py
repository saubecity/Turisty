from fastapi import FastAPI

from database import connection

app = FastAPI(title="Turisty", version="1.0")

with connection.get_db() as conn:
    print("test")

@app.get("/hi")
async def root():
    return {"test":"yay it works"}
