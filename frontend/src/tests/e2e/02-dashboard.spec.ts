/**
 * E2E tests: Dashboard pages
 *
 * Prerequisites: Full stack running, admin user seeded.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin } from "./helpers";

test.describe("Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test("dashboard page loads after login", async ({ page }) => {
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.locator("main").or(page.locator("#main-content")).or(
      page.getByText(/dashboard/i).first()
    )).toBeVisible({ timeout: 10000 });
  });

  test("sidebar navigation is visible with dashboard link", async ({ page }) => {
    await expect(page.getByRole("navigation").or(page.locator("aside"))).toBeVisible();
    await expect(page.getByRole("link", { name: /dashboard/i })).toBeVisible();
  });

  test("sidebar shows admin-only links for admin user", async ({ page }) => {
    await expect(page.getByRole("link", { name: /integrations/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /admin/i })).toBeVisible();
  });

  test("create dashboard button is present for admin", async ({ page }) => {
    const createButton = page
      .getByRole("button", { name: /create|new dashboard/i })
      .or(page.getByText(/create|new dashboard/i).first());
    await expect(createButton).toBeVisible({ timeout: 5000 });
  });

  test("sidebar collapse toggle works", async ({ page }) => {
    const collapseButton = page.getByRole("button", { name: /collapse sidebar/i });
    await expect(collapseButton).toBeVisible();

    await collapseButton.click();

    const expandButton = page.getByRole("button", { name: /expand sidebar/i });
    await expect(expandButton).toBeVisible();

    await expandButton.click();
    await expect(page.getByRole("button", { name: /collapse sidebar/i })).toBeVisible();
  });

  test("SQL Editor link navigates to sql-editor page", async ({ page }) => {
    await page.getByRole("link", { name: /sql editor/i }).click();
    await expect(page).toHaveURL(/\/sql-editor/, { timeout: 5000 });
  });

  test("Agent link navigates to agent page", async ({ page }) => {
    await page.getByRole("link", { name: /agent search/i }).click();
    await expect(page).toHaveURL(/\/agent/, { timeout: 5000 });
  });
});
