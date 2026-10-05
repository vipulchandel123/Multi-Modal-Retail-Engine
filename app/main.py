from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Modal AI Backend")

# Browser (HTML/JS) connectivity ke liye CORS enable karna zaroori hai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Multi-Modal AI Engine Operational"}