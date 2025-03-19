"""ASR service module for voice transcription"""
import os
import time
import logging
from fastapi import Depends
from funasr import AutoModel

from app.core.dependencies import get_asr_model
from app.core.config import settings
from app.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


async def transcribe_voice_to_text(voice_file, asr_model: AutoModel = Depends(get_asr_model)) -> str:
    """
    Transcribe a voice file to text using ASR.
    
    Args:
        voice_file: The voice file to transcribe
        asr_model: The ASR model to use
        
    Returns:
        str: The transcribed text
    """
    start_time = time.time()
    temp_file = f"temp{time.time()}"
    
    logger.info(f"Starting voice transcription, saving to temp file: {temp_file}")
    
    with open(temp_file, "wb") as f:
        f.write(voice_file)
    
    try:
        logger.debug(f"Running ASR model with hotwords file: {settings.HOTWORDS_FILE}")
        res = asr_model.generate(
            input=temp_file,
            use_itn=True,
            batch_size_s=300,
            merge_vad=True,
            merge_length_s=15,
            hotwords=settings.HOTWORDS_FILE
        )

        txt = res[0]["text"]
        
        elapsed_time = time.time() - start_time
        logger.info(f"Voice transcription completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Transcription result: {txt[:100]}...")
        
        return txt
    except Exception as e:
        logger.error(f"Error during voice transcription: {str(e)}", exc_info=True)
        raise
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)
            logger.debug(f"Removed temporary file: {temp_file}") 