from fastapi import APIRouter
from app.core.config import LIGHT_MODE, HAS_ASR, HAS_OCR, APP_VERSION
from app.api.models.response_models import ServerInfoModel

router = APIRouter()

@router.get("/server-info", response_model=ServerInfoModel)
async def get_server_info():
    return {
        "light_mode": LIGHT_MODE,
        "features": {
            "asr": HAS_ASR,
            "ocr": HAS_OCR
        },
        "version": APP_VERSION
    }
