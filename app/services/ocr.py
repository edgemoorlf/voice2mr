"""OCR service module"""
import time
from fastapi import Depends
from paddleocr import PaddleOCR

from app.core.dependencies import get_ocr_model
from app.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


async def transcribe_image_to_text(image_file, ocr_model: PaddleOCR = Depends(get_ocr_model)) -> str:
    """
    Transcribe an image file to text using OCR.
    
    Args:
        image_file: The image file to transcribe
        ocr_model: The OCR model to use
        
    Returns:
        str: The transcribed text
    """
    start_time = time.time()
    logger.info("Starting OCR image transcription")
    
    try:
        result = ocr_model.ocr(image_file, cls=True)
        transcripts = []
        
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                transcripts.append(line[1][0])
        
        text = '\n'.join(transcripts)
        
        elapsed_time = time.time() - start_time
        logger.info(f"OCR transcription completed in {elapsed_time:.2f} seconds")
        logger.debug(f"OCR detected {len(transcripts)} lines of text")
        
        if not text:
            logger.warning("OCR transcription returned empty result")
        else:
            logger.debug(f"OCR result sample: {text[:100]}...")
        
        return text
    except Exception as e:
        logger.error(f"Error during OCR transcription: {str(e)}", exc_info=True)
        raise 