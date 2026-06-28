import {fireEvent, render, screen} from "@testing-library/react";
import {describe, expect, it, vi} from "vitest";
import {JobCard} from "../components/job-card";
import type {Job} from "../lib/api";

const job = (status: Job["status"]): Job => ({
  jobId: `${status}-job`,
  topic: "Explain binary search",
  audienceLevel: "beginner",
  durationTargetSeconds: 60,
  status,
  stage: status,
  progressPercent: status === "succeeded" ? 100 : 45,
  isRetryable: status === "failed",
  safeError: status === "failed" ? "Lesson generation failed." : null,
  createdAt: "2026-06-25T00:00:00Z",
  updatedAt: "2026-06-25T00:00:00Z",
});

describe("JobCard", () => {
  it("links completed lessons to playback", () => {
    render(<JobCard job={job("succeeded")} onRetry={vi.fn()} />);

    expect(screen.getByRole("link", {name: "Watch lesson"})).toHaveAttribute(
      "href",
      "/lessons/succeeded-job",
    );
  });

  it("shows progress for active jobs and retries failed jobs", () => {
    const onRetry = vi.fn();
    const {rerender} = render(
      <JobCard job={job("running")} onRetry={onRetry} />,
    );

    expect(screen.getByText("45%")).toBeInTheDocument();

    rerender(<JobCard job={job("failed")} onRetry={onRetry} />);
    fireEvent.click(screen.getByRole("button", {name: "Retry lesson"}));
    expect(onRetry).toHaveBeenCalledWith("failed-job");
  });
});
