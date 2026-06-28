import Link from "next/link";
import type {Job} from "../lib/api";

export const JobCard = ({
  job,
  onRetry,
}: {
  job: Job;
  onRetry: (jobId: string) => void;
}) => (
  <article className="job-card">
    <div>
      <p className="job-status">{job.status}</p>
      <h2>{job.topic}</h2>
      <p>
        {job.audienceLevel} · {job.durationTargetSeconds} seconds
      </p>
    </div>
    {job.status === "succeeded" ? (
      <Link className="secondary-button" href={`/lessons/${job.jobId}`}>
        Watch lesson
      </Link>
    ) : job.status === "failed" ? (
      <div>
        <p className="error">{job.safeError}</p>
        <button
          className="secondary-button"
          disabled={!job.isRetryable}
          onClick={() => onRetry(job.jobId)}
          type="button"
        >
          Retry lesson
        </button>
      </div>
    ) : (
      <div className="job-progress">
        <strong>{job.progressPercent}%</strong>
        <Link href={`/jobs/${job.jobId}`}>View progress</Link>
      </div>
    )}
  </article>
);
