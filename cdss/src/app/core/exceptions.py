from fastapi import HTTPException
from typing import Any, Dict, Optional

class MedAIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
        error_key: str = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_key = error_key

class TranscriptionError(MedAIException):
    def __init__(self, source: str, detail: str = None):
        super().__init__(
            status_code=500,
            detail=f"Transcription failed from {source}: {detail}" if detail else f"Transcription failed from {source}",
            error_key="transcription_error"
        )

class UnsupportedMediaType(MedAIException):
    def __init__(self, media_type: str):
        super().__init__(
            status_code=415,
            detail=f"Unsupported media type: {media_type}",
            error_key="unsupported_media_type"
        )

class LLMServiceError(MedAIException):
    def __init__(self, service: str, detail: str = None):
        super().__init__(
            status_code=503,
            detail=f"LLM Service ({service}) Error: {detail}" if detail else f"LLM Service ({service}) Error",
            error_key="llm_service_error"
        )

class UnsupportedLanguage(MedAIException):
    def __init__(self, language: str):
        super().__init__(
            status_code=400,
            detail=f"Unsupported language: {language}",
            error_key="unsupported_language"
        )
