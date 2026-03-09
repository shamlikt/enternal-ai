/**
 * E2E tests: SQL Editor page
 *
 * Prerequisites: Full stack running, admin user seeded.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers";

test.describe("SQL Editor", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/sql-editor");
    await expect(page).toHaveURL(/\/sql-editor/);
  });

  test("SQL Editor page loads", async ({ page }) => {
    await expect(page.locator(".monaco-editor").or(page.getByText(/SQL Editor/i))).toBeVisible({
      timeout: 10000,
    });
  });

  test("Execute button is present", async ({ page }) => {
    const executeButton = page
      .getByRole("button", { name: /execute|run/i })
      .or(page.getByText(/execute/i).first());
    await expect(executeButton).toBeVisible({ timeout: 5000 });
  });

  test("Data Explorer panel shows PCORnet tables", async ({ page }) => {
    const explorerPanel = page.locator("[data-testid='data-explorer']").or(
      page.getByText("DEMOGRAPHIC").first()
    );
    await expect(explorerPanel).toBeVisible({ timeout: 5000 });
  });
});
