# Manual Service Worker & PWA Feature Test Plan

## Recent Update (2025-05-26)
- Manual service worker restored after removing next-pwa.
- Fixed a syntax error in the fetch event handler that prevented service worker registration.
- Offline fallback for navigation requests now works as expected: uncached pages show offline.html, not a 404.
- All core PWA tests (registration, caching, offline fallback) now pass.
- See change_logs.md for details.

## Checklist Table

| Test Area                | What to Check                                      | Pass/Fail |
|--------------------------|----------------------------------------------------|-----------|
| Build & Serve            | App runs in production mode                        |           |
| SW Registration          | Service worker is registered & active              |           |
| Cache Storage            | Essential assets are cached                        |           |
| Offline Fallback         | Offline.html served for uncached pages             |           |
| Asset Caching            | Visited pages/assets load offline                  |           |
| Manifest & Icons         | Manifest loads, icons display, A2HS works          |           |
| Console Errors           | No errors during registration or fetch             |           |
| Cross-Browser/Device     | Works in multiple browsers/devices                 |           |
| Update Handling          | New SW activates, old cache cleaned (if tested)    |           |
| Accessibility/UX         | Offline page is accessible and clear               |           |

---

## Detailed Steps

### 1. Build and Serve the Production App
- Run:
  ```sh
  npm run build
  npm start
  ```
- Ensure you are testing the production build, as service workers are only active in production.

### 2. Service Worker Registration
- Open your app in Chrome/Edge/Firefox.
- Go to DevTools → Application → Service Workers.
- Confirm:
  - The service worker (`service-worker.js`) is registered and activated.
  - The scope is correct (should be `/`).

### 3. Cache Storage Verification
- In DevTools → Application → Cache Storage:
  - Check for a cache named `medai-cache-v1`.
  - Confirm that the files listed in `urlsToCache` (e.g., `/`, `/manifest.json`, `/offline.html`) are present.
  - If you added icons or other assets, verify they are cached.

### 4. Offline Fallback Behavior
- In DevTools → Network, check the "Offline" box.
- Try the following:
  - Reload the app on the root URL (`/`). It should load from cache.
  - Navigate to a page that was not previously visited/cached. The service worker should serve `offline.html`.
  - If you have a homepage link in `offline.html`, test that it works offline if `/` is cached.

### 5. Asset Caching Strategy
- While online, visit several pages and assets (images, CSS, etc.).
- Go offline and try to revisit those pages/assets:
  - They should load from cache if previously visited.
  - New, unvisited pages should show the offline fallback.

### 6. Manifest and Icon Verification
- In DevTools → Application → Manifest:
  - Confirm the manifest loads without errors.
  - Check that icons are displayed correctly.
- On your device, "Add to Home Screen" and verify the app icon and name.

### 7. No Errors in Console
- Check the browser console for:
  - Service worker registration errors.
  - Fetch/caching errors.
  - Manifest or icon loading errors.

### 8. Cross-Browser and Device Testing
- Test in at least two browsers (e.g., Chrome and Firefox).
- Test on desktop and a mobile device (or emulator).
- On mobile, try "Add to Home Screen" and launch the app from the icon.

### 9. Update Handling (Optional)
- Make a small change to `service-worker.js` (e.g., update the cache name).
- Rebuild and restart the app.
- Reload the app in the browser and confirm:
  - The new service worker is installed and activated.
  - Old caches are cleaned up.

### 10. Accessibility & UX
- Ensure the offline page is accessible and clearly communicates the offline state.
- Test keyboard navigation and screen reader compatibility for the offline page.

---

## Environment-Specific Testing Strategies

Service workers introduce behavior that differs significantly between development and production environments. It's crucial to tailor your testing approach accordingly. Your application's `ServiceWorkerRegister.tsx` component currently (and correctly) only attempts to register the service worker when `process.env.NODE_ENV === 'production'`.

### A. Development Environment (e.g., running `npm run dev`)

*   **Service Worker Status:** Expected to be **INACTIVE**.
    *   **Verification:**
        *   Open DevTools → Application → Service Workers. No service worker from `service-worker.js` should be listed as active and running for the current origin.
        *   `navigator.serviceWorker.controller` should be `null` in the console.
        *   No console logs from `ServiceWorkerRegister.tsx` regarding successful registration should appear.
*   **Primary Testing Focus:**
    *   Application logic, UI development, and feature implementation *without* service worker interference.
    *   Hot Module Replacement (HMR) and fast refresh should work as expected.
*   **Testing SW-related code (if absolutely necessary during dev):**
    1.  **Recommended Approach (for accuracy):** Build and serve the app in production mode locally (`npm run build && npm start`). This is the most reliable way to test the true PWA behavior.
    2.  **Alternative (for quick checks, use with caution):**
        *   Temporarily modify `ServiceWorkerRegister.tsx` to allow registration in development (e.g., by removing or altering the `process.env.NODE_ENV === 'production'` check). **Remember to revert this change before committing.**
        *   Manually register the service worker via browser DevTools (e.g., in Chrome's Application tab, you can check "Update on reload" and sometimes force registration).
        *   **Caveat:** Aggressive caching in dev can lead to confusion. Clear the cache and unregister the SW frequently if using this approach.

### B. Production Environment (e.g., `npm run build && npm start`, Staging, or Live Production)

*   **Service Worker Status:** Expected to be **ACTIVE** and controlling the page after initial registration and a subsequent page load/navigation.
    *   **Verification:**
        *   Open DevTools → Application → Service Workers. `service-worker.js` should be listed as "activated and is running."
        *   `navigator.serviceWorker.controller` should return a `ServiceWorker` object in the console (after the SW has taken control).
        *   Console logs from `ServiceWorkerRegister.tsx` should indicate successful registration.
        *   Console logs from `service-worker.js` (e.g., "Opened cache", "Advanced Service Worker Loaded") should be visible.
*   **Primary Testing Focus:**
    *   All PWA features outlined in the "Detailed Steps" section of this test plan. This includes:
        *   Successful SW registration and activation.
        *   Correct caching of `urlsToCache` and dynamically fetched assets.
        *   Offline fallback functionality.
        *   Manifest loading, icon display, and Add to Home Screen (A2HS) prompts/behavior.
        *   Cache versioning and cleanup on SW update (if applicable).
        *   Any advanced SW features like background sync or periodic sync.
*   **Conditions:**
    *   Always test on a clean session (e.g., incognito mode or after clearing site data) to simulate a first-time user experience.
    *   Test on multiple browsers and devices as per the "Cross-Browser and Device Testing" section.
    *   Ensure the server is serving assets over HTTPS (or localhost for local testing), as service workers require a secure context.

### General Guidance for PWA Testing

*   **Prerequisite:** Most tests in the "Detailed Steps" section implicitly assume the application is running from a **production build** where the service worker is active. Consider adding a note to relevant sections or a general preamble.
*   **Clarity:** Be explicit in test case descriptions about the expected environment (dev vs. prod build) and the consequent service worker state.
*   **Automation:** For e2e tests (like Playwright), ensure the test environment correctly sets `NODE_ENV=production` and the application is served from a production build when testing PWA features.

---

## Running E2E PWA Tests with Playwright

To run the Playwright end-to-end test for PWA features in a production environment, use:

```sh
NODE_ENV=production npx playwright test tests/e2e-pwa.spec.ts
```

**Instructions:**
- Ensure your app is built and running in production mode (e.g., `npm run build && npm start`) before running the test.
- This command sets `NODE_ENV=production` so that service worker and PWA features are enabled during testing.
- The test file `tests/e2e-pwa.spec.ts` should contain your PWA E2E scenarios.
- For more details, see the E2E section in the project README.

# Backend API Test Plan

## Overview
Tests should be organized in the `tests` directory with the following structure:
```
tests/
├── unit/
│   ├── services/
│   │   ├── test_asr.py
│   │   ├── test_ocr.py
│   │   ├── test_llm.py
│   │   └── test_medical_record.py
│   └── core/
│       ├── test_config.py
│       └── test_i18n.py
├── integration/
│   ├── test_voice_endpoints.py
│   ├── test_image_endpoints.py
│   └── test_chat_endpoints.py
└── e2e/
    └── test_full_workflow.py
```

## Test Categories

### 1. Unit Tests

#### Core Components
- **Configuration (`test_config.py`)**
  - Test environment variable loading
  - Test default values
  - Test supported audio types
  - Test LLM configurations

- **i18n (`test_i18n.py`)**
  - Test language prompt retrieval
  - Test fallback to default language
  - Test medical record template retrieval
  - Test all supported languages

#### Services
- **ASR Service (`test_asr.py`)**
  - Test voice transcription with different audio formats
  - Test error handling for invalid audio
  - Test Chinese speech recognition accuracy
  - Test VAD (Voice Activity Detection) settings

- **OCR Service (`test_ocr.py`)**
  - Test image text extraction
  - Test different image formats
  - Test Chinese character recognition
  - Test error handling for invalid images

- **LLM Service (`test_llm.py`)**
  - Test completion generation
  - Test primary/fallback service switching
  - Test JSON response formatting
  - Test error handling

- **Medical Record Service (`test_medical_record.py`)**
  - Test medical record generation
  - Test chat processing
  - Test voice file processing
  - Test image file processing

### 2. Integration Tests

#### Voice Endpoints (`test_voice_endpoints.py`)
- **POST /v2mr**
  ```python
  def test_voice_to_medical_record():
      # Test single audio file conversion
      # Test multiple audio files
      # Test unsupported audio format
      # Test empty audio file
      # Test with additional medical records
      # Test different languages
  ```

#### Image Endpoints (`test_image_endpoints.py`)
- **POST /i2mr**
  ```python
  def test_image_to_medical_record():
      # Test single image conversion
      # Test multiple images
      # Test unsupported image format
      # Test empty image
      # Test with additional medical records
      # Test different languages
  ```

- **POST /iqa**
  ```python
  def test_image_qa():
      # Test image-based Q&A
      # Test keyword extraction
      # Test multiple prompts
      # Test error handling
  ```

#### Chat Endpoints (`test_chat_endpoints.py`)
- **POST /query**
  ```python
  def test_chat_query():
      # Test doctor role queries
      # Test patient role queries
      # Test session management
      # Test chat history
      # Test different languages
  ```

- **POST /t2mr**
  ```python
  def test_text_to_medical_record():
      # Test direct text conversion
      # Test with medical records
      # Test different languages
      # Test JSON/text format options
  ```

### 3. End-to-End Tests (`test_full_workflow.py`)
```python
def test_complete_medical_workflow():
    # Test full patient consultation flow:
    # 1. Voice recording to medical record
    # 2. Image upload of test results
    # 3. Chat interaction for clarification
    # 4. Final medical record generation
```

## Test Environment Setup

### Local Development
```sh
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### CI/CD Pipeline
- Tests should run on every pull request
- Coverage threshold: minimum 80%
- All tests must pass before merge

### Understanding conftest.py

The `conftest.py` file in the project root serves several critical purposes:

1. **Shared Fixtures**: 
   - Provides common test fixtures available to all test files
   - Current shared fixtures include:
     ```python
     @pytest.fixture
     def test_data_dir()  # Provides path to test data
     def sample_audio_file()  # Provides test audio data
     def sample_image_file()  # Provides test image data
     def sample_medical_record()  # Provides sample medical record text
     ```

2. **Global Test Configuration**:
   - Contains `setup_test_env` fixture with `autouse=True` for automatic environment setup
   - Sets up test environment variables for LLM services:
     ```python
     @pytest.fixture(autouse=True)
     def setup_test_env(monkeypatch):
         env_vars = {
             "LLM_API_URL": "http://localhost:11434/v1",
             "MODEL_NAME": "test-model",
             "FALLBACK_LLM_API_URL": "http://localhost:11435/v1",
             "FALLBACK_MODEL_NAME": "fallback-model"
         }
     ```

3. **Auto-Discovery**:
   - pytest automatically finds and loads `conftest.py`
   - Fixtures are available to all test files without explicit imports
   - Helps maintain DRY (Don't Repeat Yourself) principles in tests

4. **Test Organization**:
   - Centralizes common test data and configurations
   - Ensures consistent test environment setup
   - Can be hierarchical with multiple conftest.py files in different directories

## Mocking Strategy

### External Services
- Mock ASR service for voice transcription
- Mock OCR service for image processing
- Mock LLM service for text generation
```python
@pytest.fixture
def mock_llm_service(mocker):
    return mocker.patch('app.services.llm.LLMService')
```

### Test Data
- Sample audio files in different formats
- Sample images with medical information
- Sample medical records
- Expected transcription results
- Expected LLM responses

## Error Scenarios to Test
1. Network failures
2. Service timeouts
3. Invalid input formats
4. Unsupported languages
5. Empty or corrupted files
6. Rate limiting
7. Service unavailability (primary and fallback)

## Performance Testing
- Response time under normal load
- Concurrent request handling
- File size limits
- Memory usage monitoring
- Service recovery after failures

## Security Testing
- File type validation
- Size limit enforcement
- Error message safety
- API rate limiting
- Input sanitization
- Authentication (if added later)

## Monitoring and Logging
- Test log output format
- Test error reporting
- Test performance metrics
- Test health check endpoints
