"use client";

import {useState} from "react";
import type {QuizCheckpoint} from "../lib/api";

type TimedQuiz = Pick<QuizCheckpoint, "question" | "timestampSeconds">;

export const findPendingQuiz = <T extends TimedQuiz>(
  quizzes: T[],
  currentTime: number,
  answered: ReadonlySet<number>,
) => {
  const index = quizzes.findIndex(
    (quiz, quizIndex) =>
      currentTime >= quiz.timestampSeconds && !answered.has(quizIndex),
  );
  return index === -1 ? undefined : {quiz: quizzes[index]!, index};
};

export const QuizCard = ({
  quiz,
  onComplete,
}: {
  quiz: QuizCheckpoint;
  onComplete: () => void;
}) => {
  const [answer, setAnswer] = useState<number | null>(null);

  return (
    <section className="quiz-card" aria-live="polite">
      <p className="quiz-label">Quick check</p>
      <h2>{quiz.question}</h2>
      <div className="quiz-options">
        {quiz.options.map((option, index) => (
          <button
            aria-pressed={answer === index}
            className={
              answer === null
                ? "quiz-option"
                : index === quiz.correctOptionIndex
                  ? "quiz-option correct"
                  : answer === index
                    ? "quiz-option incorrect"
                    : "quiz-option"
            }
            key={option}
            onClick={() => setAnswer(index)}
            type="button"
          >
            {option}
          </button>
        ))}
      </div>
      {answer !== null ? <p className="quiz-explanation">{quiz.explanation}</p> : null}
      {answer !== null ? (
        <button className="primary-button quiz-continue" onClick={onComplete} type="button">
          Continue lesson
        </button>
      ) : null}
    </section>
  );
};
