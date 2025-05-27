"""
Voice2MR API application package
"""

import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import medical_records, chat
from app.core.config import DOMAIN, COLLECTION

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporary for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(medical_records.router, tags=["Medical Records"])
app.include_router(chat.router, tags=["Chat"])

# Only initialize heavy services in the actual server process
@app.on_event("startup")
def initialize_services():
    from app.services.asr import asr_service
    from app.services.ocr import ocr_service
    # This will trigger their __init__ only once in the child process
    _ = asr_service
    _ = ocr_service

if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description='Medical AI Assistant API.')
    parser.add_argument('--domain', 
                        type=str, 
                        help='The expertise domain of RAG', 
                        default='oncology')
    parser.add_argument('--collection', 
                        type=str, 
                        help='The collection of RAG', 
                        default='med_refv3')
    parser.add_argument('--port', 
                        type=int, 
                        help='The listening port', 
                        default=8000)
    args = parser.parse_args()

    uvicorn.run("app:app", 
                host="0.0.0.0", 
                port=args.port,
                reload=True)
