from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cluster Management API",
    description="Technical Assessment API for managing organizations, clusters, and deployments.",
    version="1.0.0",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    session_cookie=os.getenv("SESSION_COOKIE_NAME"),
    max_age=int(os.getenv("SESSION_MAX_AGE")),
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
