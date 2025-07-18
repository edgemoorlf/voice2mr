# Voice2MR

A modern medical record system with two main components:
1. MedAI: Progressive Web App (PWA) for the frontend interface
2. CDSS: Clinical Decision Support System backend

## Components

### MedAI (Frontend PWA)
- Modern, responsive web interface
- Progressive Web App capabilities
- Offline support
- Multi-language interface
- Located in `medai/` directory
- Built with TypeScript and Next.js

### CDSS (Backend)
- Voice to Medical Records (v2mr)
- Image to Medical Records (i2mr)
- Text to Medical Records (t2mr)
- Image Question-Answering (iqa)
- Clinical Decision Support System
- Located in `cdss/` directory
- Built with Python and FastAPI

## Project Structure

```
project_root/
├── cdss/                   # Backend services
│   ├── src/
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── api/
│   │       │   ├── routes/
│   │       │   │   ├── cdss.py
│   │       │   │   └── medical_records.py
│   │       │   └── models/
│   │       ├── core/
│   │       │   ├── config.py
│   │       │   └── dependencies.py
│   │       └── services/
│   │           ├── asr.py
│   │           ├── ocr.py
│   │           └── llm.py
│   ├── tests/             # Backend tests
│   │   └── unit/
│   ├── pyproject.toml     # Python project configuration
│   ├── requirements.txt   # Python dependencies
│   ├── pytest.ini        # Python test configuration
│   └── hotwords.txt      # Domain-specific vocabulary
├── medai/                 # Frontend PWA
│   ├── src/
│   │   └── app/
│   ├── public/
│   ├── tests/
│   ├── package.json      # Node.js dependencies
│   └── tsconfig.json     # TypeScript configuration
├── .env                  # Environment variables (shared)
└── README.md            # Project documentation
```

## Installation and Setup

### Backend (CDSS)

1. Navigate to the CDSS directory:
```bash
cd cdss
```

2. Install the dependencies:
```bash
pip install -e ".[dev]"  # Installs both project and test dependencies
```

3. Create a `.env` file in the root directory:
```
LLM_API_URL=http://localhost:11434/v1
MODEL_NAME=qwen2.5:latest
```

### Frontend (MedAI)

See `medai/README.md` for frontend setup instructions.

## Running the Applications

### Backend (CDSS)

You can run the backend in several ways:

#### 1. Development Mode

- Using the main entry point script (recommended):

```bash
cd cdss
python main.py --port 8000 --reload
```

- Using the installed CLI (after `pip install -e .`):

```bash
cd cdss
voice2mr --port 8000 --reload
```

- Using Uvicorn directly:

```bash
cd cdss
uvicorn src.app:app --reload --port 8000
```

The API will be available at http://localhost:8000/api/docs for Swagger documentation.

#### 2. Production Mode

- Using Gunicorn (recommended for production):

```bash
cd cdss
pip install gunicorn

gunicorn src.app:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

- Using Docker (optional):

Create a `Dockerfile` in the `cdss` directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app/src

# Run with gunicorn
CMD ["gunicorn", "src.app:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
```

Build and run the Docker container:

```bash
docker build -t cdss .
docker run -p 8000:8000 --env-file .env cdss
```

### Frontend
See `medai/README.md`


### vLLM Setup


```bash
vllm serve modelscope/models/LLM-Research/gemma-3-27b-it --enable-lora --lora-modules adapter1=tr/saves/Gemma-3-27B-Instruct/lora/train_2025-06-16-14-18-24/ --max-loras 4 --max-lora-rank 16

```

Alternatively, to load lora at runtime

```bash
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
vllm serve modelscope/models/LLM-Research/gemma-3-27b-it --enable-lora
```