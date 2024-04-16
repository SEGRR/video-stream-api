from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from router.user import router as user_router
from router.auth import router as auth_router
from router.movies import router as movies_router

origins = ["http://localhost:8000"  , "http://localhost:5500"]

app = FastAPI()
app.include_router(user_router , prefix="/user")
app.include_router(auth_router , prefix="/auth")
app.include_router(movies_router , prefix="/movies")
app.add_middleware(CORSMiddleware , allow_origins=origins)

