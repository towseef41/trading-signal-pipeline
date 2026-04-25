from fastapi import FastAPI
from api.v1.routes import router

app = FastAPI(title="Signal Ingestion API")

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}