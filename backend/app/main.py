from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth   
import app.models  # this import triggers model registration with Base

app = FastAPI(
    title="Online Store API",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

# CORS = Cross-Origin Resource Sharing.
# Browsers block requests from one domain to another by default — this is a
# security feature. But our React app (localhost:5173) needs to talk to our
# FastAPI server (localhost:8000), which are technically different "origins".
# This middleware tells the browser: "yes, requests from these origins are allowed."
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React's default dev port
    allow_credentials=True,  # allows cookies and auth headers
    allow_methods=["*"],     # allow GET, POST, PATCH, DELETE, etc.
    allow_headers=["*"],     # allow any headers (including Authorization)
)

# Register routers — each one adds a group of related endpoints
app.include_router(auth.router)


# A simple health-check endpoint.
# Visiting http://localhost:8000/ should return this immediately.
@app.get("/")
def root():
    return {"message": "Store API is running"}