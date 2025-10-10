from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database
from app.routes import userRoutes, authRoutes, adminRoutes, petOwnerRoutes, appointmentRoutes, vetRoutes

models.Base.metadata.create_all(bind=database.engine)

# Initialize FastAPI app
app = FastAPI(title="VetLink API", docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # add others if needed, e.g. deployed URLs
]
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(userRoutes.router)
app.include_router(authRoutes.router)
app.include_router(adminRoutes.router)
app.include_router(petOwnerRoutes.router)
app.include_router(appointmentRoutes.router)
app.include_router(vetRoutes.router)


# Root endpoint
@app.get("/")
def home():
    return {"message": "Welcome to VetLink API"}