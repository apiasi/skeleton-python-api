from fastapi import FastAPI
from app.api.v1.endpoints import auth

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "API rodando"}
