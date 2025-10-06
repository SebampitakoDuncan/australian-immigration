from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import status
import logging
import os
import traceback

from api.routes import router
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Australian Immigration Law RAG System",
    description="A RAG system for querying Australian immigration law documents using gpt-oss-20b",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Use configurable file size limit from settings

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add file size limit middleware
@app.middleware("http")
async def file_size_limit_middleware(request: Request, call_next):
    """Middleware to limit file upload size."""
    if request.method == "POST" and "/api/ingest" in request.url.path:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > settings.MAX_FILE_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "File too large",
                            "message": f"File size exceeds the maximum limit of {settings.MAX_FILE_SIZE_MB}MB. Received: {size / (1024*1024):.1f}MB",
                            "max_size": f"{settings.MAX_FILE_SIZE_MB}MB"
                        }
                    )
            except ValueError:
                # Invalid content-length header
                pass

    response = await call_next(request)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for better error reporting."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again.",
            "detail": str(exc) if settings.DEBUG else None
        }
    )

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors gracefully."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "message": "The request data is invalid.",
            "details": exc.errors()
        }
    )

# Include API routes
app.include_router(router, prefix="/api", tags=["RAG API"])

@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Australian Immigration Law RAG System",
        "version": "1.0.0",
        "description": "A RAG system for querying Australian immigration law documents",
        "docs": "/docs",
        "api": "/api"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting Australian Immigration Law RAG System")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")
    logger.info(f"ChromaDB directory: {settings.CHROMA_PERSIST_DIRECTORY}")
    logger.info(f"Documents directory: {settings.DOCUMENTS_DIR}")
    
    # Create necessary directories
    os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
    os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
    os.makedirs(settings.DATA_DIR, exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Australian Immigration Law RAG System")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
