import {existsSync, readdirSync} from "node:fs";
import path from "node:path";
import {defineConfig} from "@playwright/test";

const puppeteerCache = path.join(
  process.env.HOME ?? "",
  ".cache/puppeteer/chrome-headless-shell",
);
const cachedVersion = existsSync(puppeteerCache)
  ? readdirSync(puppeteerCache).sort().at(-1)
  : undefined;
const bundledChromium = process.env.PLAYWRIGHT_CHROMIUM_PATH ??
  (cachedVersion
    ? path.join(
        puppeteerCache,
        cachedVersion,
        "chrome-headless-shell-mac-arm64/chrome-headless-shell",
      )
    : undefined);

export default defineConfig({
  testDir: "./e2e",
  use: {
    baseURL: "http://127.0.0.1:3000",
    launchOptions: bundledChromium ? {executablePath: bundledChromium} : {},
    trace: "retain-on-failure",
  },
  webServer: {
    command: "pnpm dev",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: true,
  },
});
