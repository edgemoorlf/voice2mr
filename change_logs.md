## [Date: YYYY-MM-DD] PWA and Android App Conversion Progress

- Enhanced `manifest.json` with multiple icon sizes, categories, and language support.
- Moved PWA assets and icons to `medai/src/app/` and `medai/public/icons/`.
- Switched from a custom service worker to `next-pwa` for automatic service worker generation and registration.
- Removed manual service worker registration code and deleted `ServiceWorkerRegister.tsx`.
- Configured `next.config.js` to use `next-pwa`.
- Refined i18n middleware matcher to exclude static assets and internal Next.js files, resolving 404 errors and service worker precaching issues.
- Tested PWA in both development and production modes on Ubuntu and macOS.
- Identified and documented an outstanding issue: `next start` does not serve `/_next/app-build-manifest.json`, causing service worker installation failures.
- Added detailed plans and issue tracking to `current_plan.md` and `issues.md`.
