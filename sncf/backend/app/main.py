from fastapi import FastAPI
from api.recommendations import router as recommendations_router

app = FastAPI(
    title="SNCF Hackathon API",
    description="Backend API for SNCF Hackathon project with recommendation system",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])

@app.get("/")
async def root():
    return {"message": "Welcome to SNCF Hackathon API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
