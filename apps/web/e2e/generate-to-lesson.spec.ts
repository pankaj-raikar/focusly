import {expect, test} from "@playwright/test";

test("generates, polls, and opens a lesson with captions and quiz", async ({
  page,
}) => {
  let polls = 0;
  await page.route("http://localhost:8000/api/jobs", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      status: 202,
      body: JSON.stringify({
        jobId: "job-1",
        status: "queued",
        stage: "queued",
        progressPercent: 0,
        safeError: null,
        createdAt: "2026-06-24T00:00:00Z",
        updatedAt: "2026-06-24T00:00:00Z",
      }),
    });
  });
  await page.route("http://localhost:8000/api/jobs/job-1", async (route) => {
    polls += 1;
    const running = polls <= 2;
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        jobId: "job-1",
        status: running ? "running" : "succeeded",
        stage: running ? "narrating" : "succeeded",
        progressPercent: running ? 45 : 100,
        safeError: null,
        createdAt: "2026-06-24T00:00:00Z",
        updatedAt: "2026-06-24T00:00:01Z",
      }),
    });
  });
  await page.route(
    "http://localhost:8000/api/jobs/job-1/lesson",
    async (route) => {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          jobId: "job-1",
          lesson: {
            title: "Binary Search",
            hook: "Remove half the choices.",
            learningObjectives: ["Explain binary search"],
            recap: ["Use sorted data", "Check the middle", "Remove half"],
          },
          videoUrl: "/media/job-1/lesson.mp4",
          captionsUrl: "/media/job-1/captions.vtt",
          quizCheckpoints: [
            {
              afterSegmentId: "segment-1",
              question: "What does one comparison remove?",
              options: ["Half", "One item"],
              correctOptionIndex: 0,
              explanation: "Binary search removes the impossible half.",
              timestampSeconds: 10,
            },
          ],
        }),
      });
    },
  );

  await page.goto("/");
  const topic = page.getByLabel("What do you want to understand?");
  await topic.fill("   ");
  await page.getByRole("button", {name: "Make my lesson"}).click();
  await expect(
    page.getByText("Enter at least 3 characters for your topic."),
  ).toBeVisible();
  await expect(topic).toBeFocused();

  await topic.fill("Explain binary search");
  await page.getByRole("button", {name: "Make my lesson"}).click();

  await expect(page).toHaveURL(/\/jobs\/job-1/);
  await expect(page.getByText("Giving each idea a calm voice.")).toBeVisible();
  await expect(page).toHaveURL(/\/lessons\/job-1/, {timeout: 5_000});
  await expect(page.getByRole("heading", {name: "Binary Search"})).toBeVisible();
  await expect(page.locator("track[kind='captions']")).toHaveAttribute("default", "");

  await page.locator("video").evaluate((video) => {
    Object.defineProperty(video, "currentTime", {
      value: 11,
      configurable: true,
    });
    video.dispatchEvent(new Event("timeupdate"));
  });
  await expect(
    page.getByRole("heading", {name: "What does one comparison remove?"}),
  ).toBeVisible();
  await expect(page.locator("video")).toHaveJSProperty("paused", true);
  await page.getByRole("button", {name: "Half"}).click();
  await expect(
    page.getByText("Binary search removes the impossible half."),
  ).toBeVisible();
  await page.getByRole("button", {name: "Continue lesson"}).click();
  await expect(
    page.getByRole("heading", {name: "What does one comparison remove?"}),
  ).not.toBeVisible();
});

test("retries a failed lesson from the dashboard", async ({page}) => {
  let retryPolls = 0;
  const failedJob = {
    jobId: "failed-job",
    topic: "Explain recursion",
    audienceLevel: "beginner",
    durationTargetSeconds: 60,
    status: "failed",
    stage: "failed",
    progressPercent: 45,
    isRetryable: true,
    safeError: "Lesson generation failed. Please try again.",
    createdAt: "2026-06-25T00:00:00Z",
    updatedAt: "2026-06-25T00:00:01Z",
  };
  const retryJob = {
    ...failedJob,
    jobId: "retry-job",
    status: "queued",
    stage: "queued",
    progressPercent: 0,
    isRetryable: false,
    safeError: null,
  };

  await page.route("http://localhost:8000/api/jobs", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify([failedJob]),
      });
      return;
    }
    await route.fulfill({
      contentType: "application/json",
      status: 202,
      body: JSON.stringify(failedJob),
    });
  });
  await page.route(
    "http://localhost:8000/api/jobs/failed-job",
    async (route) => {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify(failedJob),
      });
    },
  );
  await page.route(
    "http://localhost:8000/api/jobs/failed-job/retry",
    async (route) => {
      await route.fulfill({
        contentType: "application/json",
        status: 202,
        body: JSON.stringify(retryJob),
      });
    },
  );
  await page.route(
    "http://localhost:8000/api/jobs/retry-job",
    async (route) => {
      retryPolls += 1;
      const succeeded = retryPolls > 2;
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          ...retryJob,
          status: succeeded ? "succeeded" : "running",
          stage: succeeded ? "succeeded" : "rendering",
          progressPercent: succeeded ? 100 : 75,
        }),
      });
    },
  );
  await page.route(
    "http://localhost:8000/api/jobs/retry-job/lesson",
    async (route) => {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          jobId: "retry-job",
          lesson: {
            title: "Recursion",
            hook: "A function can call itself.",
            learningObjectives: ["Explain recursion"],
            recap: ["Base case", "Recursive step"],
          },
          videoUrl: "/media/retry-job/lesson.mp4",
          captionsUrl: "/media/retry-job/captions.vtt",
          quizCheckpoints: [],
        }),
      });
    },
  );

  await page.goto("/");
  await page.getByLabel("What do you want to understand?").fill("Explain recursion");
  await page.getByRole("button", {name: "Make my lesson"}).click();
  await expect(page).toHaveURL(/\/jobs\/failed-job/);
  await expect(page.getByText("Lesson generation failed. Please try again.")).toBeVisible();

  await page.getByRole("link", {name: "My lessons"}).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await page.getByRole("button", {name: "Retry lesson"}).click();

  await expect(page).toHaveURL(/\/jobs\/retry-job/);
  await expect(page.getByText("Turning the explanation into motion.")).toBeVisible();
  await expect(page).toHaveURL(/\/lessons\/retry-job/, {timeout: 5_000});
  await expect(page.getByRole("heading", {name: "Recursion"})).toBeVisible();
});
