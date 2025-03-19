"""Medical Records API routes"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List

from app.models.schemas import MRRequestModel, MRResponseModel, ScaleResponseModel
from app.services.llm import transcript_to_medical_record, extract_keywords_per_transcript, qa_per_transcript
from app.services.asr import transcribe_voice_to_text
from app.services.ocr import transcribe_image_to_text
from app.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

router = APIRouter(tags=["Medical Records"])


@router.post("/t2mr", response_model=MRResponseModel)
async def t2mr_endpoint(request_model: MRRequestModel) -> MRResponseModel:
    """
    Transcript to a Medical Record.

    This endpoint provides you the capability of converting a transcript in text into a medical record.
    
    The request includes transcript, medical_records and is_json.

    - **transcript**: The transcript in text.
    - **medical_records**: Additional medical data to be applied, regarding the medical record of the patient.
    - **is_json**: Whether the result in the json or text with markdown formats.

    Returns the medical records in json or text in markdown.
    """
    logger.info(f"Received request to convert transcript to medical record (JSON: {request_model.is_json})")
    
    transcript = request_model.transcript
    medical_records = request_model.medical_records or ""
    is_json = request_model.is_json
    
    response = await transcript_to_medical_record(transcript, medical_records, is_json)
    logger.info(f"Completed transcript to medical record conversion, tokens used: {response.total_tokens}")
    
    return response


@router.post("/v2mr", response_model=MRResponseModel)
async def v2mr_endpoint(
    files: List[UploadFile] = File(...),
    medical_records: str = Form(""),
    is_json: bool = Form(False)
) -> MRResponseModel:
    """
    Voice files to a Medical Record.

    This endpoint provides you the capability of converting voice records with one or multiple files in audio or video formats into a medical record.
    
    - **files**: The voices files. The format must be in content_type "audio/mpeg", "audio/wav", "audio/mp3", "audio/m4a", "video/quicktime" or "video/mp4".
    - **medical_records**: Additional medical data to be applied, regarding the medical record of the patient.
    - **is_json**: Whether the result in the json or text with markdown formats.

    Returns the medical records in json or text in markdown.
    """
    logger.info(f"Received request to convert voice files to medical record (Files: {len(files)}, JSON: {is_json})")
    
    transcripts = []
    for i, file in enumerate(files):
        logger.info(f"Processing file {i+1}/{len(files)}: {file.filename} with content type: {file.content_type}")
        
        if file.content_type not in ["audio/mpeg", "audio/wav", "audio/mp3", "audio/m4a", "video/quicktime", "video/mp4"]:
            logger.error(f"Unsupported media type: {file.content_type}")
            raise HTTPException(status_code=415, detail="Unsupported media type")
            
        voice_file = await file.read()
        logger.debug(f"File {file.filename} read, size: {len(voice_file)} bytes")
        
        transcript = await transcribe_voice_to_text(voice_file)
        
        if transcript == '':
            logger.error("Empty transcript returned from voice transcription")
            raise HTTPException(status_code=500, detail="Internal Server Error: Empty Transcript")
            
        transcripts.append(transcript)
        logger.info(f"Voice transcription successful for file {i+1}/{len(files)}")
    
    combined_transcript = "\n".join(transcripts)
    logger.debug(f"Combined transcript length: {len(combined_transcript)} characters")
    
    response = await transcript_to_medical_record(combined_transcript, medical_records, is_json)
    logger.info(f"Completed voice to medical record conversion, tokens used: {response.total_tokens}")
    
    return response


@router.post("/i2mr", response_model=MRResponseModel)
async def i2mr_endpoint(
    files: List[UploadFile] = File(...),
    medical_records: str = Form(""),
    is_json: bool = Form(False)
) -> MRResponseModel:
    """
    Image files to a Medical Record.

    This endpoint provides you the capability of converting pictures of checkups etc., with one or multiple files in image formats into a medical record.
    
    - **files**: The image files. 
    - **medical_records**: Additional medical data to be applied, regarding the medical record of the patient.
    - **is_json**: Whether the result in the json or text with markdown formats.

    Returns the medical records in json or text in markdown.
    """
    logger.info(f"Received request to convert image files to medical record (Files: {len(files)}, JSON: {is_json})")
    
    transcripts = []
    for i, file in enumerate(files):
        logger.info(f"Processing file {i+1}/{len(files)}: {file.filename}")
        
        image_file = await file.read()
        logger.debug(f"File {file.filename} read, size: {len(image_file)} bytes")
        
        transcript = await transcribe_image_to_text(image_file)
        transcripts.append(transcript)
        
        logger.info(f"OCR transcription successful for file {i+1}/{len(files)}")
    
    combined_transcript = "\n".join(transcripts)
    logger.debug(f"Combined transcript length: {len(combined_transcript)} characters")
    
    response = await transcript_to_medical_record(combined_transcript, medical_records, is_json)
    logger.info(f"Completed image to medical record conversion, tokens used: {response.total_tokens}")
    
    return response


@router.post("/iqa", response_model=ScaleResponseModel)
async def iqa_endpoint(
    files: List[UploadFile] = File(...),
    prompts: List[str] = Form(""),
    keywords: List[str] = Form("")
) -> ScaleResponseModel:
    """
    Question answering based on image files.
    
    This endpoint extracts text from images and answers questions based on the extracted text.
    
    - **files**: The image files.
    - **prompts**: List of questions to answer.
    - **keywords**: List of keywords to extract.
    
    Returns answers to the questions and extracted key-value pairs.
    """
    logger.info(f"Received image QA request (Files: {len(files)}, Prompts: {len(prompts)}, Keywords: {len(keywords)})")
    
    transcripts = []    
    for i, file in enumerate(files):
        logger.info(f"Processing file {i+1}/{len(files)}: {file.filename}")
        
        image_file = await file.read()
        logger.debug(f"File {file.filename} read, size: {len(image_file)} bytes")
        
        transcript = await transcribe_image_to_text(image_file)
        transcripts.append(transcript)
        
        logger.info(f"OCR transcription successful for file {i+1}/{len(files)}")
    
    transcript = "\n".join(transcripts)
    logger.debug(f"Combined transcript length: {len(transcript)} characters")
    
    prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
    answers = []
    
    # Process each prompt
    for i, prompt in enumerate(prompts):
        logger.info(f"Processing prompt {i+1}/{len(prompts)}: {prompt[:50]}...")
        
        res = await qa_per_transcript(transcript, prompt)
        answers.append(res.choices[0].message.content)
        
        usage = res.usage
        prompt_tokens += usage.prompt_tokens
        completion_tokens += usage.completion_tokens
        total_tokens += usage.total_tokens
        
        logger.info(f"Processed prompt {i+1}/{len(prompts)}, tokens used: {usage.total_tokens}")

    # Process keywords
    if keywords:
        logger.info(f"Extracting keywords: {keywords}")
        res = await extract_keywords_per_transcript(transcript, keywords)
        content = res.choices[0].message.content
        
        usage = res.usage
        prompt_tokens += usage.prompt_tokens
        completion_tokens += usage.completion_tokens
        total_tokens += usage.total_tokens
        
        logger.info(f"Keywords extraction completed, tokens used: {usage.total_tokens}")
    else:
        content = "{}"
        logger.info("No keywords provided for extraction")

    response = ScaleResponseModel(
        answers=answers, 
        key_values=content, 
        prompt_tokens=prompt_tokens, 
        completion_tokens=completion_tokens, 
        total_tokens=total_tokens
    )
    
    logger.info(f"Completed image QA request, total tokens used: {total_tokens}")
    return response 