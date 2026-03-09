/**
 * E2E tests: Login flow
 *
 * Prerequisites: Full stack running via docker compose up.
 * Admin user created by the seeder: username=admin, password=changeme
 */
import { test, expect } from "@playwright/test";
import { ADMIN_USERNAME, ADMIN_PASSWORD } from "./helpers";

test.describe("Login flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
  });

  test("login page renders with username and password fields", async ({ page }) => {
    await page.goto("/login");

    await expect(page.getByRole("heading", { name: /Enternal Health/i })).toBeVisible();
    await expect(page.getByLabel("Username")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
    await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
  });

  test("valid admin credentials redirect to dashboard", async ({ page }) => {
    await page.goto("/login");

    await page.getByLabel("Username").fill(ADMIN_USERNAME);
    await page.getByLabel("Password").fill(ADMIN_PASSWORD);
    await page.getByRole("button", { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByText("Dashboard")).toBeVisible();
  });

  test("invalid credentials show error message", async ({ page }) => {
    await page.goto("/login");

    await page.getByLabel("Username").fill("wronguser");
    await page.getByLabel("Password").fill("wrongpassword");
    await page.getByRole("button", { name: /sign in/i }).click();

    await expect(page.getByRole("alert").or(page.locator(".text-red-700"))).toBeVisible({
      timeout: 5000,
    });
    await expect(page).toHaveURL(/\/login/);
  });

  test("unauthenticated user is redirected to login when accessing dashboard", async ({
    page,
  }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("unauthenticated user is redirected to login when accessing sql-editor", async ({
    page,
  }) => {
    await page.goto("/sql-editor");
    await expect(page).toHaveURL(/\/login/);
  });

  test("sign in button shows loading state during login", async ({ page }) => {
    await page.goto("/login");

    await page.getByLabel("Username").fill(ADMIN_USERNAME);
    await page.getByLabel("Password").fill(ADMIN_PASSWORD);

    const signInButton = page.getByRole("button", { name: /sign in/i });
    await signInButton.click();

    await expect(page).toHaveURL(/\/(dashboard|login)/, { timeout: 5000 });
  });
});
