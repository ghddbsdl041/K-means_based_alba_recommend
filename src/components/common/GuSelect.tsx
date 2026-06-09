const SEOUL_GU = [
  "강남구", "강동구", "강북구", "강서구", "관악구",
  "광진구", "구로구", "금천구", "노원구", "도봉구",
  "동대문구", "동작구", "마포구", "서대문구", "서초구",
  "성동구", "성북구", "송파구", "양천구", "영등포구",
  "용산구", "은평구", "종로구", "중구",  "중랑구",
];

interface GuSelectProps {
  selected: string[];
  onChange: (gus: string[]) => void;
  onConfirm: (gus: string[]) => void;
  onSkip: () => void;
  confirmLabel?: string;
}

export default function GuSelect({
  selected,
  onChange,
  onConfirm,
  onSkip,
  confirmLabel = "결과 보기 →",
}: GuSelectProps) {
  function toggle(gu: string) {
    onChange(
      selected.includes(gu) ? selected.filter((g) => g !== gu) : [...selected, gu],
    );
  }

  return (
    <div className="w-full max-w-xl mx-auto">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">
          어느 구에서 일하고 싶으세요?
        </h2>
      </div>
      <p className="text-sm text-gray-400 mb-6">
        복수 선택 가능 · 건너뛰면 전체 지역 공고를 보여드려요
      </p>

      <div className="grid grid-cols-4 sm:grid-cols-5 gap-2 mb-8">
        {SEOUL_GU.map((gu) => {
          const active = selected.includes(gu);
          return (
            <button
              key={gu}
              onClick={() => toggle(gu)}
              className={[
                "py-2 px-1 rounded-xl text-xs font-medium transition-all duration-150 border",
                active
                  ? "bg-violet-600 border-violet-600 text-white shadow-sm shadow-violet-200"
                  : "bg-white/60 border-gray-200 text-gray-600 hover:border-violet-400 hover:text-violet-600",
              ].join(" ")}
            >
              {gu}
            </button>
          );
        })}
      </div>

      <div className="flex flex-col gap-3">
        <button
          onClick={() => onConfirm(selected)}
          disabled={selected.length === 0}
          className={[
            "w-full py-4 rounded-2xl font-semibold text-base transition-all duration-200",
            selected.length > 0
              ? "bg-violet-600 text-white hover:bg-violet-700 shadow-md shadow-violet-200"
              : "bg-gray-200 text-gray-400 cursor-not-allowed",
          ].join(" ")}
        >
          {selected.length > 0
            ? `${selected.length}개 지역 선택 · ${confirmLabel}`
            : confirmLabel}
        </button>
        <button
          onClick={onSkip}
          className="w-full py-3 rounded-2xl text-sm text-gray-400 hover:text-violet-600 transition-colors"
        >
          건너뛰기 (전체 지역 보기)
        </button>
      </div>
    </div>
  );
}
