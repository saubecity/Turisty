from fastapi import FastAPI

app = FastAPI(title="Turisty", version="1.0")

@app.get("/hi")
async def root():
    return {"test":"yay it works"}
