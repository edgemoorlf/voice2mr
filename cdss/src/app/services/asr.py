import os
import time
import torch
from funasr import AutoModel
from app.core.config import ASR_CONFIG, LANGUAGE_MODEL_CONFIG
from app.core.exceptions import TranscriptionError
from app.core.i18n import SUPPORTED_LANGUAGES

class ASRService:
    _instance = None
    _models = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ASRService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Remove automatic initialization
        pass

    def _initialize_model(self, language: str):
        """Initialize a specific language model only when needed"""
        if language not in SUPPORTED_LANGUAGES or language in self._models:
            return

        config = LANGUAGE_MODEL_CONFIG["asr"].get(language, {})
        if not config.get("enabled", False):
            print(f"ASR model for {language} is disabled in config")
            return

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing ASR model for {language} on device: {device}")

        try:
            if language == "zh" and config["type"] == "funasr":
                self._models[language] = AutoModel(
                    model=config["model"],
                    vad_model="fsmn-vad",
                    vad_kwargs=ASR_CONFIG["vad_kwargs"],
                    punc_model="ct-punc",
                    log_level="info",
                    hub="ms",
                    device=device,
                    disable_update=True
                )
            elif config["type"] == "whisper":
                self._models[language] = self._initialize_whisper_model(device, language)
            elif config["type"] == "external":
                self._models[language] = {"type": "external", "language": language, "provider": config.get("provider")}
        except Exception as e:
            print(f"Failed to load ASR model for {language}: {e}")
            # For non-Chinese languages, fall back to external service
            if language != "zh":
                self._models[language] = {"type": "external", "language": language}

    def _initialize_whisper_model(self, device: str, language: str):
        """Initialize Whisper model for non-Chinese languages"""
        try:
            # Option 1: Use OpenAI Whisper
            import whisper
            model = whisper.load_model(LANGUAGE_MODEL_CONFIG["asr"][language]["model"], device=device)
            return {"type": "whisper", "model": model, "language": language}
        except ImportError:
            print(f"Whisper not available for {language}, will use external API")
            return {"type": "external", "language": language}
        except Exception as e:
            print(f"Failed to load Whisper model for {language}: {e}")
            return {"type": "external", "language": language}

    async def transcribe_voice(self, voice_file: bytes, language: str = "zh") -> str:
        """Transcribe voice file to text with language awareness"""
        if language not in SUPPORTED_LANGUAGES:
            language = "zh"  # fallback to Chinese

        # Lazy initialization of the model
        if language not in self._models:
            self._initialize_model(language)

        # If model initialization failed or is disabled, try Chinese as fallback
        if language not in self._models and language != "zh":
            print(f"No ASR model available for {language}, falling back to Chinese")
            language = "zh"
            if language not in self._models:
                self._initialize_model(language)

        model_info = self._models.get(language)
        if not model_info:
            raise TranscriptionError("ASR", f"No ASR model available for {language}")

        temp_file = f"temp{time.time()}"
        try:
            with open(temp_file, "wb") as f:
                f.write(voice_file)
            
            if language == 'zh' and not isinstance(model_info, dict):
                # Use FunASR for Chinese
                res = model_info.generate(
                    input=temp_file,
                    use_itn=True,
                    batch_size_s=300,
                    merge_vad=True,
                    merge_length_s=15,
                    hotwords="./hotwords.txt"
                )
                if not res or not res[0] or "text" not in res[0]:
                    raise TranscriptionError("ASR", "Empty transcription result")
                return res[0]["text"]
                
            elif model_info.get("type") == "whisper" and "model" in model_info:
                # Use Whisper for other languages
                result = model_info["model"].transcribe(
                    temp_file, 
                    language=language if language != 'zh' else None
                )
                return result["text"]
                
            else:
                # Route to external service (OpenAI Whisper API, Azure, etc.)
                return await self._transcribe_external(temp_file, language)
                
        except Exception as e:
            raise TranscriptionError("ASR", str(e))
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    async def _transcribe_external(self, file_path: str, language: str) -> str:
        """Use external API for transcription"""
        try:
            # Option 1: OpenAI Whisper API
            import openai
            with open(file_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language=language if language != 'zh' else 'zh'
                )
            return transcript.text
        except Exception as e:
            raise TranscriptionError("ASR", f"External transcription failed: {str(e)}")

# Create a singleton instance
asr_service = ASRService()
