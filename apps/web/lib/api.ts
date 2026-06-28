const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type JobStatus = "queued" | "running" | "succeeded" | "failed";

export type Job = {
  jobId: string;
  topic: string;
  audienceLevel: "beginner" | "intermediate" | "advanced";
  durationTargetSeconds: number;
  status: JobStatus;
  stage: string;
  progressPercent: number;
  isRetryable: boolean;
  safeError: string | null;
  createdAt: string;
  updatedAt: string;
};

export type QuizCheckpoint = {
  afterSegmentId: string;
  question: string;
  options: string[];
  correctOptionIndex: number;
  explanation: string;
  timestampSeconds: number;
};

export type Lesson = {
  jobId: string;
  lesson: {
    title: string;
    hook: string;
    learningObjectives: string[];
    recap: string[];
  };
  videoUrl: string;
  captionsUrl: string;
  quizCheckpoints: QuizCheckpoint[];
};

export const getApiUrl = (path: string) =>
  path.startsWith("http://") || path.startsWith("https://")
    ? path
    : `${API_URL}${path}`;

const request = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(getApiUrl(path), init);
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as {detail?: string};
    throw new Error(body.detail ?? "Request failed");
  }
  return response.json() as Promise<T>;
};

export const createJob = (input: {
  topic: string;
  audienceLevel: "beginner" | "intermediate" | "advanced";
  durationTargetSeconds: number;
}) =>
  request<Job>("/api/jobs", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(input),
  });

export const getJob = (jobId: string) => request<Job>(`/api/jobs/${jobId}`);

export const listJobs = () => request<Job[]>("/api/jobs");

export const retryJob = (jobId: string) =>
  request<Job>(`/api/jobs/${jobId}/retry`, {method: "POST"});

export const getLesson = (jobId: string) =>
  request<Lesson>(`/api/jobs/${jobId}/lesson`);
