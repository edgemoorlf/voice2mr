from paddleocr import PaddleOCR
from app.core.exceptions import TranscriptionError
from app.core.i18n import SUPPORTED_LANGUAGES
from app.core.config import LANGUAGE_MODEL_CONFIG

class OCRService:
    _instance = None
    _models = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Remove automatic initialization
        pass

    def _initialize_model(self, language: str):
        """Initialize a specific language model only when needed"""
        if language not in SUPPORTED_LANGUAGES or language in self._models:
            return

        config = LANGUAGE_MODEL_CONFIG["ocr"].get(language, {})
        if not config.get("enabled", False):
            print(f"OCR model for {language} is disabled in config")
            return

        try:
            if config["type"] == "paddleocr":
                try:
                    self._models[language] = PaddleOCR(
                        use_angle_cls=True,
                        lang=config["lang"],
                        use_gpu=True
                    )
                except Exception as e:
                    print(f"Failed to load PaddleOCR model for {language}: {e}")
                    if language != "zh":  # Only fall back for non-Chinese
                        self._models[language] = {"type": "external", "language": language}
            elif config["type"] == "external":
                self._models[language] = {
                    "type": "external",
                    "language": language,
                    "provider": config.get("provider")
                }
        except Exception as e:
            print(f"Failed to initialize OCR model for {language}: {e}")
            if language != "zh":  # Only fall back for non-Chinese
                self._models[language] = {"type": "external", "language": language}

    async def transcribe_image(self, image_file: bytes, language: str = "zh") -> str:
        """Transcribe image file to text with language awareness"""
        if language not in SUPPORTED_LANGUAGES:
            language = "zh"  # fallback

        # Lazy initialization of the model
        if language not in self._models:
            self._initialize_model(language)

        # If model initialization failed or is disabled, try Chinese as fallback
        if language not in self._models and language != "zh":
            print(f"No OCR model available for {language}, falling back to Chinese")
            language = "zh"
            if language not in self._models:
                self._initialize_model(language)

        model = self._models.get(language)
        if not model:
            raise TranscriptionError("OCR", f"No OCR model available for {language}")
        
        try:
            if isinstance(model, dict) and model.get("type") == "external":
                # Route to external OCR service
                return await self._transcribe_external(image_file, language)
            else:
                # Use PaddleOCR
                result = model.ocr(image_file, cls=True)
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

    async def _transcribe_external(self, image_file: bytes, language: str) -> str:
        """Use external OCR service for unsupported languages"""
        try:
            # Option 1: Azure Computer Vision
            # Option 2: Google Cloud Vision
            # Option 3: AWS Textract
            # For now, return a placeholder
            raise TranscriptionError("OCR", f"External OCR for {language} not implemented")
        except Exception as e:
            raise TranscriptionError("OCR", f"External OCR failed: {str(e)}")

# Create a singleton instance
ocr_service = OCRService()
