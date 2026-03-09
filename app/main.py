from fastapi import FastAPI
from app.core.database import engine, Base
from app.api import auth, users
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SANKALP User Type System")

# Required for Authlib sessions
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Routes
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome to SANKALP Backend. Visit /docs for API documentation."}
