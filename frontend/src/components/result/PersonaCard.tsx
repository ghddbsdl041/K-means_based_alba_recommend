import { CLUSTER_TRAITS } from "../../constants/clusterTraits";
import { getTheme } from "../../constants/clusterTheme";
import TraitBar from "./TraitBar";
import imgSamuCS from "../../assets/안정적사무_CS형.png";
import imgShortTerm from "../../assets/고수익_단기_노무형.png";
import imgPartTime from "../../assets/일반_파트타임_서비스형.png";
import imgFnB from "../../assets/정규_식음료_매장관리형.png";

const CLUSTER_IMAGES: Record<number, string> = {
  0: imgSamuCS,
  1: imgShortTerm,
  2: imgPartTime,
  3: imgFnB,
};

const CLUSTER_COUNT = 4;

interface PersonaCardProps {
  clusterId: number;
  clusterName: string;
  totalJobs: number;
}

export default function PersonaCard({ clusterId, clusterName, totalJobs }: PersonaCardProps) {
  const traits = CLUSTER_TRAITS[clusterId];
  const theme = getTheme(clusterId);

  return (
    <div className="rounded-2xl border border-white/40 bg-white/60 backdrop-blur-sm shadow-sm p-6">
      {/* 배지 */}
      <div className="flex items-center justify-between mb-5">
        <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full ${theme.badge}`}>
          ✦ AI 매칭 결과
        </span>
        <span className="text-xs text-gray-400">
          군집 {clusterId + 1} / {CLUSTER_COUNT}
        </span>
      </div>

      <p className="text-center text-sm text-gray-400 mb-4">당신의 알바 성향은</p>

      {/* 캐릭터 이미지 */}
      <div className="w-36 h-36 rounded-full overflow-hidden mx-auto mb-5 bg-gray-100">
        <img
          src={CLUSTER_IMAGES[clusterId]}
          alt={clusterName}
          className="w-full h-full object-cover"
        />
      </div>

      {/* 유형명 */}
      <h2 className={`text-xl font-bold text-center mb-1 ${theme.name}`}>{clusterName}</h2>
      {traits && (
        <p className={`text-xs text-center mb-6 leading-relaxed ${theme.description}`}>
          {traits.description}
        </p>
      )}

      {/* 성향 지표 바 */}
      {traits && (
        <div className="flex flex-col gap-3 mb-6">
          {traits.traits.map((t) => (
            <TraitBar
              key={t.label}
              label={t.label}
              value={t.value}
              colorFrom={theme.barFrom}
              colorTo={theme.barTo}
            />
          ))}
        </div>
      )}

      {/* 매칭 요약 */}
      <div className={`rounded-xl border px-4 py-3 text-center ${theme.summaryBox}`}>
        <p className={`text-xs leading-relaxed ${theme.summaryText}`}>
          이 유형에 속한 공고 중<br />
          <span className={`font-semibold ${theme.summaryStrong}`}>{totalJobs}개</span>를 추천했어요
        </p>
      </div>
    </div>
  );
}
