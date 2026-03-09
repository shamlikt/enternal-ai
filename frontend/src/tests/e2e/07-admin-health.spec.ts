/**
 * E2E tests: Admin System Health page
 *
 * Tests the system health monitoring dashboard.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers";

test.describe("Admin Health", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/admin/health");
    await expect(page).toHaveURL(/\/admin\/health/);
  });

  test("system health page loads with heading", async ({ page }) => {
    await expect(page.getByRole("heading", { name: /system health/i })).toBeVisible();
  });

  test("shows Overall Status card with status badge", async ({ page }) => {
    await expect(page.getByText("Overall Status")).toBeVisible({ timeout: 10000 });
    // Should show a healthy/degraded badge
    await expect(
      page.locator("text=healthy").or(page.locator("text=degraded")).first()
    ).toBeVisible({ timeout: 5000 });
  });

  test("refresh button is present and clickable", async ({ page }) => {
    const refreshBtn = page.getByRole("button", { name: /refresh/i });
    await expect(refreshBtn).toBeVisible();
    await refreshBtn.click();
    // Should not error — just confirm the button works
    await expect(page.getByRole("heading", { name: /system health/i })).toBeVisible();
  });
});
