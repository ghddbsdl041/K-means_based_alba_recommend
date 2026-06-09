interface TraitBarProps {
  label: string;
  value: number;
}

export default function TraitBar({ label, value }: TraitBarProps) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-600 w-14 shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-violet-500 to-violet-300 rounded-full transition-all duration-700"
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs text-gray-500 w-9 text-right shrink-0">{value}%</span>
    </div>
  );
}
