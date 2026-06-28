import {mkdir, rename, writeFile} from "node:fs/promises";
import path from "node:path";
import {pathToFileURL} from "node:url";

const ROOT = path.resolve(process.cwd(), "../..");
const {chromium} = await import(
  pathToFileURL(path.join(process.cwd(), "node_modules", "@playwright", "test", "index.mjs"))
);
const stamp = new Date().toISOString().replace(/[:.]/g, "-");
const outDir = path.join(ROOT, "outputs", "playwright", `focusly-showcase-${stamp}`);
const shotsDir = path.join(outDir, "screenshots");
const videosDir = path.join(outDir, "videos");
const baseUrl = process.env.FOCUSLY_WEB_URL ?? "http://localhost:3000";
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

await mkdir(shotsDir, {recursive: true});
await mkdir(videosDir, {recursive: true});

const browser = await chromium.launch({headless: true});
const manifest = [];

const safeName = (name) => name.replace(/[^a-z0-9-]+/gi, "-").toLowerCase();

async function withPage(label, fn) {
  const context = await browser.newContext({
    viewport: {width: 1440, height: 1000},
    recordVideo: {dir: videosDir, size: {width: 1440, height: 1000}},
  });
  const page = await context.newPage();
  page.setDefaultTimeout(30_000);
  await page.addInitScript(() => {
    const hideDevTools = () => {
      for (const element of document.querySelectorAll("nextjs-portal, [data-nextjs-dev-tools-button]")) {
        element.remove();
      }
      for (const element of document.querySelectorAll("[aria-label]")) {
        const label = element.getAttribute("aria-label") ?? "";
        const style = getComputedStyle(element);
        if (/next\.?js/i.test(label) && style.position === "fixed") element.remove();
      }
    };
    hideDevTools();
    new MutationObserver(hideDevTools).observe(document.documentElement, {
      childList: true,
      subtree: true,
    });
  });
  const shots = [];

  async function shot(name, options = {}) {
    await page.evaluate(() => {
      for (const element of document.querySelectorAll("nextjs-portal")) {
        element.remove();
      }
    });
    const file = path.join(shotsDir, `${String(manifest.length + 1).padStart(2, "0")}-${safeName(name)}.png`);
    await page.screenshot({path: file, fullPage: true, ...options});
    shots.push(file);
    console.log(`screenshot ${file}`);
    return file;
  }

  try {
    await fn(page, shot);
  } finally {
    await page.waitForTimeout(750).catch(() => undefined);
    const video = page.video();
    await context.close();
    const rawVideo = video ? await video.path().catch(() => null) : null;
    const finalVideo = rawVideo ? path.join(videosDir, `${safeName(label)}.webm`) : null;
    if (rawVideo && finalVideo) await rename(rawVideo, finalVideo);
    manifest.push({label, screenshots: shots, video: finalVideo});
    console.log(`video ${finalVideo}`);
  }
}

async function jobs() {
  const response = await fetch(`${apiUrl}/api/jobs`);
  if (!response.ok) throw new Error(`Could not load jobs: ${response.status}`);
  return response.json();
}

const allJobs = await jobs();
const completed = allJobs.find((job) => job.status === "succeeded");
const failed = allJobs.find((job) => job.status === "failed");
const completedLesson = completed
  ? await fetch(`${apiUrl}/api/jobs/${completed.jobId}/lesson`).then((response) => response.json())
  : null;

await withPage("01-home-generate-form", async (page, shot) => {
  await page.goto(baseUrl, {waitUntil: "networkidle"});
  await shot("home-start");
  await page.getByRole("button", {name: /make my lesson/i}).click();
  await shot("home-validation");
  await page.getByLabel(/what do you want/i).fill("Why does binary search remove half the list?");
  await page.getByLabel("Level").selectOption("intermediate");
  await page.getByLabel("Length").selectOption("60");
  await shot("home-filled-form");
});

await withPage("02-dashboard-library", async (page, shot) => {
  await page.goto(`${baseUrl}/dashboard`, {waitUntil: "networkidle"});
  await page.getByRole("heading", {name: /my lessons/i}).waitFor();
  await shot("dashboard-library");
});

if (failed) {
  await withPage("03-failed-job-retry-state", async (page, shot) => {
    await page.goto(`${baseUrl}/jobs/${failed.jobId}`, {waitUntil: "networkidle"});
    await page.getByRole("heading", {name: /could not be completed/i}).waitFor();
    await shot("failed-job-state");
  });
}

if (completed) {
  await withPage("04-completed-lesson-player", async (page, shot) => {
    await page.goto(`${baseUrl}/lessons/${completed.jobId}`, {waitUntil: "networkidle"});
    await page.getByRole("heading", {level: 1}).waitFor();
    await shot("lesson-overview");
    const quiz = completedLesson.quizCheckpoints[0];
    await page.locator("video").evaluate((video, quizTime) => {
      video.currentTime = quizTime;
      video.dispatchEvent(new Event("timeupdate", {bubbles: true}));
    }, quiz.timestampSeconds + 0.5);
    await page.getByText(/quick check/i).waitFor();
    await shot("lesson-quiz-checkpoint");
    await page.getByRole("button", {name: quiz.options[quiz.correctOptionIndex]}).click();
    await shot("lesson-quiz-answer");
  });
}

await withPage("05-live-generation-progress", async (page, shot) => {
  await page.goto(baseUrl, {waitUntil: "networkidle"});
  await page.getByLabel(/what do you want/i).fill("How do neural networks learn from examples?");
  await page.getByLabel("Level").selectOption("beginner");
  await page.getByLabel("Length").selectOption("60");
  await shot("live-generation-before-submit");
  await page.getByRole("button", {name: /make my lesson/i}).click();
  await page.waitForURL(/\/jobs\//);
  await shot("live-generation-started");

  const seen = new Set();
  const deadline = Date.now() + 180_000;
  while (Date.now() < deadline) {
    await page.waitForTimeout(4000);
    if (/\/lessons\//.test(page.url())) {
      await page.getByRole("heading", {level: 1}).waitFor();
      await shot("live-generation-complete");
      return;
    }
    const percent = await page.locator(".progress-heading strong").textContent().catch(() => "");
    const stage = await page.locator(".progress-card h1").textContent().catch(() => "");
    const key = `${percent}-${stage}`;
    if (percent && !seen.has(key)) {
      seen.add(key);
      await shot(`live-generation-${percent}-${stage}`);
    }
    if (await page.getByText(/could not be completed/i).isVisible().catch(() => false)) {
      await shot("live-generation-failed");
      return;
    }
  }
  await shot("live-generation-timeout-latest-state");
});

await browser.close();

await writeFile(
  path.join(outDir, "manifest.json"),
  JSON.stringify({createdAt: new Date().toISOString(), baseUrl, apiUrl, artifacts: manifest}, null, 2),
);

console.log(`done ${outDir}`);
