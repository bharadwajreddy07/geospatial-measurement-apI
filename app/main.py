from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.database import create_tables
from app.routers import auth, tasks

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="Aereo Task API",
    version="1.0.0",
    description="A production-oriented task management API with JWT authentication.",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}