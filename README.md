# Voice2MR API

A FastAPI application that provides various endpoints for converting voice and image inputs to medical records, as well as providing clinical decision support.

## Features

- Voice to Medical Records (v2mr): Convert voice recordings to structured medical records
- Image to Medical Records (i2mr): Convert images with medical text to structured medical records
- Text to Medical Records (t2mr): Convert text transcripts to structured medical records
- Image Question-Answering (iqa): Extract information from medical images and answer questions
- Clinical Decision Support System (CDSS): Get AI-assisted medical advice based on medical records

## Project Structure

```
project_root/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── cdss.py
│   │   │   └── medical_records.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── services/
│       ├── __init__.py
│       ├── asr.py
│       ├── ocr.py
│       └── llm.py
├── tests/
│   └── __init__.py
├── .env
├── requirements.txt
├── main.py
└── README.md
```

## Installation

1. Clone the repository
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory (optional):

```
LLM_API_URL=http://localhost:11434/v1
MODEL_NAME=qwen2.5:latest
DOMAIN=oncology
COLLECTION=med_refv3
```

## Running the Application

```bash
python main.py --port 8000 --debug
```

Or simply:

```bash
python main.py
```

The API will be available at http://localhost:8000/api/docs for Swagger documentation.

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

- FastAPI: Web framework
- OpenAI API: LLM interface
- FunASR: Audio speech recognition
- PaddleOCR: Optical character recognition

## License

See the LICENSE file for details.

## End-to-End (E2E) PWA Testing

To run the Playwright E2E test for PWA features in a production environment, use the following command:

```sh
NODE_ENV=production npx playwright test tests/e2e-pwa.spec.ts
```

**Notes:**
- This command ensures the tests run with `NODE_ENV=production`, which is required for service worker and PWA features to be active.
- Make sure your app is built and served in production mode before running the test (e.g., `npm run build && npm start`).
- The test file `tests/e2e-pwa.spec.ts` should contain your PWA-related E2E tests.
- For more details, see the test plan in `docs/testplans.md`. 