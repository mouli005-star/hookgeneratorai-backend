from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints
import time

app = FastAPI(title="HookMaster AI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "HookMaster AI"}

app.include_router(endpoints.router, prefix="/api/v1")
