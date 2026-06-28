import {describe, expect, it} from "vitest";
import {findPendingQuiz} from "../components/quiz-card";

describe("quiz timing", () => {
  const quizzes = [
    {question: "First?", timestampSeconds: 10},
    {question: "Second?", timestampSeconds: 20},
  ];

  it("keeps the earliest reached unanswered quiz active", () => {
    expect(findPendingQuiz(quizzes, 12, new Set())?.quiz.question).toBe("First?");
    expect(findPendingQuiz(quizzes, 21, new Set())?.quiz.question).toBe("First?");
    expect(findPendingQuiz(quizzes, 21, new Set([0]))?.quiz.question).toBe("Second?");
    expect(findPendingQuiz(quizzes, 30, new Set([0, 1]))).toBeUndefined();
  });
});
