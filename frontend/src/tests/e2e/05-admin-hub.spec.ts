/**
 * E2E tests: Admin hub page
 *
 * Tests the admin landing page with its 4 section cards.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers";

test.describe("Admin Hub", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/admin");
    await expect(page).toHaveURL(/\/admin/);
  });

  test("admin page loads with 4 section cards", async ({ page }) => {
    await expect(page.getByRole("heading", { name: /admin/i })).toBeVisible();
    await expect(page.getByText("User Management")).toBeVisible();
    await expect(page.getByText("System Health")).toBeVisible();
    await expect(page.getByText("Audit Log")).toBeVisible();
    await expect(page.getByText("Application Logs")).toBeVisible();
  });

  test("navigate to User Management via card click", async ({ page }) => {
    await page.getByText("User Management").click();
    await expect(page).toHaveURL(/\/admin\/users/, { timeout: 5000 });
  });

  test("navigate to System Health via card click", async ({ page }) => {
    await page.getByText("System Health").click();
    await expect(page).toHaveURL(/\/admin\/health/, { timeout: 5000 });
  });

  test("navigate to Audit Log via card click", async ({ page }) => {
    await page.getByText("Audit Log").click();
    await expect(page).toHaveURL(/\/admin\/audit/, { timeout: 5000 });
  });
});
