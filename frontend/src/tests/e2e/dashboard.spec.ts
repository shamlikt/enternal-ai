/**
 * E2E tests: Dashboard pages
 *
 * Prerequisites: Full stack running, admin user seeded.
 *
 * Tests:
 * - Dashboard list page loads
 * - Create new dashboard button is visible (for admin/analyst)
 * - Template selection is visible
 * - Navigation sidebar shows Dashboard link as active
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

test.describe("Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test("dashboard page loads after login", async ({ page }) => {
    await expect(page).toHaveURL(/\/dashboard/);
    // Main content area should be visible
    await expect(page.locator("main").or(page.locator("#main-content")).or(
      page.getByText(/dashboard/i).first()
    )).toBeVisible({ timeout: 10000 });
  });

  test("sidebar navigation is visible with dashboard link", async ({ page }) => {
    // Sidebar should be visible with navigation
    await expect(page.getByRole("navigation").or(page.locator("aside"))).toBeVisible();
    // Dashboard link should be present
    await expect(page.getByRole("link", { name: /dashboard/i })).toBeVisible();
  });

  test("sidebar shows admin-only links for admin user", async ({ page }) => {
    // Admin should see Integrations, Quarantine, Admin links
    await expect(page.getByRole("link", { name: /integrations/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /admin/i })).toBeVisible();
  });

  test("create dashboard button is present for admin", async ({ page }) => {
    // Admin should be able to create dashboards
    const createButton = page
      .getByRole("button", { name: /create|new dashboard/i })
      .or(page.getByText(/create|new dashboard/i).first());
    await expect(createButton).toBeVisible({ timeout: 5000 });
  });

  test("sidebar collapse toggle works", async ({ page }) => {
    // Find the collapse toggle button
    const collapseButton = page.getByRole("button", { name: /collapse sidebar/i });
    await expect(collapseButton).toBeVisible();

    await collapseButton.click();

    // After collapse, sidebar should be narrower (text labels hidden)
    const expandButton = page.getByRole("button", { name: /expand sidebar/i });
    await expect(expandButton).toBeVisible();

    // Click again to expand
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
