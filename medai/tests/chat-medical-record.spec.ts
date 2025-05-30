import { test, expect } from '@playwright/test';

// Test for medical record formatting in the chat interface
test.describe('Chat Medical Record Formatting', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the chat page (assuming English locale)
    await page.goto('/en', { waitUntil: 'networkidle' });
  });

  test('Medical record should be properly formatted with sections and styling', async ({ page }) => {
    // Sample medical record content (based on user's example)
    const medicalRecordContent = `好的，根据您提供的资料，我将整理成病历记录：
* *病历记录** * *主诉：** 患者自述无明显不适，偶有咳嗽，无痰。 * *现病史：** 患者于2023年10月18日在青岛某医院确诊为肝癌，基础疾病为乙型肝炎，病程35年，近年来控制不佳，导致肝癌进展。已在302医院行两次肝动脉介入栓塞术，治疗后无其他药物治疗，仅进行基本的抗病毒药物治疗。患者仍需长期服用抗病毒药物。 * *既往史：** 乙型肝炎35年。 * *过敏史：** 无。 * *家族史：** 无。 * *体格检查：** 身材正常，气色尚可，偶尔咳嗽，无痰，无明显喘息。饮食、大小便正常，睡眠良好。喜食凉食，舌苔白，舌质正常，无青筋显现。手指末端触感温度稍偏凉。脉象正常，稍感倦怠。 * *辅助检查：** - CT 胸部（2023-06-08）：食管胸上段管壁不均匀增厚，符合食管癌表现，纵隔小淋巴结显示，双肺下叶少许间质性病变可能。 - 病理 检查（2023-06-19）：提示双肺下叶胸膜下条索影及磨玻璃密度小片影。 - PET/CT（2023-06-08）：食管胸上段占位，符合食管癌。 - 心电图、超声心脏及甲状腺等无明显异常。 * *诊断：** 1. 肝癌（继发于乙型肝炎） 2. 食管上段癌 3. 乙型肝炎 * *处置意见：** 建议继续接受抗病毒治疗并定期复查肝功能。鉴于食管癌表现，请血液科会诊确定进一步治疗方案。 * *注意事项：** 禁止烟酒，避免辛辣刺激饮食。保持良好作息，避免过度劳累并定期复查肝功能。 * *中医辩证：** 肝郁脾虚，湿热内蕴。 * *中药处方：** 1. 柴胡舒肝散：柴胡、白芍、枳壳、甘草、茯苓各10克，煎水服用，每日一剂。 2. 保和丸：每次5克，每日三次，饭后温水服用。 注：以上中药处方需在专业中医师处确认后使用。
患者需密切注意症状变化，并根据病情调整中药处方。`;

    // Wait for chat component to load
    await page.waitForSelector('[data-testid="chat-container"]', { timeout: 10000 });

    // Simulate sending a medical record message
    // First, we need to input some text to trigger the medical record response
    const chatInput = page.locator('input[placeholder*="Type"]').first();
    await chatInput.fill('请整理一下病历记录');
    
    // Submit the message
    await page.locator('button[type="submit"]').click();

    // Wait for the response
    await page.waitForTimeout(2000);

    // Mock the response to include our medical record content
    await page.evaluate((content) => {
      // Add a test message using React's component rendering
      const event = new CustomEvent('addTestMessage', {
        detail: {
          role: 'assistant',
          content: content,
          id: 'test-medical-record',
          timestamp: Date.now()
        }
      });
      window.dispatchEvent(event);
    }, medicalRecordContent);

    // Wait a bit for the component to render
    await page.waitForTimeout(1000);

    // Now test if the medical record formatting is applied
    const medicalRecordContainer = page.locator('[data-testid="medical-record-container"]');
    await expect(medicalRecordContainer).toBeVisible();

    // Test various formatting elements
    await test.step('Check medical record header', async () => {
      const header = page.locator('h3:has-text("医疗记录 / Medical Record")');
      await expect(header).toBeVisible();
      await expect(header).toHaveClass(/font-bold.*text-blue-800/);
    });

    await test.step('Check section headers', async () => {
      const sectionHeaders = page.locator('h4.font-semibold.text-blue-800');
      await expect(sectionHeaders.first()).toBeVisible();
    });

    await test.step('Check bullet points', async () => {
      const bulletPoints = page.locator('span.text-blue-600:has-text("•")');
      await expect(bulletPoints.first()).toBeVisible();
    });

    await test.step('Check content structure', async () => {
      // Check if sections are properly separated
      const sections = page.locator('.mb-4');
      const sectionCount = await sections.count();
      expect(sectionCount).toBeGreaterThan(1);
    });

    // Take a screenshot for visual verification
    await page.screenshot({ 
      path: 'test-results/medical-record-formatting.png',
      fullPage: true 
    });
  });

  test('Regular chat messages should not be formatted as medical records', async ({ page }) => {
    // Wait for chat component to load
    await page.waitForSelector('[data-testid="chat-container"]', { timeout: 10000 });

    const regularMessage = "Hello, how are you today?";
    
    // Send a regular message
    const chatInput = page.locator('input[placeholder*="Type"]').first();
    await chatInput.fill(regularMessage);
    await page.locator('button[type="submit"]').click();

    // Wait for response and verify it's not formatted as medical record
    await page.waitForTimeout(1000);
    
    // Check that medical record specific styling is not applied
    const medicalRecordContainer = page.locator('.bg-blue-50.border.border-blue-200');
    await expect(medicalRecordContainer).not.toBeVisible();
    
    const medicalRecordHeader = page.locator('h3:has-text("医疗记录 / Medical Record")');
    await expect(medicalRecordHeader).not.toBeVisible();
  });
}); 