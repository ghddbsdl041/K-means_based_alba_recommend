import { useState, useMemo } from "react";
import { QUESTIONS } from "../types/survey";
import type { AnswerValue, SurveyAnswers } from "../types/survey";

export function useSurvey() {
  const [answers, setAnswers] = useState<SurveyAnswers>({});
  const [currentStep, setCurrentStep] = useState(0);

  const visibleQuestions = useMemo(() => {
    return QUESTIONS.filter((q) => {
      if (!q.condition) return true;
      const { questionId, requiredValue } = q.condition;
      return answers[questionId as keyof SurveyAnswers] === requiredValue;
    });
  }, [answers]);

  const currentQuestion = visibleQuestions[currentStep];
  const totalSteps = visibleQuestions.length;
  const isLast = currentStep === totalSteps - 1;
  const currentAnswer = currentQuestion ? answers[currentQuestion.id] : undefined;

  function answer(value: AnswerValue) {
    if (!currentQuestion) return;

    const newAnswers = { ...answers, [currentQuestion.id]: value };

    // Q1이 A로 변경되면 Q2, Q3 답변 초기화
    if (currentQuestion.id === "Q1" && value === "A") {
      delete newAnswers.Q2;
      delete newAnswers.Q3;
    }
    // Q2가 A로 변경되면 Q3 답변 초기화
    if (currentQuestion.id === "Q2" && value === "A") {
      delete newAnswers.Q3;
    }

    setAnswers(newAnswers);
  }

  function next() {
    if (currentStep < totalSteps - 1) {
      setCurrentStep((s) => s + 1);
    }
  }

  function prev() {
    if (currentStep > 0) {
      setCurrentStep((s) => s - 1);
    }
  }

  function isComplete(): boolean {
    return visibleQuestions.every((q) => answers[q.id] !== undefined);
  }

  return {
    answers,
    currentStep,
    currentQuestion,
    visibleQuestions,
    totalSteps,
    isLast,
    currentAnswer,
    answer,
    next,
    prev,
    isComplete,
  };
}
