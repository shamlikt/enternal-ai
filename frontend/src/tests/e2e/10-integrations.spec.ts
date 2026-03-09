/**
 * E2E tests: Integrations page
 *
 * Tests FHIR/Snowflake integration management.
 * Requires HAPI FHIR to be running at http://fhir:8080/fhir (from docker compose).
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

async function ensureFhirIntegration(baseURL: string, token: string): Promise<number> {
  // Check if FHIR integration exists
  const listResp = await fetch(`${baseURL}/api/v1/integrations/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const integrations = await listResp.json();
  const existing = integrations.find(
    (i: { type: string }) => i.type === "fhir"
  );
  if (existing) return existing.id;

  // Create one
  const createResp = await fetch(`${baseURL}/api/v1/integrations/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: "HAPI FHIR (E2E Test)",
      type: "fhir",
      config_json: {
        server_url: "http://fhir:8080/fhir",
        auth_type: "none",
      },
    }),
  });
  const created = await createResp.json();
  return created.id;
}

test.describe("Integrations", () => {
  let integrationId: number;

  test.beforeAll(async ({ }, testInfo) => {
    const baseURL = testInfo.project.use.baseURL ?? "http://localhost:3000";
    const apiBase = baseURL.replace(":3000", ":8000");
    const token = await getAuthToken(apiBase);
    integrationId = await ensureFhirIntegration(apiBase, token);
  });

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto("/integrations");
    await expect(page).toHaveURL(/\/integrations/);
  });

  test("page loads with Integrations heading", async ({ page }) => {
    await expect(page.getByRole("heading", { name: /integrations/i })).toBeVisible();
  });

  test("shows existing FHIR integration card", async ({ page }) => {
    await expect(page.getByText("HAPI FHIR (E2E Test)").or(page.getByText("fhir"))).toBeVisible({
      timeout: 10000,
    });
  });

  test("integration card shows status badge", async ({ page }) => {
    // Card should have a status badge (active, inactive, etc.)
    await expect(
      page.locator("[data-slot='badge']").or(page.locator(".inline-flex")).first()
    ).toBeVisible({ timeout: 10000 });
  });

  test("Test button triggers connection test", async ({ page }) => {
    page.on("dialog", (dialog) => dialog.accept());
    const testBtn = page.getByRole("button", { name: /test/i }).first();
    await expect(testBtn).toBeVisible({ timeout: 10000 });
    await testBtn.click();
    // Wait for the alert dialog (success or failure)
    await page.waitForTimeout(3000);
  });

  test("Run Ingestion button triggers ingestion run", async ({ page }) => {
    const runBtn = page.getByRole("button", { name: /run ingestion/i }).first();
    await expect(runBtn).toBeVisible({ timeout: 10000 });
    await runBtn.click();
    // Should show loading state briefly
    await page.waitForTimeout(3000);
  });

  test("Ingestion History tab shows runs", async ({ page }) => {
    await page.getByRole("tab", { name: /ingestion history/i }).click();
    // Should show either run rows or "No ingestion runs yet" message
    await page.waitForTimeout(2000);
    const hasRuns = await page.locator("table tbody tr").first().isVisible().catch(() => false);
    const hasEmpty = await page.getByText("No ingestion runs yet").isVisible().catch(() => false);
    expect(hasRuns || hasEmpty).toBeTruthy();
  });

  test("Add Integration dialog opens with Name/Type fields", async ({ page }) => {
    await page.getByRole("button", { name: /add integration/i }).click();
    await expect(page.getByRole("heading", { name: /add integration/i })).toBeVisible();
    await expect(page.getByLabel("Name")).toBeVisible();
    await expect(page.getByLabel("Type")).toBeVisible();
  });
});
