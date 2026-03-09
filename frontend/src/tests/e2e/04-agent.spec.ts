/**
 * E2E tests: Agent Search (AI chat) page
 *
 * Prerequisites: Full stack running, admin user seeded.
 * Note: Actual AI responses require AWS Bedrock credentials.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers";

test.describe("Agent Search", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/agent");
    await expect(page).toHaveURL(/\/agent/);
  });

  test("agent page loads with chat input", async ({ page }) => {
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
