"""CDSS API routes"""
from fastapi import APIRouter, Depends
from openai import OpenAI

from app.models.schemas import CDSSRequestModel, CDSSResponseModel
from app.services.llm import process_cdss_query, medical_record_to_natural_language
from app.core.dependencies import get_llm_client


router = APIRouter(tags=["CDSS"])


@router.post("/query", response_model=CDSSResponseModel)
async def process_text(request_model: CDSSRequestModel):
    """
    Process a query to the CDSS system.
    
    This endpoint processes queries to the Clinical Decision Support System.
    
    Returns the response from the CDSS system.
    """
    return await process_cdss_query(
        prompt=request_model.prompt,
        role=request_model.role,
        session_id=request_model.session_id,
        medical_records=request_model.medical_records,
        history=request_model.history
    )


@router.post("/mr2nl", response_model=CDSSResponseModel)
async def mr_to_natural_language(request_model: CDSSRequestModel):
    """
    Convert medical records to natural language.
    
    This endpoint converts structured medical records to a more readable natural language format.
    
    Returns the converted medical record.
    """
    return await medical_record_to_natural_language(
        role=request_model.role,
        medical_records=request_model.medical_records
    ) 