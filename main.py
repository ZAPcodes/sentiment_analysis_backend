from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router  # Import API routes

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Run: uvicorn main:app --reload
