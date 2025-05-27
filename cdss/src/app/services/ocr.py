from paddleocr import PaddleOCR
from app.core.exceptions import TranscriptionError

class OCRService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            self._initialize_model()

    def _initialize_model(self):
        try:
            self._model = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True)
        except Exception as e:
            raise TranscriptionError("OCR", f"Model initialization failed: {str(e)}")

    async def transcribe_image(self, image_file: bytes) -> str:
        """Transcribe image file to text"""
        if not self._model:
            self._initialize_model()

        try:
            result = self._model.ocr(image_file, cls=True)
            if not result:
                raise TranscriptionError("OCR", "Empty transcription result")

            transcripts = []
            for idx in range(len(result)):
                res = result[idx]
                for line in res:
                    transcripts.append(line[1][0])
            
            return '\n'.join(transcripts)
        except Exception as e:
            raise TranscriptionError("OCR", str(e))

# Create a singleton instance
ocr_service = OCRService()
