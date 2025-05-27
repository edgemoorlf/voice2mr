from fastapi import APIRouter
from app.api.models.request_models import CDSSRequestModel
from app.api.models.response_models import CDSSResponseModel
from app.services.medical_record import medical_record_service

router = APIRouter()

@router.post("/query", response_model=CDSSResponseModel)
async def process_text(request_model: CDSSRequestModel) -> CDSSResponseModel:
    """
    Process a chat query.

    This endpoint handles chat interactions with the medical AI assistant.
    
    - **prompt**: The user's query text.
    - **role**: The role of the user (doctor/patient).
    - **session_id**: Optional session ID for conversation continuity.
    - **medical_records**: Optional medical records for context.
    - **history**: Optional conversation history.
    - **language**: The language for the response (default: zh).

    Returns the AI assistant's response.
    """
    response = await medical_record_service.process_chat(
        prompt=request_model.prompt,
        role=request_model.role,
        medical_records=request_model.medical_records,
        session_id=request_model.session_id,
        history=request_model.history,
        language=request_model.language
    )
    return CDSSResponseModel(**response)

@router.post("/mr2nl", response_model=CDSSResponseModel)
async def mr2nl(request_model: CDSSRequestModel) -> CDSSResponseModel:
    """
    Convert medical records to natural language.

    This endpoint converts formal medical records into natural language that is easier to understand.
    
    - **medical_records**: The medical records to convert.
    - **role**: The role of the user (doctor/patient).
    - **language**: The language for the response (default: zh).

    Returns the natural language version of the medical records.
    """
    response = await medical_record_service.process_chat(
        prompt=f"Please rephrase the following medical records into natural language: {request_model.medical_records}",
        role=request_model.role,
        language=request_model.language
    )
    return CDSSResponseModel(**response)
