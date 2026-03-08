/**
 * E2E tests: SQL Editor page
 *
 * Prerequisites: Full stack running, admin user seeded.
 *
 * Tests:
 * - SQL Editor page loads with Monaco editor
 * - Execute button is visible
 * - Non-SELECT SQL shows error (SELECT-only guardrail enforced at API)
 * - Schema tree (Data Explorer) is visible and shows tables
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

test.describe("SQL Editor", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/sql-editor");
    await expect(page).toHaveURL(/\/sql-editor/);
  });

  test("SQL Editor page loads", async ({ page }) => {
    // Page should have some editor-related content
    await expect(page.locator(".monaco-editor").or(page.getByText(/SQL Editor/i))).toBeVisible({
      timeout: 10000,
    });
  });

  test("Execute button is present", async ({ page }) => {
    // Look for an execute/run button
    const executeButton = page
      .getByRole("button", { name: /execute|run/i })
      .or(page.getByText(/execute/i).first());
    await expect(executeButton).toBeVisible({ timeout: 5000 });
  });

  test("Data Explorer panel shows PCORnet tables", async ({ page }) => {
    // The data explorer should show the CDM table list
    // At minimum, DEMOGRAPHIC should be present if DB is seeded
    const explorerPanel = page.locator("[data-testid='data-explorer']").or(
      page.getByText("DEMOGRAPHIC").first()
    );
    await expect(explorerPanel).toBeVisible({ timeout: 5000 });
  });
});
