import { useState, useEffect, useLayoutEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

import imgSamuCS from "../../assets/안정적사무_CS형.png";
import imgShortTerm from "../../assets/고수익_단기_노무형.png";
import imgPartTime from "../../assets/일반_파트타임_서비스형.png";
import imgFnB from "../../assets/정규_식음료_매장관리형.png";

const CHARACTER_CARDS = [
  { id: 0, label: "안정적 사무/CS형", image: imgSamuCS },
  { id: 1, label: "고수익 단기/노무형", image: imgShortTerm },
  { id: 2, label: "일반 파트타임 서비스형", image: imgPartTime },
  { id: 3, label: "정규 식음료/매장관리형", image: imgFnB },
];

const GAP = 16;
const CARD_RATIO = 0.72;

function CardSlider() {
  const [current, setCurrent] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const [cardWidth, setCardWidth] = useState(0);

  useLayoutEffect(() => {
    function measure() {
      if (containerRef.current) {
        setCardWidth(containerRef.current.offsetWidth * CARD_RATIO);
      }
    }
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent((c) => (c + 1) % CHARACTER_CARDS.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  const translateX = -current * (cardWidth + GAP);

  return (
    <div className="w-full select-none">
      <div ref={containerRef} className="overflow-hidden w-full">
        <AnimatePresence initial={false}>
          <motion.div
            className="flex"
            style={{ gap: GAP }}
            animate={{ x: translateX }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
          >
            {CHARACTER_CARDS.map((card) => (
              <div
                key={card.id}
                className="shrink-0 rounded-[20px] bg-white overflow-hidden"
                style={{
                  width: cardWidth > 0 ? cardWidth : `${CARD_RATIO * 100}%`,
                  boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
                }}
              >
                <div className="aspect-square w-full overflow-hidden bg-gray-50">
                  <img
                    src={card.image}
                    alt={card.label}
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      const img = e.target as HTMLImageElement;
                      img.style.display = "none";
                      if (img.parentElement) {
                        img.parentElement.classList.add("bg-gray-100");
                      }
                    }}
                  />
                </div>
                <p className="text-center text-[13px] text-[#374151] px-3 py-3 font-medium">
                  {card.label}
                </p>
              </div>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="flex justify-center gap-2 mt-5">
        {CHARACTER_CARDS.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrent(i)}
            aria-label={`슬라이드 ${i + 1}`}
            className={[
              "h-2 rounded-full transition-all duration-300",
              i === current ? "bg-[#2563EB] w-5" : "bg-[#D1D5DB] w-2",
            ].join(" ")}
          />
        ))}
      </div>
    </div>
  );
}

export default function HeroSection() {
  const navigate = useNavigate();

  return (
    <section className="w-full">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-10 md:gap-16">

        {/* Left: 텍스트 + 버튼 */}
        <div className="flex-1 min-w-0">
          <span
            className="inline-block px-3 py-1 rounded-full text-[12px] font-medium mb-5"
            style={{ background: "#EDE9FE", color: "#6D28D9" }}
          >
            Real-time AI Crawling Engine
          </span>

          <h1
            className="font-extrabold text-gray-900"
            style={{ fontSize: 40, lineHeight: 1.3 }}
          >
            실시간 AI 크롤링으로 찾는 나만의{" "}
            <span style={{ color: "#2563EB" }}>딱 맞는 알바</span>
          </h1>

          <p
            className="text-[#6B7280] leading-relaxed"
            style={{ fontSize: 15, marginTop: 16 }}
          >
            수만 개의 알바 사이트를 실시간으로 분석하여,
            <br className="hidden sm:block" />
            당신의 성향과 능력에 맞는 최적의 일자리를 매칭해드립니다.
          </p>

          <div className="flex flex-wrap gap-3" style={{ marginTop: 32 }}>
            <button
              onClick={() => navigate("/survey")}
              className="rounded-lg text-white font-semibold text-[14px] transition-colors hover:bg-blue-700"
              style={{
                background: "#2563EB",
                padding: "12px 24px",
              }}
            >
              내 유형 진단하고 매칭 시작하기
            </button>
            <button
              onClick={() =>
                document
                  .getElementById("features")
                  ?.scrollIntoView({ behavior: "smooth" })
              }
              className="rounded-lg font-semibold text-[14px] transition-colors hover:bg-blue-50"
              style={{
                background: "transparent",
                border: "1.5px solid #2563EB",
                color: "#2563EB",
                padding: "12px 24px",
              }}
            >
              서비스 소개 보기
            </button>
          </div>
        </div>

        {/* Right: 캐릭터 카드 슬라이더 */}
        <div className="w-full md:w-1/2 md:max-w-[420px] shrink-0">
          <CardSlider />
        </div>
      </div>
    </section>
  );
}
