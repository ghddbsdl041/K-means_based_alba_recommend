interface TraitBarProps {
  label: string;
  value: number;
  colorFrom?: string;
  colorTo?: string;
}

export default function TraitBar({ label, value, colorFrom = "#7C3AED", colorTo = "#A78BFA" }: TraitBarProps) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-600 w-14 shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${value}%`,
            background: `linear-gradient(to right, ${colorFrom}, ${colorTo})`,
          }}
        />
      </div>
      <span className="text-xs text-gray-400 w-9 text-right shrink-0">{value}%</span>
    </div>
  );
}
