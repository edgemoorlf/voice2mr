import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test('English homepage should render correctly', async ({ page }) => {
    await page.goto('/en');

    // Wait for the page to be somewhat stable, e.g., for the main heading to appear
    await expect(page.locator('h2:has-text("Your AI Medical Assistant")')).toBeVisible({ timeout: 15000 });

    const chatComponent = page.locator('div.flex.flex-col.bg-white.rounded-lg.shadow[class*="min-h-[500px]"]');
    await expect(chatComponent).toBeVisible();
    await expect(chatComponent).toHaveScreenshot('en-chat-component.png');

    const uploadSection = page.locator('div.bg-white.shadow.rounded-lg:has(h3:has-text("Upload Medical Records"))');
    await expect(uploadSection).toBeVisible();
    await expect(uploadSection).toHaveScreenshot('en-upload-section.png');
  });

  test('Chinese homepage should render correctly', async ({ page }) => {
    await page.goto('/zh');

    // Wait for the page to be somewhat stable, e.g., for the main heading to appear
    await expect(page.locator('h2:has-text("您的AI医疗助手")')).toBeVisible({ timeout: 15000 });

    const chatComponent = page.locator('div.flex.flex-col.bg-white.rounded-lg.shadow[class*="min-h-[500px]"]');
    await expect(chatComponent).toBeVisible();
    await expect(chatComponent).toHaveScreenshot('zh-chat-component.png');

    // Expect the translated heading
    const uploadSection = page.locator('div.bg-white.shadow.rounded-lg:has(h3:has-text("上传病历"))');
    await expect(uploadSection).toBeVisible();
    await expect(uploadSection).toHaveScreenshot('zh-upload-section.png');
  });
}); 