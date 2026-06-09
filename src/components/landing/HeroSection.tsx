import { useNavigate } from "react-router-dom";

export default function HeroSection() {
  const navigate = useNavigate();

  return (
    <div className="text-center mb-16">
      <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-violet-100 text-violet-600 text-sm font-medium mb-6">
        ✦ AI 기반 알바 매칭
      </div>

      <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 leading-tight mb-4">
        나에게 맞는 알바,
        <br />
        <span className="text-violet-600">성향</span>으로 찾아요.
      </h1>

      <p className="text-base md:text-lg text-gray-500 mb-10 max-w-sm mx-auto">
        조건 필터 말고, 5가지 질문으로<br />딱 맞는 알바를 추천받아 보세요.
      </p>

      <button
        onClick={() => navigate("/survey")}
        className="px-8 py-4 rounded-2xl bg-violet-600 text-white font-semibold text-base hover:bg-violet-700 shadow-lg shadow-violet-200 transition-all duration-200 hover:shadow-violet-300 hover:-translate-y-0.5"
      >
        지금 시작하기 →
      </button>
    </div>
  );
}
