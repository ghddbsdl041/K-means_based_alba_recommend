import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { fetchRecommendations } from "../lib/api";
import type { Job } from "../types/job";
import type { SurveyAnswers, AnswerValue } from "../types/survey";
import PersonaCard from "../components/result/PersonaCard";
import JobList from "../components/result/JobList";
import GuSelect from "../components/common/GuSelect";
import { getTheme } from "../constants/clusterTheme";

function PersonaSkeleton() {
  return (
    <div className="rounded-2xl border border-white/40 bg-white/60 backdrop-blur-sm p-6 animate-pulse">
      <div className="h-5 bg-gray-200 rounded w-24 mb-5" />
      <div className="w-32 h-32 rounded-full bg-gray-200 mx-auto mb-5" />
      <div className="h-5 bg-gray-200 rounded w-1/2 mx-auto mb-2" />
      <div className="h-3 bg-gray-200 rounded w-2/3 mx-auto mb-6" />
      <div className="space-y-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex gap-3 items-center">
            <div className="w-14 h-3 bg-gray-200 rounded" />
            <div className="flex-1 h-2 bg-gray-200 rounded-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

function JobSkeleton() {
  return (
    <div className="w-full rounded-2xl border border-white/40 bg-white/60 backdrop-blur-sm p-5 animate-pulse">
      <div className="flex gap-4">
        <div className="flex-1 space-y-3">
          <div className="h-3 bg-gray-200 rounded w-1/3" />
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-3 bg-gray-200 rounded w-1/2" />
        </div>
        <div className="h-9 w-24 bg-gray-200 rounded-xl self-center shrink-0" />
      </div>
    </div>
  );
}

export default function ResultPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showGuSelector, setShowGuSelector] = useState(false);

  const guParam = searchParams.get("gu");
  const [preferredGus, setPreferredGus] = useState<string[]>(
    guParam ? guParam.split(",").filter(Boolean) : [],
  );

  const answers: SurveyAnswers = {
    Q1: (searchParams.get("Q1") as AnswerValue) ?? undefined,
    Q2: (searchParams.get("Q2") as AnswerValue) ?? undefined,
    Q3: (searchParams.get("Q3") as AnswerValue) ?? undefined,
    Q4: (searchParams.get("Q4") as AnswerValue) ?? undefined,
    Q5: (searchParams.get("Q5") as AnswerValue) ?? undefined,
  };

  const clusterId = jobs.length > 0 ? jobs[0].cluster_id : null;
  const clusterName = jobs.length > 0 ? jobs[0].cluster_name : "";

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRecommendations(answers);
      setJobs(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!answers.Q1 || !answers.Q4 || !answers.Q5) {
      navigate("/survey");
      return;
    }
    load();
  }, []);

  return (
    <div className="min-h-screen px-4 py-10">
      {/* 지역 재선택 오버레이 */}
      {showGuSelector && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm px-4">
          <div className="w-full max-w-xl rounded-3xl border border-white/40 bg-white/90 backdrop-blur-md shadow-xl p-8">
            <GuSelect
              selected={preferredGus}
              onChange={setPreferredGus}
              onConfirm={(gus) => { setPreferredGus(gus); setShowGuSelector(false); }}
              onSkip={() => { setPreferredGus([]); setShowGuSelector(false); }}
              confirmLabel="적용하기"
            />
          </div>
        </div>
      )}

      {/* 상단 헤더 */}
      <div className="max-w-6xl mx-auto flex items-center justify-between mb-8">
        <button
          onClick={() => navigate("/survey")}
          className="text-sm text-gray-400 hover:text-violet-600 transition-colors"
        >
          ← 다시 하기
        </button>
        <span className={`text-sm font-medium ${clusterId !== null ? getTheme(clusterId).summaryStrong : "text-violet-600"}`}>성향 분석 결과</span>
      </div>

      {/* 에러 */}
      {error && (
        <div className="max-w-6xl mx-auto text-center py-16">
          <p className="text-gray-500 mb-4">{error}</p>
          <button
            onClick={load}
            className="px-6 py-3 rounded-xl bg-violet-600 text-white font-medium hover:bg-violet-700 transition-colors"
          >
            다시 시도하기
          </button>
        </div>
      )}

      {!error && (
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6 items-start">
          {/* 왼쪽: 성향 카드 (sticky) */}
          <div className="lg:sticky lg:top-10">
            {loading ? (
              <PersonaSkeleton />
            ) : clusterId !== null ? (
              <PersonaCard clusterId={clusterId} clusterName={clusterName} totalJobs={jobs.length} />
            ) : null}
          </div>

          {/* 오른쪽: 공고 리스트 */}
          <div>
            {loading ? (
              <div className="flex flex-col gap-4">
                {[...Array(6)].map((_, i) => <JobSkeleton key={i} />)}
              </div>
            ) : (
              <JobList
                jobs={jobs}
                clusterId={clusterId}
                preferredGus={preferredGus}
                onShowAll={() => setPreferredGus([])}
                onChangeGu={() => setShowGuSelector(true)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
