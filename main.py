from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database
from app.routes import userRoutes, authRoutes

models.Base.metadata.create_all(bind=database.engine)

# Initialize FastAPI app
app = FastAPI(title="VetLink API", docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(userRoutes.router)
app.include_router(authRoutes.router)


# Root endpoint
@app.get("/")
def home():
    return {"message": "Welcome to VetLink API"}