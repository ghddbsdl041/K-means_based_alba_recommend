const FEATURES = [
  {
    icon: "✦",
    title: "5문항 성향 설문",
    desc: "간단한 선택으로 내 근무 스타일 파악",
  },
  {
    icon: "✦",
    title: "AI 기반 매칭",
    desc: "K-Means 클러스터링으로 최적 공고 추천",
  },
  {
    icon: "✦",
    title: "실시간 공고 연결",
    desc: "알바몬·알바천국 최신 공고 바로 연결",
  },
];

export default function FeatureStrip() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl mx-auto">
      {FEATURES.map((f) => (
        <div
          key={f.title}
          className="rounded-2xl border border-white/40 bg-white/60 backdrop-blur-sm p-6 text-center"
        >
          <span className="text-violet-500 text-lg font-bold mb-3 block">{f.icon}</span>
          <h3 className="text-sm font-semibold text-gray-800 mb-1">{f.title}</h3>
          <p className="text-xs text-gray-500 leading-relaxed">{f.desc}</p>
        </div>
      ))}
    </div>
  );
}
