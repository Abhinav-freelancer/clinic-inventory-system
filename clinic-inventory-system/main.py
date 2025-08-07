from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from app.api.v1.router import router as api_router

# Create FastAPI app
app = FastAPI(
    title="Clinic Inventory System",
    description="A comprehensive inventory management system for clinics",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Clinic Inventory System API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
