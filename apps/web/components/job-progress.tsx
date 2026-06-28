import type {Job} from "../lib/api";

const stageCopy: Record<string, string> = {
  queued: "Your lesson is in line.",
  planning: "Shaping the lesson into a few clear ideas.",
  narrating: "Giving each idea a calm voice.",
  rendering: "Turning the explanation into motion.",
  succeeded: "Your lesson is ready.",
  failed: "The lesson could not be completed.",
};

export const JobProgress = ({job}: {job: Job}) => (
  <section className="progress-card" aria-live="polite">
    <div className="progress-heading">
      <p>Building your lesson</p>
      <strong>{job.progressPercent}%</strong>
    </div>
    <div
      aria-label={`${job.progressPercent}% complete`}
      aria-valuemax={100}
      aria-valuemin={0}
      aria-valuenow={job.progressPercent}
      className="progress-track"
      role="progressbar"
    >
      <div style={{width: `${job.progressPercent}%`}} />
    </div>
    <h1>{stageCopy[job.stage] ?? "Working on your lesson."}</h1>
    <p>Keep this tab open. Short lessons usually finish in a few minutes.</p>
    <div className="stage-list" aria-hidden="true">
      <span className={job.progressPercent >= 15 ? "is-done" : ""}>Plan</span>
      <span className={job.progressPercent >= 40 ? "is-done" : ""}>Explain</span>
      <span className={job.progressPercent >= 70 ? "is-done" : ""}>Animate</span>
      <span className={job.progressPercent >= 100 ? "is-done" : ""}>Ready</span>
    </div>
  </section>
);
