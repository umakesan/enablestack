// UAT suite config template. Copy to <project>/uat/playwright.config.ts and set the webServer command.
// Evidence is the point: trace, video and screenshots are always on. One retry; a pass on retry is "met, flaky".
import { defineConfig, devices } from '@playwright/test';

const PORT = Number(process.env.UAT_PORT ?? 4317);

export default defineConfig({
  testDir: './scenarios',
  retries: 1,
  reporter: [['list'], ['json', { outputFile: process.env.UAT_JSON ?? 'uat-results.json' }], ['html', { open: 'never', outputFolder: process.env.UAT_HTML ?? 'uat-html' }]],
  outputDir: process.env.UAT_OUT ?? 'uat-artifacts',
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: 'on',
    video: 'on',
    screenshot: 'on',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } } },
    { name: 'phone', use: { ...devices['Pixel 7'] } },
  ],
  webServer: {
    command: `<start command using PORT=${PORT} and a fresh UAT data file>`,
    url: `http://127.0.0.1:${PORT}`,
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
