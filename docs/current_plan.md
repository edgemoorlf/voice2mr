# Plan to Ditch next-pwa and Restore Manual Service Worker

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
