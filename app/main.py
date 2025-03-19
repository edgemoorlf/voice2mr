"""Main application module"""
import argparse
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import cdss, medical_records
from app.core.config import settings
from app.core.logging import setup_logging


# Set up logging
logger = setup_logging()


def create_application(domain: str = None, collection: str = None) -> FastAPI:
    """
    Create the FastAPI application with all routes.
    
    Args:
        domain: The expertise domain of RAG
        collection: The collection of RAG
        
    Returns:
        FastAPI: The configured FastAPI application
    """
    # Update domain and collection if provided
    if domain:
        settings.DOMAIN = domain
        logger.info(f"Domain set to {domain}")
    if collection:
        settings.COLLECTION = collection
        logger.info(f"Collection set to {collection}")

    # Create application
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Voice to Medical Records API",
        version="1.0.0",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )
    logger.info(f"Initializing {settings.PROJECT_NAME}")

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug("CORS middleware configured")

    # Include routers
    app.include_router(cdss.router, prefix="/api")
    app.include_router(medical_records.router, prefix="/api")
    logger.debug("Routers configured")

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"{settings.PROJECT_NAME} startup complete")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"{settings.PROJECT_NAME} shutdown")

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description='Voice to Medical Records API')
    parser.add_argument('--port', 
                        type=int, 
                        help='The listening port', 
                        default=8000)
    parser.add_argument('--debug',
                        action='store_true',
                        help='Enable debug mode')
    args = parser.parse_args()

    # Enable debug mode if specified
    if args.debug:
        settings.DEBUG = True
        log_level = "debug"
    else:
        log_level = settings.LOG_LEVEL.lower()

    app = create_application(domain=args.domain, collection=args.collection)

    logger.info(f"Starting server at http://0.0.0.0:{args.port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.port,
        log_level=log_level
    ) 