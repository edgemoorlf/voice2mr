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
DOMAIN=oncology
COLLECTION=med_refv3
```

### Frontend (MedAI)

See `medai/README.md` for frontend setup instructions.

## Running the Applications

### Backend
```bash
cd cdss
python -m src.app --port 8000 --debug
```

The API will be available at http://localhost:8000/api/docs for Swagger documentation.

### Frontend
See `medai/README.md` for frontend running instructions.

## Testing

### Backend Tests

From the `cdss` directory:
```bash
pytest  # Run all tests
pytest tests/unit/  # Run unit tests
pytest tests/integration/  # Run integration tests
pytest tests/e2e/  # Run end-to-end tests
pytest --cov=src.app tests/  # Run tests with coverage
```

### Frontend Tests
See `medai/README.md` for frontend testing instructions.

## API Endpoints

### Medical Records

- `POST /api/t2mr`: Convert text transcript to medical record
- `POST /api/v2mr`: Convert voice recording to medical record
- `POST /api/i2mr`: Convert image to medical record
- `POST /api/iqa`: Extract information from medical images and answer questions

### CDSS

- `POST /api/query`: Get AI-assisted medical advice
- `POST /api/mr2nl`: Convert structured medical records to natural language

## Dependencies

### Backend (Python)
- FastAPI: Web framework
- OpenAI API: LLM interface
- FunASR: Audio speech recognition
- PaddleOCR: Optical character recognition

### Frontend (TypeScript)
See `medai/README.md` for frontend dependencies.

## License

See the LICENSE file for details. 