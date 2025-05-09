import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    // Wait for the dev server to be ready
    await page.waitForTimeout(2000);
  });

  test('should load the page and show main components', async ({ page }) => {
    await page.goto('http://localhost:3000/en');
    await page.waitForLoadState('networkidle');
    
    // Check if main components are visible
    await expect(page.locator('h2')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Upload Medical Records' })).toBeVisible();
    
    // Check if file upload zone exists
    await expect(page.locator('text=Drag & drop files here')).toBeVisible();
  });

  test('should support language switching', async ({ page }) => {
    await page.goto('http://localhost:3000/zh');
    await page.waitForLoadState('networkidle');
    
    // The page should load with Chinese content
    await expect(page).toHaveURL('http://localhost:3000/zh');
    await expect(page.locator('h2')).toBeVisible();
  });

  test('should handle file upload interaction', async ({ page }) => {
    await page.goto('http://localhost:3000/en');
    await page.waitForLoadState('networkidle');
    
    // Check file upload functionality
    const fileInput = page.locator('input[type="file"]');
    await expect(fileInput).toBeVisible();
    
    // Check if the upload button is initially not visible (since no files are selected)
    const processButton = page.getByText('Process Files', { exact: true });
    await expect(processButton).toBeHidden();
  });

  test('should have correct styles applied', async ({ page }) => {
    await page.goto('http://localhost:3000/en');
    await page.waitForLoadState('networkidle');
    
    // Check background color
    const body = page.locator('body');
    await expect(body).toHaveClass(/bg-gray-50/);
    
    // Check container max width
    const container = page.locator('.max-w-7xl');
    await expect(container).toBeVisible();
    
    // Check heading styles
    const heading = page.locator('h2').first();
    await expect(heading).toHaveClass(/text-3xl.*font-bold.*text-gray-900/);
    
    // Check chat container styles
    const chatContainer = page.locator('.bg-white.shadow-lg.rounded-lg');
    await expect(chatContainer).toBeVisible();
    await expect(chatContainer).toHaveClass(/p-6/);
    
    // Check upload zone styles
    const uploadZone = page.locator('.border-2.border-dashed');
    await expect(uploadZone).toHaveClass(/border-gray-300.*rounded-lg.*hover:border-blue-500/);
    
    // Check icon styles
    const icon = page.locator('.h-12.w-12.text-gray-400');
    await expect(icon).toBeVisible();
  });
}); 