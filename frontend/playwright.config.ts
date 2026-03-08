import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E test configuration.
 *
 * Tests run against the full stack (frontend + backend + DB).
 * In CI, docker compose up must be running before these tests execute.
 * Locally: docker compose up, then npx playwright test.
 */
export default defineConfig({
  testDir: "./src/tests/e2e",
  fullyParallel: false,  // E2E tests may share state, run serially
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: process.env.BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "off",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
