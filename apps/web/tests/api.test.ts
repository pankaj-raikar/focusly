import {afterEach, describe, expect, it, vi} from "vitest";
import {createJob, getApiUrl, getJob, listJobs, retryJob} from "../lib/api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("API client", () => {
  it("creates a job with the documented request contract", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({jobId: "job-1", status: "queued"}), {
        status: 202,
        headers: {"Content-Type": "application/json"},
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const job = await createJob({
      topic: "Explain binary search",
      audienceLevel: "beginner",
      durationTargetSeconds: 60,
    });

    expect(job.jobId).toBe("job-1");
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/jobs",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          topic: "Explain binary search",
          audienceLevel: "beginner",
          durationTargetSeconds: 60,
        }),
      }),
    );
  });

  it("throws the API detail for failed requests", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({detail: "Job not found"}), {
          status: 404,
          headers: {"Content-Type": "application/json"},
        }),
      ),
    );

    await expect(getJob("missing")).rejects.toThrow("Job not found");
  });

  it("lists jobs and retries a failed job", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([{jobId: "failed-job", status: "failed"}])),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({jobId: "retry-job", status: "queued"}), {
          status: 202,
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    expect(await listJobs()).toEqual([
      expect.objectContaining({jobId: "failed-job"}),
    ]);
    expect(await retryJob("failed-job")).toEqual(
      expect.objectContaining({jobId: "retry-job"}),
    );
    expect(fetchMock).toHaveBeenLastCalledWith(
      "http://localhost:8000/api/jobs/failed-job/retry",
      {method: "POST"},
    );
  });

  it("keeps absolute media URLs and prefixes relative ones", () => {
    expect(getApiUrl("https://media.example/video.mp4")).toBe(
      "https://media.example/video.mp4",
    );
    expect(getApiUrl("/media/job/video.mp4")).toBe(
      "http://localhost:8000/media/job/video.mp4",
    );
  });
});
