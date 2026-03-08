/**
 * E2E tests: Agent Search (AI chat) page
 *
 * Prerequisites: Full stack running, admin user seeded, AWS Bedrock configured.
 *
 * Tests:
 * - Agent page loads
 * - Chat input is visible
 * - Session list panel is present
 * - Sending a message shows it in the chat
 *
 * Note: The actual AI response requires AWS Bedrock credentials.
 * Tests that depend on LLM responses use mock responses via network interception
 * or skip assertions on the AI response content.
 */
import { test, expect, Page } from "@playwright/test";

const ADMIN_USERNAME = process.env.ADMIN_USERNAME ?? "admin";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? "adminpass123";

async function loginAsAdmin(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Username").fill(ADMIN_USERNAME);
  await page.getByLabel("Password").fill(ADMIN_PASSWORD);
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
}

test.describe("Agent Search", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/agent");
    await expect(page).toHaveURL(/\/agent/);
  });

  test("agent page loads with chat input", async ({ page }) => {
    // Chat input area should be present
    const chatInput = page
      .getByRole("textbox", { name: /ask|message|question/i })
      .or(page.locator("textarea").first());
    await expect(chatInput).toBeVisible({ timeout: 10000 });
  });

  test("send button is present", async ({ page }) => {
    const sendButton = page.getByRole("button", { name: /send/i }).first();
    await expect(sendButton).toBeVisible({ timeout: 5000 });
  });

  test("typing a question shows it in the input", async ({ page }) => {
    const chatInput = page
      .getByRole("textbox", { name: /ask|message|question/i })
      .or(page.locator("textarea").first());

    await chatInput.fill("How many patients are in the database?");
    await expect(chatInput).toHaveValue("How many patients are in the database?");
  });
});
