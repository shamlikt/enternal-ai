/**
 * E2E tests: Admin Application Logs page
 *
 * Tests the structured logs viewer with level filters.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers";

test.describe("Admin Application Logs", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/admin/logs");
    await expect(page).toHaveURL(/\/admin\/logs/);
  });

  test("application logs page loads with heading", async ({ page }) => {
    await expect(page.getByRole("heading", { name: /application logs/i })).toBeVisible();
  });

  test("filter buttons are visible", async ({ page }) => {
    await expect(page.getByRole("button", { name: /all/i }).first()).toBeVisible();
    await expect(page.getByText("ERROR")).toBeVisible();
    await expect(page.getByText("WARNING")).toBeVisible();
  });

  test("page handles empty state gracefully", async ({ page }) => {
    // Wait for loading to complete
    await page.waitForTimeout(2000);
    // Should show either log entries or "No log entries" message
    const hasEntries = await page.locator(".font-mono .border-b").first().isVisible().catch(() => false);
    const hasEmpty = await page.getByText("No log entries").isVisible().catch(() => false);
    expect(hasEntries || hasEmpty).toBeTruthy();
  });
});
