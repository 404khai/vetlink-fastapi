from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database
from routes import userRoutes

models.Base.metadata.create_all(bind=database.engine)

# Initialize FastAPI app
app = FastAPI(title="User Management API", docs_url="/docs")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(userRoutes.router)


# Root endpoint
@app.get("/")
def home():
    return {"message": "Welcome to VetLink API"}