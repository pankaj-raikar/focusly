"use client";

import {useParams} from "next/navigation";
import Link from "next/link";
import {useEffect, useState} from "react";
import {LessonPlayer} from "../../../components/lesson-player";
import {getLesson, type Lesson} from "../../../lib/api";

export default function LessonPage() {
  const {jobId} = useParams<{jobId: string}>();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getLesson(jobId).then(setLesson).catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : "Could not load lesson");
    });
  }, [jobId]);

  if (error) {
    return <main className="center-shell" id="main-content"><p className="error">{error}</p></main>;
  }
  if (!lesson) {
    return (
      <main className="center-shell" id="main-content">
        <div className="progress-skeleton" aria-label="Loading lesson">
          <span />
          <span />
          <span />
        </div>
      </main>
    );
  }

  return (
    <main className="lesson-shell" id="main-content">
      <header className="lesson-header">
        <Link className="wordmark" href="/">focusly</Link>
        <nav className="header-nav" aria-label="Lesson navigation">
          <Link href="/dashboard">My lessons</Link>
          <Link className="header-action" href="/">New lesson</Link>
        </nav>
      </header>
      <section className="lesson-intro">
        <p className="eyebrow">Your focused lesson</p>
        <h1>{lesson.lesson.title}</h1>
        <p>{lesson.lesson.hook}</p>
      </section>
      <LessonPlayer lesson={lesson} />
      <section className="recap">
        <h2>Keep these three things</h2>
        <ul>
          {lesson.lesson.recap.map((item, index) => (
            <li key={item}>
              <span>{index + 1}</span>
              {item}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
