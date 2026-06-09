import { CLUSTER_TRAITS } from "../../constants/clusterTraits";
import TraitBar from "./TraitBar";

interface PersonaCardProps {
  clusterId: number;
  clusterName: string;
  totalJobs: number;
}

const CLUSTER_COUNT = 4;

export default function PersonaCard({ clusterId, clusterName, totalJobs }: PersonaCardProps) {
  const traits = CLUSTER_TRAITS[clusterId];

  return (
    <div className="rounded-2xl border border-white/40 bg-white/60 backdrop-blur-sm shadow-sm p-6">
      <div className="flex items-center justify-between mb-5">
        <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-violet-100 text-violet-600">
          ✦ AI 매칭 결과
        </span>
        <span className="text-xs text-gray-400">
          군집 {clusterId + 1} / {CLUSTER_COUNT}
        </span>
      </div>

      <p className="text-center text-sm text-gray-400 mb-4">당신의 알바 성향은</p>

      <div className="w-32 h-32 rounded-full bg-gray-100 border-2 border-dashed border-gray-300 flex items-center justify-center text-gray-400 text-xs mx-auto mb-5">
        캐릭터 준비 중
      </div>

      <h2 className="text-xl font-bold text-violet-700 text-center mb-1">{clusterName}</h2>
      {traits && (
        <p className="text-xs text-gray-500 text-center mb-6 leading-relaxed">{traits.description}</p>
      )}

      {traits && (
        <div className="flex flex-col gap-3 mb-6">
          {traits.traits.map((t) => (
            <TraitBar key={t.label} label={t.label} value={t.value} />
          ))}
        </div>
      )}

      <div className="rounded-xl bg-violet-50 border border-violet-100 px-4 py-3 text-center">
        <p className="text-xs text-violet-600 leading-relaxed">
          이 유형에 속한 공고 중<br />
          <span className="font-semibold text-violet-700">{totalJobs}개</span>를 추천했어요
        </p>
      </div>
    </div>
  );
}
