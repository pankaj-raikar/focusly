"use client";

import {useParams, useRouter} from "next/navigation";
import Link from "next/link";
import {useEffect, useState} from "react";
import {JobProgress} from "../../../components/job-progress";
import {getJob, type Job} from "../../../lib/api";

export default function JobPage() {
  const {jobId} = useParams<{jobId: string}>();
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    let timeout: ReturnType<typeof setTimeout>;

    const poll = async () => {
      try {
        const nextJob = await getJob(jobId);
        if (cancelled) return;
        setJob(nextJob);
        if (nextJob.status === "succeeded") {
          router.replace(`/lessons/${jobId}`);
        } else if (nextJob.status !== "failed") {
          timeout = setTimeout(poll, 1500);
        }
      } catch (reason) {
        if (!cancelled) {
          setError(reason instanceof Error ? reason.message : "Could not load job");
        }
      }
    };

    void poll();
    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [jobId, router]);

  return (
    <main className="center-shell" id="main-content">
      <header className="compact-header">
        <Link className="wordmark" href="/">focusly</Link>
        <Link className="header-action" href="/dashboard">My lessons</Link>
      </header>
      {error ? <p className="error" role="alert">{error}</p> : null}
      {job ? <JobProgress job={job} /> : (
        <div className="progress-skeleton" aria-label="Loading lesson progress">
          <span />
          <span />
          <span />
        </div>
      )}
      {job?.status === "failed" ? (
        <div className="failure-panel">
          <p>{job.safeError}</p>
          <Link className="secondary-button" href="/">Try another topic</Link>
        </div>
      ) : null}
    </main>
  );
}
