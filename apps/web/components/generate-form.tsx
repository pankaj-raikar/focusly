"use client";

import {useRouter} from "next/navigation";
import {useRef, useState} from "react";
import {createJob} from "../lib/api";

export const GenerateForm = () => {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [audienceLevel, setAudienceLevel] = useState<
    "beginner" | "intermediate" | "advanced"
  >("beginner");
  const [duration, setDuration] = useState(60);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const topicRef = useRef<HTMLTextAreaElement>(null);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const trimmedTopic = topic.trim();
    if (trimmedTopic.length < 3) {
      setError("Enter at least 3 characters for your topic.");
      topicRef.current?.focus();
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      const job = await createJob({
        topic: trimmedTopic,
        audienceLevel,
        durationTargetSeconds: duration,
      });
      router.push(`/jobs/${job.jobId}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not start lesson");
      setSubmitting(false);
      topicRef.current?.focus();
    }
  };

  return (
    <form className="generate-form" onSubmit={submit}>
      <div className="form-heading">
        <label htmlFor="topic">What do you want to understand?</label>
        <span>{topic.length}/300</span>
      </div>
      <textarea
        aria-describedby={error ? "topic-error" : undefined}
        autoComplete="off"
        id="topic"
        maxLength={300}
        minLength={3}
        name="topic"
        onChange={(event) => setTopic(event.target.value)}
        placeholder="Try: Why does binary search remove half the list?"
        ref={topicRef}
        required
        rows={4}
        value={topic}
      />
      <div className="form-options">
        <label>
          Level
          <select
            autoComplete="off"
            name="audienceLevel"
            onChange={(event) =>
              setAudienceLevel(
                event.target.value as "beginner" | "intermediate" | "advanced",
              )
            }
            value={audienceLevel}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </label>
        <label>
          Length
          <select
            autoComplete="off"
            name="durationTargetSeconds"
            onChange={(event) => setDuration(Number(event.target.value))}
            value={duration}
          >
            <option value={60}>About 1 minute</option>
            <option value={90}>About 90 seconds</option>
            <option value={120}>About 2 minutes</option>
          </select>
        </label>
      </div>
      {error ? <p className="error" id="topic-error" role="alert">{error}</p> : null}
      <button className="primary-button" disabled={submitting} type="submit">
        {submitting ? "Starting..." : "Make my lesson"}
      </button>
      <p className="form-footnote">No long lectures. Just the part you need.</p>
    </form>
  );
};
