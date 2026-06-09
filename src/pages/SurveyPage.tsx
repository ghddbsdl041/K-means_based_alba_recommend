import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSurvey } from "../hooks/useSurvey";
import ProgressBar from "../components/survey/ProgressBar";
import QuestionCard from "../components/survey/QuestionCard";
import GuSelect from "../components/common/GuSelect";
import type { AnswerValue } from "../types/survey";

type Phase = "survey" | "gu";

export default function SurveyPage() {
  const navigate = useNavigate();
  const [phase, setPhase] = useState<Phase>("survey");
  const [preferredGus, setPreferredGus] = useState<string[]>([]);

  const {
    currentStep,
    currentQuestion,
    visibleQuestions,
    totalSteps,
    isLast,
    currentAnswer,
    answers,
    answer,
    next,
    prev,
    isComplete,
  } = useSurvey();

  function goToResult(gus: string[]) {
    const params = new URLSearchParams();
    Object.entries(answers).forEach(([k, v]) => { if (v) params.set(k, v); });
    if (gus.length > 0) params.set("gu", gus.join(","));
    navigate(`/result?${params.toString()}`);
  }

  function handleNext() {
    if (isLast && isComplete()) {
      setPhase("gu");
    } else {
      next();
    }
  }

  if (phase === "gu") {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
        {/* 진행 표시 — Q6 위치 */}
        <div className="w-full max-w-xl mx-auto mb-8">
          <div className="flex items-center gap-3 mb-3">
            <button
              onClick={() => setPhase("survey")}
              className="text-sm text-gray-400 hover:text-violet-600 transition-colors"
            >
              ← 뒤로
            </button>
            <span className="ml-auto text-sm font-medium text-violet-600">
              마지막 단계
            </span>
          </div>
          <div className="h-2 bg-violet-400 rounded-full" />
        </div>

        <GuSelect
          selected={preferredGus}
          onChange={setPreferredGus}
          onConfirm={(gus) => goToResult(gus)}
          onSkip={() => goToResult([])}
        />
      </div>
    );
  }

  if (!currentQuestion) return null;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <ProgressBar current={currentStep} total={totalSteps} onBack={prev} />

      <QuestionCard
        question={currentQuestion}
        selected={currentAnswer}
        onSelect={(v: AnswerValue) => answer(v)}
      />

      <div className="mt-10 w-full max-w-xl">
        <button
          onClick={handleNext}
          disabled={!currentAnswer}
          className={[
            "w-full py-4 rounded-2xl text-white font-semibold text-base transition-all duration-200",
            currentAnswer
              ? "bg-violet-600 hover:bg-violet-700 shadow-md shadow-violet-200"
              : "bg-gray-200 cursor-not-allowed text-gray-400",
          ].join(" ")}
        >
          {isLast ? "다음 →" : "다음 →"}
        </button>
      </div>

      <p className="mt-6 text-xs text-gray-400">
        Q{visibleQuestions[currentStep]?.id?.replace("Q", "")} — 총 {totalSteps}문항
      </p>
    </div>
  );
}
