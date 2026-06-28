"use client";

import Link from "next/link";
import {useRouter} from "next/navigation";
import {useEffect, useState} from "react";
import {JobCard} from "../../components/job-card";
import {listJobs, retryJob, type Job} from "../../lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    listJobs().then(setJobs).catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : "Could not load lessons");
    });
  }, []);

  const retry = async (jobId: string) => {
    try {
      const job = await retryJob(jobId);
      router.push(`/jobs/${job.jobId}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not retry lesson");
    }
  };

  return (
    <main className="dashboard-shell" id="main-content">
      <header className="site-header">
        <Link className="wordmark" href="/">focusly</Link>
        <Link className="header-action" href="/">New lesson</Link>
      </header>
      <section className="dashboard-heading">
        <p className="eyebrow">Your library</p>
        <h1>My lessons</h1>
        <p>Continue an active lesson, retry a failure, or watch one again.</p>
      </section>
      {error ? <p className="error" role="alert">{error}</p> : null}
      {jobs === null ? (
        <div className="progress-skeleton" aria-label="Loading lessons">
          <span />
          <span />
          <span />
        </div>
      ) : jobs.length === 0 ? (
        <section className="empty-library">
          <h2>No lessons yet</h2>
          <p>Generate your first focused lesson to start this library.</p>
          <Link className="primary-button" href="/">Make a lesson</Link>
        </section>
      ) : (
        <section className="job-list" aria-label="Lessons">
          {jobs.map((job) => (
            <JobCard job={job} key={job.jobId} onRetry={retry} />
          ))}
        </section>
      )}
    </main>
  );
}
