from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from typing import List
from app.api.models.request_models import MRRequestModel
from app.api.models.response_models import MRResponseModel
from app.services.medical_record import medical_record_service

router = APIRouter()

@router.post("/t2mr", response_model=MRResponseModel)
async def t2mr_endpoint(request_model: MRRequestModel) -> MRResponseModel:
    """
    Transcript to a Medical Record.

    This endpoint provides you the capability of converting a transcript in text into a medical record.
    
    - **transcript**: The transcript in text.
    - **medical_records**: Additional medical data to be applied, regarding the medical record of the patient.
    - **is_json**: Whether the result in the json or text with markdown formats.
    - **language**: The language for the response (default: zh).

    Returns the medical records in json or text in markdown.
    """
    response = await medical_record_service.generate_medical_record(
        transcript=request_model.transcript,
        medical_records=request_model.medical_records,
        language=request_model.language,
        is_json=request_model.is_json
    )
    return MRResponseModel(**response)

@router.post("/a2mr", response_model=MRResponseModel)
async def a2mr_endpoint(
    files: List[UploadFile] = File(...),
    medical_records: str = Form(""),
    is_json: bool = Form(False),
    language: str = Form("zh")
) -> MRResponseModel:
    """
    Voice or image files to a Medical Record.

    This endpoint provides you the capability of converting voice records with one or multiple files in audio, video or image formats into a medical record.
    
    - **files**: The multimedia files. For audio/video files, the format must be in content_type "audio/mpeg", "audio/wav", "audio/mp3", "audio/m4a", "video/quicktime" or "video/mp4".
                 For images, common image formats are supported.
    - **medical_records**: Additional medical data to be applied, regarding the medical record of the patient.
    - **is_json**: Whether the result in the json or text with markdown formats.
    - **language**: The language for the response (default: zh).

    Returns the medical records in json or text in markdown.
    """
    voice_files = []
    voice_content_types = []
    image_files = []
    
    for file in files:
        content = await file.read()
        if file.content_type.startswith('audio/') or file.content_type.startswith('video/'):
            voice_files.append(content)
            voice_content_types.append(file.content_type)
        elif file.content_type.startswith('image/'):
            image_files.append(content)

    transcripts = []
    if voice_files:
        try:
            voice_transcript = await medical_record_service.process_voice_files(voice_files, voice_content_types, language)
            transcripts.append(voice_transcript)
        except RuntimeError as e:
            raise HTTPException(
                status_code=501,
                detail=str(e)
            )
    
    if image_files:
        try:
            image_transcript = await medical_record_service.process_image_files(image_files)
            if medical_records:
                transcripts.append(medical_records)
            transcripts.append(image_transcript)
        except RuntimeError as e:
            raise HTTPException(
                status_code=501,
                detail=str(e)
            )
    elif medical_records:
        transcripts.append(medical_records)

    if not transcripts:
        transcripts = [medical_records] if medical_records else []

    response = await medical_record_service.generate_medical_record(
        transcript="\n".join(transcripts),
        language=language,
        is_json=is_json
    )
    
    return MRResponseModel(**response)
