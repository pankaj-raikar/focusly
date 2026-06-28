"use client";

import {useRef, useState} from "react";
import {findPendingQuiz, QuizCard} from "./quiz-card";
import {getApiUrl, type Lesson} from "../lib/api";

export const LessonPlayer = ({lesson}: {lesson: Lesson}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [answered, setAnswered] = useState<ReadonlySet<number>>(new Set());
  const [activeQuiz, setActiveQuiz] = useState<{
    quiz: Lesson["quizCheckpoints"][number];
    index: number;
  } | null>(null);

  const checkQuiz = (video: HTMLVideoElement) => {
    if (activeQuiz) return;
    const pending = findPendingQuiz(
      lesson.quizCheckpoints,
      video.currentTime,
      answered,
    );
    if (pending) {
      video.pause();
      setActiveQuiz(pending);
    }
  };

  const continueLesson = () => {
    if (!activeQuiz) return;
    setAnswered((completed) => new Set(completed).add(activeQuiz.index));
    setActiveQuiz(null);
    const playback = videoRef.current?.play();
    if (playback) void playback.catch(() => undefined);
  };

  return (
    <>
      <div className="player-frame">
        <video
          controls
          onTimeUpdate={(event) => checkQuiz(event.currentTarget)}
          preload="metadata"
          ref={videoRef}
        >
          <source src={getApiUrl(lesson.videoUrl)} type="video/mp4" />
          <track
            default
            kind="captions"
            label="English"
            src={getApiUrl(lesson.captionsUrl)}
            srcLang="en"
          />
          Your browser does not support video playback.
        </video>
      </div>
      {activeQuiz ? (
        <QuizCard
          key={activeQuiz.index}
          onComplete={continueLesson}
          quiz={activeQuiz.quiz}
        />
      ) : null}
    </>
  );
};
