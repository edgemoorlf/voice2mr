## [Date: 2025-05-26] Complete Project Separation
- Moved all Python-related configuration files to `cdss/` directory:
  - pyproject.toml
  - requirements.txt
  - pytest.ini
  - hotwords.txt
- Clear separation between Python (CDSS) and TypeScript (MedAI) projects
- Updated README.md with clearer project structure and setup instructions
- Each project now has its own complete configuration
- Improved project organization and maintainability

## [Date: 2025-05-26] Major Project Reorganization
- Split project into two main components:
  1. CDSS (Backend): Moved to `cdss/` directory
  2. MedAI (Frontend): Located in `medai/` directory
- Reorganized backend code under `cdss/src/app`
- Updated pyproject.toml to reflect new directory structure
- Updated README.md with new project organization and setup instructions
- Maintained separation of concerns between frontend and backend
- All tests passing with new structure

## [Date: 2025-05-26] Project Structure Improvement - Src Layout
- Migrated to modern src layout (`src/app/` instead of `app/`)
- Removed manual Python path manipulation from root conftest.py
- Updated pyproject.toml to use src directory
- Added proper package build configuration with hatch
- All tests passing with cleaner project structure

## [Date: 2025-05-26] Test Infrastructure Documentation Update
- Added comprehensive documentation about `conftest.py` and its role in the test infrastructure
- Documented shared fixtures for test data and environment setup
- Explained the auto-discovery and test organization benefits of `conftest.py`
- Updated testplans.md with detailed conftest.py explanation and examples

## [Date: 2025-05-26] Manual Service Worker Fixes and PWA Test Pass
- Fixed a critical syntax error in medai/public/service-worker.js fetch event handler (duplicate catch block removed, error handling simplified).
- Service worker now registers and activates correctly in production.
- Offline fallback for navigation requests restored: uncached pages now show offline.html instead of Next.js 404.
- All PWA-related Playwright tests now pass: registration, asset caching, offline fallback, manifest, and no console errors.
- See testplans.md for updated test plan and checklist.

## [Date: 2025-05-24] Ditch next-pwa service worker registration

- [15:43] I am not convinced next-pwa works well for automatic service-worker registration on which I have paid a price of two days. That's enough. I would like to go back to manual service worker registration that used to work. Please ditch next-pwa service-worker registration and switch back to manual service worker and its registration.
- Uninstalled `next-pwa` package.
- Removed `next-pwa` configuration from `medai/next.config.js`.
- Created `medai/public/service-worker.js` with an advanced service worker implementation (network falling back to cache for navigation, cache first for assets, background sync, periodic updates).
- Populated `urlsToCache` in `medai/public/service-worker.js` with essential offline assets.
- Created `medai/public/offline.html` as the offline fallback page.
- Created `medai/src/app/components/ServiceWorkerRegister.tsx` for manual service worker registration.
- Imported and added `ServiceWorkerRegister` component to `medai/src/app/layout.tsx`.

## [Date: 2025-05-23] PWA and Android App Conversion Progress

- Enhanced `manifest.json` with multiple icon sizes, categories, and language support.
- Moved PWA assets and icons to `medai/src/app/` and `medai/public/icons/`.
- Switched from a custom service worker to `next-pwa` for automatic service worker generation and registration.
- Removed manual service worker registration code and deleted `ServiceWorkerRegister.tsx`.
- Configured `next.config.js` to use `next-pwa`.
- Refined i18n middleware matcher to exclude static assets and internal Next.js files, resolving 404 errors and service worker precaching issues.
- Tested PWA in both development and production modes on Ubuntu and macOS.
- Identified and documented an outstanding issue: `next start` does not serve `/_next/app-build-manifest.json`, causing service worker installation failures.
- Added detailed plans and issue tracking to `current_plan.md` and `issues.md`.

