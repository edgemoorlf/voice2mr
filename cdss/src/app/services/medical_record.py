import time
from typing import Dict, List, Optional
from app.services.llm import llm_service
from app.services.asr import asr_service
from app.services.ocr import ocr_service
from app.core.config import SUPPORTED_AUDIO_TYPES
from app.core.exceptions import UnsupportedMediaType, TranscriptionError
from app.core.i18n import get_language_prompt

class MedicalRecordService:
    async def process_voice_files(self, files: List[bytes], content_types: List[str], language: str) -> str:
        """Process voice files and return combined transcript"""
        transcripts = []
        
        for file_content, content_type in zip(files, content_types):
            if content_type not in SUPPORTED_AUDIO_TYPES:
                raise UnsupportedMediaType(content_type)
                
            transcript = await asr_service.transcribe_voice(file_content)
            if not transcript:
                raise TranscriptionError("ASR", "Empty transcript")
            transcripts.append(transcript)
        
        return "\n".join(transcripts)

    async def process_image_files(self, files: List[bytes]) -> str:
        """Process image files and return combined transcript"""
        transcripts = []
        
        for file_content in files:
            transcript = await ocr_service.transcribe_image(file_content)
            if not transcript:
                raise TranscriptionError("OCR", "Empty transcript")
            transcripts.append(transcript)
        
        return "\n".join(transcripts)

    async def generate_medical_record(
        self,
        transcript: str,
        medical_records: Optional[str] = None,
        language: str = "zh",
        is_json: bool = True
    ) -> Dict:
        """Generate medical record from transcript and additional records"""
        # Get language-specific prompts
        context_str = get_language_prompt(language, 'doctor_context')
        format_prompt = get_language_prompt(language, 'mr_format')
        format_detail = get_language_prompt(language, 'mr_format_detail')
        
        # Construct the prompt
        prompt = f"{format_prompt}\n{format_detail}\n\n{transcript}"
        if medical_records:
            prompt += f"\n\nAdditional medical records:\n{medical_records}"

        # Create messages list
        messages = [{"role": "user", "content": prompt}]

        result = await llm_service.generate_completion(
            messages=messages,
            system_context=context_str,
            is_json=is_json
        )
        
        return {
            "content": result["content"],
            "timestamp": int(time.time()),
            "prompt_tokens": result["usage"].prompt_tokens,
            "completion_tokens": result["usage"].completion_tokens,
            "total_tokens": result["usage"].total_tokens
        }

    async def process_chat(
        self,
        prompt: str,
        role: str,
        medical_records: Optional[str] = None,
        session_id: Optional[str] = None,
        history: Optional[List[str]] = None,
        language: str = "zh"
    ) -> Dict:
        """Process chat messages and return response"""
        # Get language-specific context
        context_str = get_language_prompt(language, f'{role}_context')
        
        # Build messages list
        messages = []
        if history:
            messages.append({"role": "assistant", "content": '\n'.join(history)})
        
        # Add medical records context if provided
        if medical_records:
            query_context = get_language_prompt(language, f'{role}_query_context')
            context_with_records = query_context.format(medical_records=medical_records)
            messages.append({"role": "system", "content": context_with_records})
            
        messages.append({"role": "user", "content": prompt})

        result = await llm_service.generate_completion(
            messages=messages,
            system_context=context_str
        )
        
        return {
            "session_id": session_id,
            "content": result["content"],
            "timestamp": int(time.time()),
            "prompt_tokens": result["usage"].prompt_tokens,
            "completion_tokens": result["usage"].completion_tokens,
            "total_tokens": result["usage"].total_tokens
        }

# Create a singleton instance
medical_record_service = MedicalRecordService()
