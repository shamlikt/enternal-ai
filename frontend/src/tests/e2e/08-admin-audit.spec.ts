/**
 * E2E tests: Admin Audit Log page
 *
 * Tests the audit log AG Grid page.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers";

test.describe("Admin Audit Log", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/admin/audit");
    await expect(page).toHaveURL(/\/admin\/audit/);
  });

  test("audit log page loads with heading", async ({ page }) => {
    await expect(page.getByRole("heading", { name: /audit log/i })).toBeVisible();
  });

  test("AG Grid renders with expected column headers", async ({ page }) => {
    await expect(page.locator(".ag-root-wrapper")).toBeVisible({ timeout: 10000 });
    // Check for expected column headers
    await expect(page.locator(".ag-header-cell").filter({ hasText: "Time" }).first()).toBeVisible();
    await expect(page.locator(".ag-header-cell").filter({ hasText: "User" }).first()).toBeVisible();
    await expect(
      page.locator(".ag-header-cell").filter({ hasText: "Action" }).first()
    ).toBeVisible();
  });

  test("grid shows data or empty state", async ({ page }) => {
    await expect(page.locator(".ag-root-wrapper")).toBeVisible({ timeout: 10000 });
    // Either rows exist or "No Rows To Show" overlay is visible
    const hasRows = await page.locator(".ag-row").first().isVisible().catch(() => false);
    const hasOverlay = await page
      .locator(".ag-overlay-no-rows-center")
      .isVisible()
      .catch(() => false);
    expect(hasRows || hasOverlay).toBeTruthy();
  });
});
