const FEATURES = [
  {
    step: "01",
    title: "5문항 성향 설문",
    desc: "간단한 선택으로 내 근무 스타일 파악",
  },
  {
    step: "02",
    title: "AI 기반 매칭",
    desc: "K-Means 클러스터링으로 최적 공고 추천",
  },
  {
    step: "03",
    title: "실시간 공고 연결",
    desc: "알바몬·알바천국 최신 공고 바로 연결",
  },
];

export default function FeatureStrip() {
  return (
    <div className="w-full max-w-6xl mx-auto">
      <h2 className="text-center text-[22px] font-bold text-gray-400 mb-8">
        어떻게 작동하나요?
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {FEATURES.map((f) => (
          <div
            key={f.step}
            className="rounded-2xl border border-white/50 bg-white/50 backdrop-blur-sm p-6 shadow-sm hover:shadow-md hover:bg-white/65 transition-all duration-200"
          >
            <div className="text-xs font-bold text-[#6D28D9] mb-3 tracking-widest">
              STEP {f.step}
            </div>
            <h3 className="text-sm font-semibold text-gray-800 mb-1.5">
              {f.title}
            </h3>
            <p className="text-xs text-gray-500 leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
