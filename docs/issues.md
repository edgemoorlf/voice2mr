# Outstanding Issues

## 1. Service Worker Registration and Internal Asset Serving (Resolved)
- Manual service worker restored and now registers/activates correctly after fixing a syntax error in the fetch event handler.
- Offline fallback for navigation requests now works: uncached pages show offline.html, not a 404.
- Previous issue with registration failure due to script evaluation error is resolved.
- Note: Careful error handling in the fetch event is critical to avoid breaking SW registration.

### Previously:

- After switching to `next-pwa` and removing manual service worker registration, the service worker is generated and registered automatically.
- However, requests to internal Next.js build artifacts (e.g., `/_next/app-build-manifest.json`) return the app's 404 page instead of the expected JSON.
- This causes service worker installation to fail (`bad-precaching-response`) and leaves the service worker stuck in the "installing" state, breaking offline support.
- The file exists on disk after build, but is not served by `next start`.
- The issue is reproducible in minimal Next.js 15.1.8 projects on both Ubuntu and macOS, and with both Next.js 14.x and 15.x.
- The problem is not specific to the project, OS, or configuration, but appears to be a broader issue with how `next start` serves internal build artifacts.
- No direct match for this issue was found in Next.js documentation or GitHub issues. Some platforms (e.g., Netlify) have had issues with serving `_next` assets, but this occurs locally with the standard Next.js server.

## 2. Middleware Interference (Resolved)
- The i18n middleware matcher was initially too broad, intercepting requests for static assets and internal files, causing 404 errors and interfering with service worker precaching.
- This was resolved by refining the matcher to exclude static and internal files.

## 3. Next Steps
- Further investigation into why `next start` fails to serve internal build artifacts.
- Consider testing with older Next.js or Node.js versions to isolate the problem.
- Consider raising an issue with the Next.js team or checking for very recent regressions in Next.js 15.x.
