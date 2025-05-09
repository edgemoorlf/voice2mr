import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    // Wait for the dev server to be ready
    await page.waitForTimeout(2000);
  });

  test('should load the page and show main components', async ({ page }) => {
    await page.goto('http://localhost:3000/en');
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot to debug
    await page.screenshot({ path: 'test-results/home-page.png' });
    
    // Log the page content for debugging
    const content = await page.content();
    console.log('Page content:', content);
    
    // Check if main components are visible
    await expect(page.locator('h2')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Upload Medical Records' })).toBeVisible();
    
    // Check if file upload zone exists
    await expect(page.locator('text=Drag & drop files here')).toBeVisible();
  });

  test('should support language switching', async ({ page }) => {
    await page.goto('http://localhost:3000/zh');
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot to debug
    await page.screenshot({ path: 'test-results/language-switch.png' });
    
    // Log the page content for debugging
    const content = await page.content();
    console.log('Page content:', content);
    
    // The page should load with Chinese content
    await expect(page).toHaveURL('http://localhost:3000/zh');
    await expect(page.locator('h2')).toBeVisible();
  });

  test('should handle file upload interaction', async ({ page }) => {
    await page.goto('http://localhost:3000/en');
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot to debug
    await page.screenshot({ path: 'test-results/file-upload.png' });
    
    // Log the page content for debugging
    const content = await page.content();
    console.log('Page content:', content);
    
    // Check file upload functionality
    const fileInput = page.locator('input[type="file"]');
    await expect(fileInput).toBeVisible();
    
    // Check if the upload button is initially not visible (since no files are selected)
    const processButton = page.getByText('Process Files', { exact: true });
    await expect(processButton).toBeHidden();
  });
});
