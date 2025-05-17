import argparse
import os
import time
import uuid
from dotenv import load_dotenv
import torch

# Load environment variables from app/.env
load_dotenv('app/.env')

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from openai import OpenAI

from funasr import AutoModel
# from funasr.utils.postprocess_utils import rich_transcription_postprocess

from paddleocr import PaddleOCR

import sys
sys.path.append(".")

KV_LIMIT = 256
DOMAIN = "oncology"
COLLECTION = ""

# Now these will pick up values from app/.env
LLM_API_URL = os.environ.get("LLM_API_URL", "http://localhost:11434/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemma3:1b")
FALLBACK_LLM_API_URL = os.environ.get("FALLBACK_LLM_API_URL", "http://localhost:11434/v1")
FALLBACK_MODEL_NAME = os.environ.get("FALLBACK_MODEL_NAME", "qwen2.5:0.5b")


# Global ASR model instance
_asr_model = None

def get_asr_model():
    """Get or create the ASR model instance using singleton pattern"""
    global _asr_model
    if _asr_model is None:
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        _asr_model = AutoModel(
            model="paraformer-zh",
            vad_model="fsmn-vad",
            vad_kwargs={
                "max_single_segment_time": 90000,  # 增加单段音频的最大时长
                "max_end_silence_time": 1200,      # 增加结束静音的最大时长
                "sil_to_speech_time_thres": 200,   # 增加从静音到语音的时间阈值
                "speech_to_sil_time_thres": 200,   # 增加从语音到静音的时间阈值
                "speech_2_noise_ratio": 1.2,       # 调整语音与噪音的比率
            },    
            punc_model="ct-punc",
            log_level="info",
            hub="ms",
            device=device,  # Use CUDA if available, otherwise CPU
            disable_update=True  # Prevent automatic updates
        )
    return _asr_model

template = \
"""
##患者信息：##

性别： 女
年龄： 34岁
就诊时间： 2024年1月15日 15:30
科别： 皮肤科门诊（大寨）

##主诉：##
双侧面颊皮疹1年余，加重20余天。

##现病史：##
- 1年多前，双侧面颊及颈部出现褐色斑片，无明显自觉症状。
- 3个月前，患者自行外购使用某淡斑产品后，局部皮肤出现烧灼感伴脱屑，但继续使用了3个月。
- 20天前，上述皮损部位颜色较前加重，烧灼感及脱屑无明显好转。

##既往史：##
体健，自述肝肾功能正常。

##体格检查：##
双侧面颊及颈部可见大致对称分布、形状不规则、边界欠清的褐色斑片，基底皮肤轻微红斑。

##辅助检查：##
无

##诊断：##
- 黄褐斑；刺激性皮炎

##处理：##
###药物治疗：###

- 加味道遥胶囊：每次3粒，每日两次，口服
- 复方甘草酸苷片：每次2片，每日三次，口服
- 维生素C片：每次1片，每日两次，口服
- 丁酸氢化可的松乳膏（尤卓尔乳膏）：每次1支，每日一次，外用
- 吡美莫司乳膏（爱宁达乳膏）：每次1支，每日一次，外用
- 多磺酸粘多糖乳膏（喜辽妥乳膏）：每次1支，每日一次，外用

###处理意见：###

- 停用一切功效性护肤品
- 考虑目前皮肤屏障受损，建议精简护肤
- 注意防晒
- 保持心情愉悦
- 2周后复诊
"""

sessions = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporary for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Needed for custom headers like X-Client-Type
)

ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True)
hotwords="./hotwords.txt"

class CDSSRequestModel(BaseModel):
    prompt: str
    role: str
    session_id: Optional[str] = None
    medical_records: Optional[str] = None
    history: Optional[List[str]] = None

class CDSSResponseModel(BaseModel):
    session_id: str
    content: str
    timestamp: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class VoiceFileRequest(BaseModel):
    voice_file: UploadFile = None
    is_json: bool = False  # Default value is False
    prompt: str = ""       # Default value is an empty string

class MRRequestModel(BaseModel):
    transcript: str
    medical_records: Optional[str] = None
    is_json: bool = True

class MRResponseModel(BaseModel):
    content: str
    timestamp: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ScaleResponseModel(BaseModel):
    answers: List[str]
    key_values: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

async def transcribe_image_to_text(image_file) -> str:
    result = ocr.ocr(image_file, cls=True)
    transcripts = []
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            transcripts.append(line[1][0])
    
    return '\n'.join(transcripts)

async def transcribe_voice_to_text(voice_file) -> str:
    temp_file = f"temp{time.time()}"
    with open(temp_file, "wb") as f:
        f.write(voice_file)
    print(f"temp file saved to {temp_file}")

    asr_model = get_asr_model()  # Get the singleton instance
    res = asr_model.generate(
        input=temp_file,
        use_itn=True,
        batch_size_s=300,
        merge_vad=True,
        merge_length_s=15,
        hotwords=hotwords
    )

    txt = res[0]["text"]
    os.remove(temp_file)
    print("########################")
    print(txt)
    # txt = rich_transcription_postprocess(txt)
    print("########################")
    # print(txt)
    return txt

async def extract_keywords_per_transcript(transcript: str, keywords: str):
    context_str = f"You are an intelligent assistant of a medical doctor in a Chinese hospital. You speak Chinese only. \
Your task is to generate a JSON-formatted key value list based on the transcript and keyword list. \
Here is a transcript parsed from medical checkup results or medical records of a patient: {transcript}"
    prompt = f"Please extract the following keywords out of the transcript: {keywords}\
If you cannot find the answer, simply assign 'NA' as the value of the keyword."
    client = OpenAI(base_url=LLM_API_URL, api_key="not used")
    llm_response = client.chat.completions.create(
        model = MODEL_NAME,
        messages = [
                    {"role": "system", "content": context_str},
                    {"role": "user",   "content": prompt}
                   ],
        response_format={"type": "json_object"},
        max_tokens=8000
    )
    return llm_response

async def qa_per_transcript(transcript: str, prompt: str):
    context_str = f"You are an intelligent assistant of a medical doctor in a Chinese hospital. You speak Chinese only. \
Here is a transcript parsed from medical checkup results or medical records of a patient: {transcript}"
    prompt = f"Please answer the following question only according to the transcript provided: {prompt}\
Simply answer the question. Do not explain."
# If you cannot find the answer, simply return 'Not found'. \
# Please do not mention any personal identity information."
    client = OpenAI(base_url=LLM_API_URL, api_key="not used")
    
    llm_response = client.chat.completions.create(
        model = MODEL_NAME,
        messages = [
                    {"role": "system", "content": context_str},
                    {"role": "user",   "content": prompt}
                   ],
        response_format={"type": "json_object"},
        max_tokens=8000
    )
    return llm_response

def create_chat_completion(client, model, messages, response_format=None):
    """
    Create a chat completion that works with both OpenAI and Ollama APIs
    """
    try:
        # Check if we're using Ollama (local URL)
        if "localhost" in LLM_API_URL or "127.0.0.1" in LLM_API_URL:
            # Ollama format
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False
            )
        else:
            # OpenAI format
            kwargs = {
                'model': model,
                'messages': messages,
            }
            if response_format:
                kwargs['response_format'] = response_format
                
            response = client.chat.completions.create(**kwargs)
            
        return response
    except Exception as e:
        print(f"Error in create_chat_completion: {str(e)}")
        raise

async def t2mr(transcript: str, medical_records: str, json: bool):
    json_str = "Your task is to generate a JSON-formatted medical record based on the patient's description. " if json else ""
    prompt = f"Please convert the conversation transcript into a formal medical record: {transcript}"
    context_str = f"You are an intelligent assistant of a medical doctor in a Chinese hospital. You speak Chinese only. \
{json_str} \
Please include the following items, in Chinese: \
主诉,现病史,既往史,过敏史,家族史,体格检查,辅助检查,诊断,处置意见,注意事项,中医辩证,中药处方. \
If no information for the item, just say: 无 \
Please do not miss including any checkup data. \
Please do not mention any personal identity information. \
Here is an example of a well-formatted medical record:\n{template}"

    if medical_records != '':
        context_str += f"\n Here are medical data from the patient's checkup: {medical_records}"

    try:
        client = OpenAI(base_url=LLM_API_URL, api_key="not used")

        kwargs = {
            'model': MODEL_NAME,
            'messages': [
                        {"role": "system", "content": context_str},
                        {"role": "user",   "content": prompt}
                       ],
        }

        if json:
            kwargs['response_format'] = {"type": "json_object"}

        print(f"prompts: {kwargs['messages']}")

        llm_response = create_chat_completion(
            client=client,
            model=MODEL_NAME,
            messages=kwargs['messages'],
            response_format=kwargs.get('response_format')
        )
        
        content = llm_response.choices[0].message.content    
        usage   = llm_response.usage
        print(llm_response)
        response = MRResponseModel(content=content,
                                 timestamp=int(time.time()),
                                 prompt_tokens=usage.prompt_tokens,
                                 completion_tokens=usage.completion_tokens,
                                 total_tokens=usage.total_tokens
                                 )
        
        return response
    except Exception as e:
        print(f"Error communicating with primary LLM service: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        
        # Try fallback LLM service
        FALLBACK_LLM_API_URL = os.environ.get("FALLBACK_LLM_API_URL", "http://localhost:11434/v1")
        FALLBACK_MODEL_NAME = os.environ.get("FALLBACK_MODEL_NAME", "qwen3-latest")
        
        try:
            print(f"Attempting to use fallback LLM service at {FALLBACK_LLM_API_URL}")
            fallback_client = OpenAI(base_url=FALLBACK_LLM_API_URL, api_key="not used")
            
            # Same kwargs as before, but with fallback model name
            kwargs['model'] = FALLBACK_MODEL_NAME
            
            fallback_response = create_chat_completion(
                client=fallback_client,
                model=FALLBACK_MODEL_NAME,
                messages=kwargs['messages'],
                response_format=kwargs.get('response_format')
            )
            
            content = fallback_response.choices[0].message.content
            usage = fallback_response.usage
            print(f"Fallback LLM service responded successfully")
            
            response = MRResponseModel(content=content,
                                     timestamp=int(time.time()),
                                     prompt_tokens=usage.prompt_tokens,
                                     completion_tokens=usage.completion_tokens,
                                     total_tokens=usage.total_tokens
                                     )
            return response
            
        except Exception as fallback_error:
            print(f"Error communicating with fallback LLM service: {str(fallback_error)}")
            if hasattr(fallback_error, 'response'):
                print(f"Fallback response status: {fallback_error.response.status_code}")
                print(f"Fallback response body: {fallback_error.response.text}")
                
            # Both primary and fallback services failed
            raise HTTPException(
                status_code=503,
                detail=f"All LLM Services Unavailable. Primary: {str(e)}. Fallback: {str(fallback_error)}. Please check LLM services."
            )

@app.post("/t2mr")
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
    transcript      = request_model.transcript
    medical_records = request_model.medical_records or ""
    is_json         = request_model.is_json or True
    response = await t2mr(transcript, medical_records, is_json)
    return response

@app.post("/a2mr")
async def a2mr_endpoint(files: List[UploadFile] = File(...),
                        medical_records: str = Form(""),
                        is_json: bool = Form(False)):
    """
    Voice or image files to a Medical Record.

    This endpoint provides you the capability of converting voice records with one or multiple files in audio, video or image formats into a medical record.
    
    - **files**: The multimedia files. For audio/video files, the format must be in content_type "audio/mpeg", "audio/wav", "audio/mp3", "audio/m4a", "video/quicktime" or "video/mp4".
                 For images, common image formats are supported.
    - **medical_records**: Additional medical data to be applied, regarding the medical record of the patient.
    - **is_json**: Whether the result in the json or text with markdown formats.

    Returns the medical records in json or text in markdown.
    """
    transcripts = []
    image_records = [medical_records]
    for file in files:
        print(f"Received file:{file.filename} with content type: {file.content_type}")
        
        # Handle audio/video files
        if file.content_type in ["audio/mpeg", "audio/wav", "audio/mp3", "audio/m4a", "video/quicktime", "video/mp4"]:
            voice_file = await file.read()
            transcript = await transcribe_voice_to_text(voice_file)
            if transcript == '':
                raise HTTPException(status_code=500, detail="Internal Server Error: Empty Transcript from Voice File")
            transcripts.append(transcript)
            
        # Handle image files
        elif file.content_type.startswith('image/'):
            image_file = await file.read()
            text = await transcribe_image_to_text(image_file)
            if text == '':
                raise HTTPException(status_code=500, detail="Internal Server Error: Empty Transcript from Image File")
            image_records.append(text)
        else:
            raise HTTPException(status_code=415, detail=f"Unsupported media type: {file.content_type}")
    
    if not transcripts:
        transcripts = image_records
        image_records = []
        if not transcripts:
            raise HTTPException(status_code=400, detail="No valid files were processed")
        
    response = await t2mr("\n".join(transcripts), "\n".join(image_records), is_json)
    return response

@app.post("/v2mr")
async def v2mr_endpoint(files: List[UploadFile] = File(...),
                        medical_records: str = Form(""),
                        is_json: bool = Form(False)):
    """
    Voice files to a Medical Record.

    This endpoint provides you the capability of converting voice records with one or multiple files in audio or video formats into a medical record.
    
    - **files**: The audio files. the format must be in content_type "audio/mpeg", "audio/wav", "audio/mp3", "audio/m4a", "video/quicktime" "video/mp4".
    - **medical_records**: Additional medical data to be applied, regarding the medical record of the patient.
    - **is_json**: Whether the result in the json or text with markdown formats.

    Returns the medical records in json or text in markdown.
    """
    
    transcripts = []
    for file in files:
        print(f"Received file:{file.filename} with content type: {file.content_type}")
        if file.content_type not in ["audio/mpeg", "audio/wav", "audio/mp3", "audio/m4a", "video/quicktime", "video/mp4"]:
            raise HTTPException(status_code=415, detail="Unsupported media type")
            
        voice_file = await file.read()
        transcript = await transcribe_voice_to_text(voice_file)
        if transcript == '':
            raise HTTPException(status_code=500, detail="Internal Server Error: Empty Transcript")
        transcripts.append(transcript)
    
    response = await t2mr("\n".join(transcripts), medical_records, is_json)
    return response

@app.post("/i2mr")
async def i2mr_endpoint(files: List[UploadFile] = File(...),
                        medical_records: str = Form(""),
                        is_json: bool = Form(False)):

    """
    Image files to a Medical Record.

    This endpoint provides you the capability of converting pictures of checkups etc., with one or multiple files in image formats into a medical record.
    
    - **files**: The image files. 
    - **medical_records**: Additional medical data to be applied, regarding the medical record of the patient.
    - **is_json**: Whether the result in the json or text with markdown formats.

    Returns the medical records in json or text in markdown.
    """

    transcripts = []
    for file in files:
        image_file = await file.read()
        transcript = await transcribe_image_to_text(image_file)
        transcripts.append(transcript)
        print(transcript)

    response = await t2mr("\n".join(transcripts), medical_records, is_json)
    return response

@app.post("/iqa")
async def iqa_endpoint(files: List[UploadFile] = File(...),
                       prompts: List[str] = Form(""),
                       keywords: List[str] = Form("")) -> ScaleResponseModel:

    transcripts = []    
    for file in files:
        image_file = await file.read()
        transcript = await transcribe_image_to_text(image_file)
        transcripts.append(transcript)
        print(transcript)

    prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
    answers = []
    for prompt in prompts:
        res = await qa_per_transcript(transcript, prompt)
        print(f"***BEGIN****{prompt}*********")
        print(res)
        print(f"*******{prompt}***END******")
        answers.append(res.choices[0].message.content)
        usage   = res.usage
        prompt_tokens += usage.prompt_tokens
        completion_tokens += usage.completion_tokens
        total_tokens += usage.total_tokens

    res = await extract_keywords_per_transcript(transcript, keywords)
    print(f"***BEGIN****{keywords}*********")
    print(res)
    print(f"*******{keywords}***END******")
    content = res.choices[0].message.content
    usage   = res.usage
    prompt_tokens += usage.prompt_tokens
    completion_tokens += usage.completion_tokens
    total_tokens += usage.total_tokens

    response = ScaleResponseModel(answers=answers, 
                                  key_values=content, 
                                  prompt_tokens=prompt_tokens, 
                                  completion_tokens=completion_tokens, 
                                  total_tokens=total_tokens)
    return response

@app.post("/mr2nl")
async def mr2nl(request_model: CDSSRequestModel) -> CDSSResponseModel:
    print(f"Received request body: {request_model}")
    role            = request_model.role
    medical_records = request_model.medical_records

    if role == 'doctor':
        context_str = "You are an intelligent assistant of a medical doctor in a Chinese hospital.\
You speak Chinese and is an expert in oncology. "
        prompt = f"Please rephrase the following {medical_records} into \
natural language to be used as a section for a medical record readable by doctors and patients. \
If there are multiple checkups in the medical records, please list them by time, in reverse order. \
Please only refer to the data provided. Do not explain."
    client = OpenAI(base_url=LLM_API_URL, api_key="not used")
    llm_response = create_chat_completion(
        client=client,
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": context_str},
            {"role": "user", "content": prompt}
        ]
    )
    
    content = llm_response.choices[0].message.content    
    usage   = llm_response.usage
    print(llm_response)
    
    response = CDSSResponseModel(session_id=str(uuid.uuid4()), 
                             content=content,
                             timestamp=int(time.time()),
                             prompt_tokens=usage.prompt_tokens,
                             completion_tokens=usage.completion_tokens,
                             total_tokens=usage.total_tokens
                             )

    return response

@app.post("/query")
async def process_text(request_model: CDSSRequestModel) -> CDSSResponseModel:
    print(f"Received request body: {request_model}")    
    prompt          = request_model.prompt
    role            = request_model.role
    session_id      = request_model.session_id
    medical_records = request_model.medical_records
    history         = request_model.history or []

    if not session_id:
        session_id = str(uuid.uuid4())

    # reset history per session if the user is sending one proactively
    if len(history) > 0:
        sessions[session_id] = history
        print(history)
    else:
        history = sessions[session_id] if session_id in sessions else []

    context_str = f"You are an intelligent assistant of a medical doctor in a Chinese hospital.\
You speak Chinese and is an expert in {DOMAIN}. \n"

    if role == 'doctor':
        #retrieved_info = rag_retrieval(prompt, index_med, metadata_med, chunks_med, chunk_to_doc_map_med, k=3)
        retrieved_info = ''

        context_str = f"{context_str} This question is for a patient with the following medical records: {medical_records}\n \
Here are some retrieved documents that may be relevant to the question: {retrieved_info}. \
Please try to answer the question with reference to name of the specific document and highlight it. \
If the documents are irrelevant, do not mention them. \
You may seek answers out of the scope of given documents, if they cannot answer the patient's questions. \
Since the answer is for an expert doctor, therefore please keep it precise, professional, and evident-based. \
The treatment plans or advices should be personalized. The procedures or medicines recommended in the plans should refer back to the patient's conditions. \
Do not talk in a general way that a doctor should have known. Do not answer in a tone toward a general population and a group, but only specific to this individual patient. \
Even the titles of the plan should be specific. Do not use general terms such as systematic, comprehensive etc."
    else:
        context_str = f"{context_str} This question is for a patient with the following medical records: \
{medical_records}\n \
The answer is for a patient, so please use words that can be understandable by someone \
who may not have extensive medical knowledge. Please use a kind and encouraging tone. \
Please try to answer in concisely less than 20 sentences and one or two key points highlighted. \
If necessary, please ask the patient questions for his or her conditions first.\n"


    messages = [
        {"role": "assistant", "content": '\n'.join(history)},
        {"role": "system", "content": context_str},
        {"role": "user", "content": prompt}
    ]
    print(f"messages: ------BEGIN-------\n{messages}\n------END--------")

    client = OpenAI(base_url=LLM_API_URL, api_key="not used")
    llm_response = create_chat_completion(
        client=client,
        model=MODEL_NAME,
        messages=messages
    )
    
    # append new content into history and set it in the session
    content = llm_response.choices[0].message.content    
    usage   = llm_response.usage
    print(llm_response)
    history.append(content)
    sessions[session_id] = history
    
    response = CDSSResponseModel(session_id=session_id, 
                             content=content,
                             timestamp=int(time.time()),
                             prompt_tokens=usage.prompt_tokens,
                             completion_tokens=usage.completion_tokens,
                             total_tokens=usage.total_tokens
                             )

    return response


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description='RAG based on Markdown or text files.')
    parser.add_argument('--domain', 
                        type=str, 
                        help='The expertise domain of RAG', 
                        default='oncology')
    parser.add_argument('--collection', 
                        type=str, 
                        help='The collection of RAG', 
                        default='med_refv3')
    parser.add_argument('--port', 
                        type=int, 
                        help='The listening port', 
                        default=8000)
    args = parser.parse_args()
    DOMAIN = args.domain
    COLLECTION = args.collection

    uvicorn.run("jcdss:app", 
                host="0.0.0.0", 
                port=args.port,
                reload=True
                )
