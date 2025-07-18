"""
Voice2MR API application package
"""

import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import medical_records, chat, server_info

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
app.include_router(server_info.router, tags=["Server Info"])

if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description='Medical AI Assistant API.')
    parser.add_argument('--port', 
                        type=int, 
                        help='The listening port', 
                        default=8000)
    args = parser.parse_args()

    uvicorn.run("app:app", 
                host="0.0.0.0", 
                port=args.port,
                reload=True)
