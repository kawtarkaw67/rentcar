import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests_e2e',
  timeout: 30000,
  retries: 0,
  use: {
    baseURL: 'http://127.0.0.1:8000',
    headless: true,
  },
});
