/**
 * E2E tests: Quarantine page
 *
 * Tests the quarantine records viewer with stats and AG Grid.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers";

test.describe("Quarantine", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/quarantine");
    await expect(page).toHaveURL(/\/quarantine/);
  });

  test("quarantine page loads with heading", async ({ page }) => {
    await expect(page.getByRole("heading", { name: /quarantine/i })).toBeVisible();
  });

  test("stats cards render with Total Quarantined", async ({ page }) => {
    await expect(page.getByText("Total Quarantined")).toBeVisible({ timeout: 10000 });
  });

  test("AG Grid renders with columns", async ({ page }) => {
    await expect(page.locator(".ag-root-wrapper")).toBeVisible({ timeout: 10000 });
    await expect(
      page.locator(".ag-header-cell").filter({ hasText: "Resource Type" }).first()
    ).toBeVisible();
    await expect(
      page.locator(".ag-header-cell").filter({ hasText: "Error" }).first()
    ).toBeVisible();
  });
});
