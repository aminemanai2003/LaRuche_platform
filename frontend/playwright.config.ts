import { defineConfig, devices } from '@playwright/test'

/**
 * E2E config — runs against the already-running Vite dev server on :5173.
 * Start the app first:  npm run dev   (in frontend/)
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
})
