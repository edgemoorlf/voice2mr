from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/server-info")
async def get_server_info():
    """
    Get server configuration information.
    
    Returns:
        dict: Server information including:
            - light_mode (bool): True if server is running in lightweight mode
    """
    # Check if LIGHT_MODE environment variable is set to "true"
    light_mode = os.getenv("LIGHT_MODE", "false").lower() == "true"
    
    return {
        "light_mode": light_mode
    }
