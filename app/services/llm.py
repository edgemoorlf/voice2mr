"""LLM service module"""
import time
import uuid
from fastapi import Depends
from openai import OpenAI

from app.core.dependencies import get_llm_client, get_sessions
from app.core.config import settings
from app.models.schemas import CDSSResponseModel, MRResponseModel, ScaleResponseModel
from app.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


async def extract_keywords_per_transcript(transcript: str, keywords: str, client: OpenAI = Depends(get_llm_client)):
    """
    Extract keywords from a transcript.
    
    Args:
        transcript: The transcript to extract keywords from
        keywords: The keywords to extract
        client: The OpenAI client
        
    Returns:
        The LLM response
    """
    logger.info(f"Extracting keywords from transcript: {keywords}")
    start_time = time.time()
    
    context_str = f"You are an intelligent assistant of a medical doctor in a Chinese hospital. You speak Chinese only. \
Your task is to generate a JSON-formatted key value list based on the transcript and keyword list. \
Here is a transcript parsed from medical checkup results or medical records of a patient: {transcript}"
    prompt = f"Please extract the following keywords out of the transcript: {keywords}\
If you cannot find the answer, simply assign 'NA' as the value of the keyword."
    
    try:
        logger.debug(f"Sending request to LLM model: {settings.MODEL_NAME}")
        llm_response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": context_str},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=8000
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Keywords extraction completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Tokens used - Prompt: {llm_response.usage.prompt_tokens}, Completion: {llm_response.usage.completion_tokens}")
        
        return llm_response
    except Exception as e:
        logger.error(f"Error during keyword extraction: {str(e)}", exc_info=True)
        raise


async def qa_per_transcript(transcript: str, prompt: str, client: OpenAI = Depends(get_llm_client)):
    """
    Question answering based on a transcript.
    
    Args:
        transcript: The transcript to answer questions from
        prompt: The question prompt
        client: The OpenAI client
        
    Returns:
        The LLM response
    """
    logger.info(f"Processing QA for prompt: {prompt[:50]}...")
    start_time = time.time()
    
    context_str = f"You are an intelligent assistant of a medical doctor in a Chinese hospital. You speak Chinese only. \
Here is a transcript parsed from medical checkup results or medical records of a patient: {transcript}"
    qa_prompt = f"Please answer the following question only according to the transcript provided: {prompt}\
Simply answer the question. Do not explain."
    
    try:
        logger.debug(f"Sending request to LLM model: {settings.MODEL_NAME}")
        llm_response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": context_str},
                {"role": "user", "content": qa_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=8000
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"QA processing completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Tokens used - Prompt: {llm_response.usage.prompt_tokens}, Completion: {llm_response.usage.completion_tokens}")
        
        return llm_response
    except Exception as e:
        logger.error(f"Error during QA processing: {str(e)}", exc_info=True)
        raise


async def transcript_to_medical_record(
    transcript: str, 
    medical_records: str = "", 
    is_json: bool = True,
    client: OpenAI = Depends(get_llm_client)
) -> MRResponseModel:
    """
    Convert a transcript to a medical record.
    
    Args:
        transcript: The transcript to convert
        medical_records: Additional medical records
        is_json: Whether to return JSON or text
        client: The OpenAI client
        
    Returns:
        MRResponseModel: The medical record response
    """
    logger.info(f"Converting transcript to medical record (JSON format: {is_json})")
    start_time = time.time()
    
    json_str = "Your task is to generate a JSON-formatted medical record based on the patient's description. " if is_json else ""
    prompt = f"Please convert the conversation transcript into a formal medical record: {transcript}"
    context_str = f"You are an intelligent assistant of a medical doctor in a Chinese hospital. You speak Chinese only. \
{json_str} \
Please include the following items, in Chinese: \
主诉,现病史,既往史,过敏史,家族史,体格检查,辅助检查,诊断,处置意见,注意事项,中医辩证,中药处方. \
If no information for the item, just say: 无 \
Please do not miss including any checkup data. \
Please do not mention any personal identity information."

    if medical_records != '':
        context_str += f"\n Here are medical data from the patient's checkup: {medical_records}"
        logger.debug("Added additional medical records to context")

    try:
        logger.debug(f"Sending request to LLM model: {settings.MODEL_NAME}")
        llm_response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": context_str},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=8000
        )
        
        content = llm_response.choices[0].message.content    
        usage = llm_response.usage
        
        elapsed_time = time.time() - start_time
        logger.info(f"Medical record conversion completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Tokens used - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}")
        
        response = MRResponseModel(
            content=content,
            timestamp=int(time.time()),
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens
        )
        
        return response
    except Exception as e:
        logger.error(f"Error during transcript to medical record conversion: {str(e)}", exc_info=True)
        raise


async def medical_record_to_natural_language(
    role: str, 
    medical_records: str,
    client: OpenAI = Depends(get_llm_client)
) -> CDSSResponseModel:
    """
    Convert medical records to natural language.
    
    Args:
        role: The role of the user
        medical_records: The medical records to convert
        client: The OpenAI client
        
    Returns:
        CDSSResponseModel: The response
    """
    logger.info(f"Converting medical records to natural language for role: {role}")
    start_time = time.time()
    
    if role == 'doctor':
        context_str = "You are an intelligent assistant of a medical doctor in a Chinese hospital.\
You speak Chinese and is an expert in oncology. "
        prompt = f"Please rephrase the following {medical_records} into \
natural language to be used as a section for a medical record readable by doctors and patients. \
If there are multiple checkups in the medical records, please list them by time, in reverse order. \
Please only refer to the data provided. Do not explain."
    
    try:
        logger.debug(f"Sending request to LLM model: {settings.MODEL_NAME}")
        llm_response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": context_str},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = llm_response.choices[0].message.content    
        usage = llm_response.usage
        
        elapsed_time = time.time() - start_time
        logger.info(f"Medical record to natural language conversion completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Tokens used - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}")
        
        response = CDSSResponseModel(
            session_id=str(uuid.uuid4()), 
            content=content,
            timestamp=int(time.time()),
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens
        )

        return response
    except Exception as e:
        logger.error(f"Error during medical record to natural language conversion: {str(e)}", exc_info=True)
        raise


async def process_cdss_query(
    prompt: str,
    role: str,
    session_id: str = None,
    medical_records: str = None,
    history: list = None,
    client: OpenAI = Depends(get_llm_client),
    sessions_dict = Depends(get_sessions)
) -> CDSSResponseModel:
    """
    Process a CDSS query.
    
    Args:
        prompt: The prompt
        role: The role of the user
        session_id: The session ID
        medical_records: Medical records
        history: Chat history
        client: The OpenAI client
        sessions_dict: The sessions dictionary
        
    Returns:
        CDSSResponseModel: The response
    """
    logger.info(f"Processing CDSS query for role: {role}")
    start_time = time.time()
    
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.debug(f"Generated new session ID: {session_id}")

    # Reset history per session if the user is sending one proactively
    if history and len(history) > 0:
        sessions_dict[session_id] = history
        logger.debug(f"Updated session history for session {session_id}, history length: {len(history)}")
    else:
        history = sessions_dict.get(session_id, [])
        logger.debug(f"Retrieved session history for session {session_id}, history length: {len(history)}")

    context_str = f"You are an intelligent assistant of a medical doctor in a Chinese hospital.\
You speak Chinese and is an expert in {settings.DOMAIN}. \n"

    if role == 'doctor':
        # Add retrieved information if available
        retrieved_info = ''  # Placeholder for RAG retrieval
        logger.debug("Using doctor role context")

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
        logger.debug("Using patient role context")
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

    try:
        logger.debug(f"Sending request to LLM model: {settings.MODEL_NAME}")
        llm_response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        # Append new content into history and set it in the session
        content = llm_response.choices[0].message.content    
        usage = llm_response.usage
        
        history.append(content)
        sessions_dict[session_id] = history
        logger.debug(f"Updated session history, new length: {len(history)}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"CDSS query processing completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Tokens used - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}")
        
        response = CDSSResponseModel(
            session_id=session_id, 
            content=content,
            timestamp=int(time.time()),
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens
        )

        return response
    except Exception as e:
        logger.error(f"Error during CDSS query processing: {str(e)}", exc_info=True)
        raise 