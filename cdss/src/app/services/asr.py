import os
import time
import torch
from funasr import AutoModel
from app.core.config import ASR_CONFIG
from app.core.exceptions import TranscriptionError

class ASRService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ASRService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            self._initialize_model()

    def _initialize_model(self):
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Initializing ASR model on device: {device}")
            
            self._model = AutoModel(
                model="paraformer-zh",
                vad_model="fsmn-vad",
                vad_kwargs=ASR_CONFIG["vad_kwargs"],
                punc_model="ct-punc",
                log_level="info",
                hub="ms",
                device=device,
                disable_update=True
            )
        except Exception as e:
            raise TranscriptionError("ASR", f"Model initialization failed: {str(e)}")

    async def transcribe_voice(self, voice_file: bytes) -> str:
        """Transcribe voice file to text"""
        if not self._model:
            self._initialize_model()

        temp_file = f"temp{time.time()}"
        try:
            with open(temp_file, "wb") as f:
                f.write(voice_file)
            
            res = self._model.generate(
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
        except Exception as e:
            raise TranscriptionError("ASR", str(e))
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

# Create a singleton instance
asr_service = ASRService()
