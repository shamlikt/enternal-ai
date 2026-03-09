/**
 * E2E tests: Dashboard CRUD operations
 *
 * Tests dashboard listing, creation (via API), and navigation.
 */
import { test, expect } from "@playwright/test";
import { loginAsAdmin, ADMIN_USERNAME, ADMIN_PASSWORD } from "./helpers";

async function getAuthToken(baseURL: string): Promise<string> {
  const resp = await fetch(`${baseURL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `username=${ADMIN_USERNAME}&password=${ADMIN_PASSWORD}`,
  });
  const data = await resp.json();
  return data.access_token;
}

test.describe("Dashboard CRUD", () => {
  let dashboardId: number | null = null;
  const dashboardName = `E2E Dashboard ${Date.now()}`;

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test("dashboard list page renders", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: /dashboards/i })).toBeVisible();
    // Should show New Dashboard button or empty state
    await expect(
      page
        .getByRole("button", { name: /new dashboard/i })
        .or(page.getByText(/create|new dashboard/i).first())
    ).toBeVisible({ timeout: 5000 });
  });

  test("create dashboard via API and verify it appears in UI", async ({ page }, testInfo) => {
    const baseURL = testInfo.project.use.baseURL ?? "http://localhost:3000";
    const apiBase = baseURL.replace(":3000", ":8000");
    const token = await getAuthToken(apiBase);

    // Create dashboard via API
    const resp = await fetch(`${apiBase}/api/v1/dashboards/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: dashboardName,
        description: "Created by E2E test",
        is_public: false,
      }),
    });
    const dashboard = await resp.json();
    dashboardId = dashboard.id;

    // Navigate to dashboards page and verify it appears
    await page.goto("/dashboard");
    await expect(page.getByText(dashboardName)).toBeVisible({ timeout: 10000 });
  });

  test("click dashboard card navigates to dashboard view", async ({ page }, testInfo) => {
    if (!dashboardId) {
      // Create one first if the previous test didn't run
      const baseURL = testInfo.project.use.baseURL ?? "http://localhost:3000";
      const apiBase = baseURL.replace(":3000", ":8000");
      const token = await getAuthToken(apiBase);
      const resp = await fetch(`${apiBase}/api/v1/dashboards/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: `E2E Nav Dashboard ${Date.now()}`,
          description: "Created by E2E test",
          is_public: false,
        }),
      });
      const dashboard = await resp.json();
      dashboardId = dashboard.id;
    }

    await page.goto("/dashboard");
    // Click on any dashboard card (first one available)
    const card = page.locator("a[href*='/dashboard/']").first();
    await expect(card).toBeVisible({ timeout: 10000 });
    await card.click();
    // Should navigate to individual dashboard view
    await expect(page).toHaveURL(/\/dashboard\/\d+/, { timeout: 5000 });
  });
});
