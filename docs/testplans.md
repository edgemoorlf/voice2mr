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
