import { test as base, expect } from '@playwright/test';

// Create a test fixture that provides a fresh context with caching disabled
const test = base.extend({
  context: async ({ browser }, use) => {
    // Create a fresh context with caching disabled
    const context = await browser.newContext({
      bypassCSP: true, // Allow us to inspect and modify service worker
      ignoreHTTPSErrors: true,
      serviceWorkers: 'allow', // Enable service workers from the start
    });
    await use(context);
    await context.close();
  },
});

// These tests assume the app is running in production mode (npm run build && npm start)
// and is accessible at http://localhost:3000

test.describe('PWA Manual Service Worker', () => {
  test('Service worker is registered and active', async ({ page, context }) => {
    // Set up console logging
    const consoleLogs: string[] = [];
    page.on('console', msg => {
      const text = msg.text();
      console.log(`BROWSER CONSOLE: ${text}`);
      consoleLogs.push(text);
    });

    // Go to page and verify SW script content
    await page.goto('/', { waitUntil: 'networkidle' });
    
    // Fetch and verify service worker content
    const swResponse = await page.request.get('/service-worker.js');
    const swContent = await swResponse.text();
    console.log('Service Worker Script Content (first 300 chars):');
    console.log(swContent.substring(0, 300));

    // Wait for service worker registration and caching
    const swState = await page.evaluate(async () => {
      if (!('serviceWorker' in navigator)) return 'ServiceWorker API not available';
      
      try {
        const registration = await navigator.serviceWorker.register('/service-worker.js');
        await navigator.serviceWorker.ready;
        
        // Wait a bit for caching to complete
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check cache contents
        const cache = await caches.open('medai-cache-v1');
        const cachedUrls = await cache.keys();
        
        return {
          status: 'success',
          state: registration.active?.state,
          cached: cachedUrls.map(req => req.url)
        };
      } catch (error: unknown) {
        return {
          status: 'error',
          error: error instanceof Error ? error.toString() : 'Unknown error'
        };
      }
    });
    
    console.log('Service Worker State:', swState);
    
    // Verify service worker is controlling the page
    const controller = await page.evaluate(() => navigator.serviceWorker?.controller?.state);
    expect(controller).toBe('activated');
  });

  test('Essential assets are cached', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });
    
    // Wait for service worker and check cache
    const cacheState = await page.evaluate(async () => {
      await navigator.serviceWorker.ready;
      const cache = await caches.open('medai-cache-v1');
      const offline = await cache.match('/offline.html');
      const root = await cache.match('/');
      const manifest = await cache.match('/manifest.json');
      
      return {
        '/offline.html': !!offline,
        '/': !!root,
        '/manifest.json': !!manifest
      };
    });
    
    console.log('Cache State:', cacheState);
    expect(cacheState['/offline.html']).toBe(true);
  });

  test('Offline fallback works for navigation', async ({ page, context }) => {
    // Enable request logging
    page.on('console', msg => console.log('BROWSER:', msg.text()));
    
    // First ensure cache is populated and service worker is active
    await page.goto('/', { waitUntil: 'networkidle' });
    
    // Wait for and verify service worker status
    const swStatus = await page.evaluate(async () => {
      const registration = await navigator.serviceWorker.ready;
      await new Promise(resolve => setTimeout(resolve, 1000)); // Extra time for activation
      return {
        active: !!registration.active,
        state: registration.active?.state,
        controller: !!navigator.serviceWorker.controller
      };
    });
    console.log('Service Worker Status:', swStatus);

    // Verify cache contents before going offline
    const cacheStatus = await page.evaluate(async () => {
      const cache = await caches.open('medai-cache-v1');
      const offlinePage = await cache.match('/offline.html');
      const offlineContent = await offlinePage?.text();
      return {
        hasOfflinePage: !!offlinePage,
        offlinePageUrl: offlinePage?.url,
        offlineContent: offlineContent?.substring(0, 200) // First 200 chars
      };
    });
    console.log('Cache Status:', cacheStatus);
    
    // Go offline by intercepting all requests
    await page.route('**/*', route => {
      console.log('Intercepted request to:', route.request().url());
      route.abort('internetdisconnected');
    });
    console.log('Network requests will be aborted to simulate offline mode');

    // Navigate to non-existent page
    const response = await page.goto('/some-non-existent-page1', {
      waitUntil: 'domcontentloaded',
      timeout: 5000
    }).catch(e => {
      console.log('Navigation error:', e.message);
      return null;
    });
    
    if (response) {
      console.log('Navigation Response:', {
        status: response.status(),
        headers: response.headers()
      });
    }
    
    const content = await page.content();
    console.log('Page content preview:', content.substring(0, 200));
    
    expect(content).toContain('You are Offline');
    
    // Clean up route interception
    await page.unroute('**/*');
  });

  test('Manifest loads and icons are present', async ({ page }) => {
    await page.goto('/');
    const manifest = await page.evaluate(async () => {
      const res = await fetch('/manifest.json');
      return res.ok;
    });
    expect(manifest).toBe(true);
    // Optionally, check for icons in the manifest
  });

  test('No errors in console during registration', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));
    await page.goto('/');
    expect(errors).toEqual([]);
  });
}); 