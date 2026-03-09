/**
 * E2E tests: Admin Users page
 *
 * Tests user management with AG Grid and create dialog.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers";

test.describe("Admin Users", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/admin/users");
    await expect(page).toHaveURL(/\/admin\/users/);
  });

  test("users page loads and shows admin user in grid", async ({ page }) => {
    await expect(page.getByRole("heading", { name: /users/i })).toBeVisible();
    // AG Grid should render and show the admin user
    await expect(page.locator(".ag-root-wrapper")).toBeVisible({ timeout: 10000 });
    await expect(page.locator(".ag-cell").filter({ hasText: "admin" }).first()).toBeVisible({
      timeout: 5000,
    });
  });

  test("Create User button opens dialog", async ({ page }) => {
    await page.getByRole("button", { name: /create user/i }).click();
    await expect(page.getByRole("heading", { name: /create user/i })).toBeVisible();
    await expect(page.getByLabel("Username")).toBeVisible();
    await expect(page.getByLabel("Email")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
  });

  test("create analyst user via dialog", async ({ page }) => {
    await page.getByRole("button", { name: /create user/i }).click();

    const uniqueSuffix = Date.now().toString().slice(-6);
    await page.getByLabel("Username").fill(`analyst_${uniqueSuffix}`);
    await page.getByLabel("Email").fill(`analyst_${uniqueSuffix}@test.com`);
    await page.getByLabel("Password").fill("testpass123");

    // Select analyst role (should be default)
    await page.getByRole("button", { name: /create$/i }).click();

    // Dialog should close and user should appear in grid
    await expect(page.getByRole("heading", { name: /create user/i })).not.toBeVisible({
      timeout: 5000,
    });
    await expect(
      page.locator(".ag-cell").filter({ hasText: `analyst_${uniqueSuffix}` }).first()
    ).toBeVisible({ timeout: 5000 });
  });

  test("role selector shows admin/analyst/viewer options", async ({ page }) => {
    await page.getByRole("button", { name: /create user/i }).click();

    // Click the Role select trigger
    const roleSelect = page.locator("[role='combobox']").last();
    await roleSelect.click();

    await expect(page.getByRole("option", { name: /admin/i })).toBeVisible();
    await expect(page.getByRole("option", { name: /analyst/i })).toBeVisible();
    await expect(page.getByRole("option", { name: /viewer/i })).toBeVisible();
  });
});
