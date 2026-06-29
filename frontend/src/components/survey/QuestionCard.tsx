import type { Question } from "../../types/survey";
import type { AnswerValue } from "../../types/survey";

interface QuestionCardProps {
  question: Question;
  selected: AnswerValue | undefined;
  onSelect: (value: AnswerValue) => void;
}

export default function QuestionCard({ question, selected, onSelect }: QuestionCardProps) {
  return (
    <div className="w-full max-w-xl mx-auto">
      <h2 className="text-2xl md:text-3xl font-semibold text-gray-900 mb-8 leading-snug text-center">
        {question.text}
      </h2>

      <div className="grid grid-cols-2 gap-4">
        {(["A", "B"] as AnswerValue[]).map((value) => {
          const option = value === "A" ? question.optionA : question.optionB;
          const isSelected = selected === value;

          return (
            <button
              key={value}
              onClick={() => onSelect(value)}
              className={[
                "rounded-2xl p-6 text-left cursor-pointer transition-all duration-200 flex flex-col gap-2",
                isSelected
                  ? "border-2 border-violet-500 bg-violet-50/80 backdrop-blur-sm shadow-md shadow-violet-100"
                  : "border border-gray-200 bg-white/60 backdrop-blur-sm hover:border-violet-400 hover:shadow-md",
              ].join(" ")}
            >
              <span className={`text-xs font-semibold tracking-widest ${isSelected ? "text-violet-500" : "text-gray-400"}`}>
                {value}
              </span>
              <span className={`text-lg font-semibold leading-tight ${isSelected ? "text-violet-700" : "text-gray-800"}`}>
                {option.label}
              </span>
              <span className={`text-sm ${isSelected ? "text-violet-500" : "text-gray-500"}`}>
                {option.description}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
