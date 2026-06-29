interface ProgressBarProps {
  current: number;
  total: number;
  onBack: () => void;
}

export default function ProgressBar({ current, total, onBack }: ProgressBarProps) {
  const percent = ((current + 1) / total) * 100;

  return (
    <div className="w-full max-w-xl mx-auto mb-8">
      <div className="flex items-center gap-3 mb-3">
        <button
          onClick={onBack}
          disabled={current === 0}
          className="text-sm text-gray-400 hover:text-violet-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
        >
          ← 뒤로
        </button>
        <span className="ml-auto text-sm font-medium text-violet-600">
          {current + 1} / {total}
        </span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-violet-500 to-violet-400 rounded-full transition-all duration-500"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
