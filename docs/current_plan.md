# Backend Restructuring and Multi-lingual Support Plan

## 1. Code Structure Reorganization
1. **Create Modular Package Structure**
   - Create a new `app` package with the following structure:
     ```
     app/
     ├── __init__.py
     ├── api/
     │   ├── __init__.py
     │   ├── routes/
     │   │   ├── __init__.py
     │   │   ├── medical_records.py
     │   │   ├── voice.py
     │   │   ├── image.py
     │   │   └── chat.py
     │   └── models/
     │       ├── __init__.py
     │       ├── request_models.py
     │       └── response_models.py
     ├── core/
     │   ├── __init__.py
     │   ├── config.py
     │   ├── i18n.py
     │   └── exceptions.py
     ├── services/
     │   ├── __init__.py
     │   ├── asr.py
     │   ├── ocr.py
     │   ├── llm.py
     │   └── medical_record.py
     └── utils/
         ├── __init__.py
         ├── file_handlers.py
         └── validators.py
     ```

2. **Separate Core Functionality**
   - Move ASR (Automatic Speech Recognition) logic to `services/asr.py`
   - Move OCR (Optical Character Recognition) logic to `services/ocr.py`
   - Move LLM (Language Model) interactions to `services/llm.py`
   - Move medical record processing to `services/medical_record.py`

3. **API Route Organization**
   - Split endpoints into logical groups in `routes/` directory
   - Implement proper request/response models in `models/` directory
   - Add input validation and error handling middleware

## 2. Multi-lingual Support Implementation
1. **Language Configuration**
   - Create language configuration in `core/i18n.py`
   - Support the same languages as frontend: en, zh, es, fr, th
   - Implement language detection and fallback mechanisms

2. **Translation System**
   - Create translation files for each supported language
   - Implement translation service for:
     - Error messages
     - System prompts
     - Medical record templates
     - Response formatting

3. **LLM Prompt Engineering**
   - Update LLM prompts to support multiple languages
   - Implement language-specific context and instructions
   - Add language detection and appropriate response formatting

4. **API Response Localization**
   - Add language parameter to all API endpoints
   - Implement response localization middleware
   - Ensure consistent language handling across all endpoints

## 3. Error Handling and Logging
1. **Structured Error Handling**
   - Create custom exception classes
   - Implement consistent error response format
   - Add proper error logging and monitoring

2. **Request Validation**
   - Add input validation for all endpoints
   - Implement proper error messages in multiple languages
   - Add request logging and monitoring

## 4. Testing and Documentation
1. **Testing Infrastructure**
   - Add unit tests for each module
   - Implement integration tests for API endpoints
   - Add language-specific test cases

2. **API Documentation**
   - Update OpenAPI/Swagger documentation
   - Add language support information
   - Document new endpoints and models

## 5. Migration Strategy
1. **Phase 1: Code Restructuring**
   - Create new package structure
   - Move existing code to new modules
   - Update imports and dependencies

2. **Phase 2: Multi-lingual Support**
   - Implement language configuration
   - Add translation system
   - Update LLM prompts

3. **Phase 3: Testing and Deployment**
   - Add tests for new functionality
   - Update documentation
   - Deploy changes incrementally

## 6. Future Considerations
1. **Performance Optimization**
   - Implement caching for translations
   - Optimize LLM prompts for each language
   - Add performance monitoring

2. **Additional Languages**
   - Create process for adding new languages
   - Implement language-specific optimizations
   - Add language-specific medical terminology

3. **Integration with Frontend**
   - Ensure consistent language handling
   - Implement proper error handling
   - Add proper logging and monitoring

# Plan to Ditch next-pwa and Restore Manual Service Worker (DONE)

**Update (2025-05-26):**
- Manual service worker is restored and working.
- Fixed a syntax error in the fetch event handler (duplicate catch block removed, error handling simplified).
- Offline fallback for navigation requests is now working: uncached pages show offline.html, not a 404.
- All PWA-related tests now pass (see testplans.md).
- Robust error handling in the service worker fetch event is essential to avoid registration failures.

## Plans to Do
1.  **Remove next-pwa from your project:** (Done)
    *   Uninstall the package.
    *   Remove next-pwa config from next.config.js.

2.  **Restore/Create your custom service worker:** (Done)
    *   Place your service worker file (e.g., service-worker.js) in medai/public/ (not src/app/).
    *   If you have a previous working version, restore it. Otherwise, I can help you write a robust one for offline support.

3.  **Manual registration in your app:** (Done)
    *   Add a registration script (e.g., ServiceWorkerRegister.tsx or inline in your root layout/page).
    *   Ensure registration only happens in production and in the browser.

4.  **Update manifest and icons:** (Done)
    *   No changes needed if already correct.

5.  **Test and debug:** (Done)
    *   Build and run your app (`next build` + `next start`).
    *   Use DevTools to verify service worker registration and offline support.

---

# Plan: Turning Next.js PWA (MedAI) into an Android App

## 1. PWA Setup
- Create and enhance `manifest.json` with multiple icon sizes, categories, and language support.
- Place `manifest.json` and icons in `medai/src/app/` and `medai/public/icons/` respectively.

## 2. Service Worker
- Initially write a custom service worker for offline support.
- Switch to using `next-pwa` for automatic service worker generation and registration.
- Remove all manual service worker registration code (including custom `ServiceWorkerRegister.tsx`) to avoid conflicts with `next-pwa`.
- Ensure `next.config.js` is configured to use `next-pwa`.

## 3. Middleware and Routing
- Implement i18n middleware to redirect `/` to `/en` and handle locale-based routing.
- Refine middleware matcher to exclude static assets and internal Next.js files (e.g., `/_next/*`, `/icons/*`, `/manifest.json`) to prevent 404 errors and service worker precaching issues.

## 4. Testing and Debugging
- Test PWA in both development and production modes.
- Note: PWA features (service worker, offline, etc.) are only enabled in production (`npm run build` + `npm start`).
- Debug service worker installation and asset precaching using browser DevTools.

## 5. Cross-Platform Testing
- Test on both Ubuntu and macOS.
- Reproduce issues in both minimal and full-featured Next.js projects, and with different Next.js versions (14.x, 15.x).
- Verify that issues are not specific to project, OS, or configuration.

## 6. Android App Conversion
- Once PWA is working, use tools like TWA (Trusted Web Activity) or PWABuilder to wrap the PWA as an Android app.
- Ensure multi-language support and offline functionality are preserved.
- Test installation and behavior on Android devices/emulators.

## 7. Ongoing
- Monitor for Next.js and `next-pwa` updates or regressions.
- Consider raising issues with the Next.js team if core problems persist.

## Next Steps & Recommendations (Manual Service Worker)

1.  **Populate `urlsToCache`**: In `medai/public/service-worker.js`, review and add critical pages/assets for the initial offline experience (e.g., `/`, `/offline.html`, `/manifest.json`, key icons). Most Next.js static assets (`_next/static/...`) will be cached on first use by the current strategy.
2.  **Create `offline.html`**: Develop a simple `medai/public/offline.html` page to be served when a navigation request fails and the page isn't cached.
3.  **Implement Background Sync Logic**: If needed for features like offline form submission, implement `replayFailedRequests()` in the service worker, likely using IndexedDB.
4.  **Implement Periodic Sync Logic**: If regular background content updates are required, implement `updateContent()` in the service worker and handle permissions.
5.  **Test Thoroughly**: Build for production (`npm run build` + `npm run start`). Use browser DevTools to verify service worker activation, cache contents, and offline behavior across different browsers/devices.
6.  **Refine Caching Strategies**: Adjust service worker caching strategies based on specific application needs for different resource types (images, API calls, etc.).

## Plan: Implement Background Sync and Periodic Sync

Per user data storage feature has to be implemented before --

3. **Implement Background Sync Logic**
   - Use IndexedDB to store failed POST/PUT requests when offline.
   - Implement `replayFailedRequests()` in the service worker to retry these requests when connectivity is restored (using the 'sync' event).
   - Add client-side logic to queue failed requests and register for background sync.

4. **Implement Periodic Sync Logic**
   - Implement `updateContent()` in the service worker to fetch and cache fresh data/content periodically (using the 'periodicsync' event).
   - Request and handle permissions for periodic background sync in the client.
   - Add logic to update cached content and notify the user if new content is available.

